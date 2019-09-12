from radical.entk import Pipeline, Stage, Task, AppManager 

import argparse
import os
import re
import pprint
import glob
import yaml
from pprint import pprint

def to_file(list_of_cmd, fname):
    with open(fname, "w") as f:
        for l in list_of_cmd:
            f.write(l + "\n")
        f.close()
        return fname


def set_vmd_run(task, list_of_cmd, name=None):
    fname = to_file(list_of_cmd, name or "input.tcl")
    task.executable = [ 'vmd' ]
    task.arguments = [ '-eofexit', '<', fname ]


def get_pipeline(workflow_cfg, resource):

    # Get workflow parameters from the workflow cfg file for the specific
    # resource

    ## Extract resource-independent global parameters
    total_iters = workflow_cfg['global']['total_iters']
    ensemble_size = workflow_cfg['global']['ensemble_size']
    sim_duration = workflow_cfg['global']['sim_duration']

    ## Simulation related parameters
    sim_pre_exec = workflow_cfg[resource]['simulation']['pre_exec']
    sim_cpus = workflow_cfg[resource]['simulation']['cpus']

    ## Analysis related parameters
    ana_pre_exec = workflow_cfg[resource]['analysis']['pre_exec']
    ana_cpus = workflow_cfg[resource]['analysis']['cpus']


    # Create one Pipeline for the entire workflow. The Pipeline contains 1 
    # Simulation stage and 1 Analysis stage per iteration.
    # Please refer to the API reference for more details about Pipeline, Stage,
    # Task. Link: https://radicalentk.readthedocs.io/en/latest/api/app_create.html
    p = Pipeline()
    p.name = 'simple_mdff'

    task_names = []

    first_stage = Stage()
    # We use names of pipelines, stages, tasks to refer to data of a
    # particular task
    first_stage.name = 'Generating a simulated density map'


    # Create tasks and add them to stage
    task = Task()
    task.name = 'Starting to load the target PDB'
    task.cpu_reqs['threads_per_process'] = sim_cpus
    task.pre_exec = [ "/usr/bin/wget https://www.ks.uiuc.edu/Training/Tutorials/science/mdff/mdff-tutorial-files/2-mdff-vacuo/4ake-target.pdb" ]
    task_tcl_cmds = [ 'mol new 4ake-target.pdb' ]
    task_tcl_cmds += [ 'package require autopsf' ]
    task_tcl_cmds += [ 'autopsf 4ake-target.pdb' ]
    task_tcl_cmds += [ 'set sel [atomselect top all]' ]
    task_tcl_cmds += [ 'package require mdff']
    task_tcl_cmds += [ 'mdff sim $sel -res 5 -o 4ake-target_autopsf.situs' ]
    task_tcl_cmds += [ 'mol new 4ake-target_autopsf.situs' ]

    set_vmd_run(task, task_tcl_cmds, "first_stage.tcl")
    first_stage.add_tasks(task)
    # Add sim_stage to Pipeline
    p.add_stages(first_stage)


    second_stage = Stage()
    second_stage.name = 'Converting the density map to an MDFF potential'

    task = Task()
    task.name = 'generate dx file'
    task.cpu_reqs['threads_per_process'] = sim_cpus
    task_tcl_cmds = [ 'package require mdff' ]
    task_tcl_cmds += [ 'mdff griddx -i 4ake-target_autopsf.situs -o 4ake-target_autopsf-grid.dx' ]

    set_vmd_run(task, task_tcl_cmds, "second_stage.tcl")
    second_stage.add_tasks(task)
    p.add_stages(second_stage)


    third_stage = Stage()
    third_stage.name = 'Preparing the initial structure'

    task = Task()
    task.name = 'Starting to load the initial structure'
    task.cpu_reqs['threads_per_process'] = sim_cpus
    task.pre_exec = [ '/usr/bin/wget https://www.ks.uiuc.edu/Training/Tutorials/science/mdff/mdff-tutorial-files/2-mdff-vacuo/1ake-initial.pdb' ]
    task_tcl_cmds = [ 'mol new 1ake-initial.pdb' ]
    task_tcl_cmds += [ 'package require autopsf' ]
    task_tcl_cmds += [ 'autopsf 1ake-initial.pdb' ]
    task_tcl_cmds += [ 'package require mdff' ]
    task_tcl_cmds += [ 'mdff gridpdb -psf 1ake-initial_autopsf.psf -pdb 1ake-initial_autopsf.pdb -o 1ake-initial_autopsf-grid.pdb' ]

    set_vmd_run(task, task_tcl_cmds, "third_stage.tcl")
    third_stage.add_tasks(task)
    p.add_stages(third_stage)


    fourth_stage = Stage()
    fourth_stage.name = 'Defining secondary structure restraints'

    task = Task()
    task.cpu_reqs['threads_per_process'] = sim_cpus
    task_tcl_cmds = [ 'package require ssrestraints' ]
    task_tcl_cmds += [ 'ssrestraints -psf 1ake-initial_autopsf.psf -pdb 1ake-initial_autopsf.pdb -o 1ake-extrabonds.txt -hbonds' ]
    task_tcl_cmds += [ 
            'mol new 1ake-initial_autopsf.psf',
            'mol addfile 1ake-initial_autopsf.pdb',
            'cispeptide restrain -o 1ake-extrabonds-cispeptide.txt',
            'chirality restrain -o 1ake-extrabonds-chirality.txt',
            ]

    set_vmd_run(task, task_tcl_cmds, "fourth_stage.tcl")
    fourth_stage.add_tasks(task)
    p.add_stages(fourth_stage)

  
    fifth_stage = Stage()
    fifth_stage.name = 'Rigid-body docking the structure into the density map'
    task = Task()
    task.cpu_reqs['threads_per_process'] = sim_cpus
    # Expect to run Situs package
    # colores 4ake-target_autopsf.situs 1ake-initial_autopsf.pdb -res 5 -nopowell
    # However, this example uses prepared pdb files by wget
    task.pre_exec = [ '/usr/bin/wget https://www.ks.uiuc.edu/Training/Tutorials/science/mdff/mdff-tutorial-files/2-mdff-vacuo/1ake-colores.pdb' ]
    task.executable = [ 'mv' ]
    task.arguments  = [ '1ake-colores.pdb', '1ake-initial_autopsf-docked.pdb' ]
 
    fifth_stage.add_tasks(task)
    p.add_stages(fifth_stage)

  
    sixth_stage = Stage()
    sixth_stage.name = 'Running the MDFF simulation with NAMD'
    task = Task()
    task.cpu_reqs['threads_per_process'] = sim_cpus
    task_tcl_cmds = [ 'package require mdff' ]
    task_tcl_cmds += [ 'mdff setup -o adk -psf 1ake-initial_autopsf.psf -pdb 1ake-initial_autopsf-docked.pdb -griddx 4ake-target_autopsf-grid.dx -gridpdb 1ake-initial_autopsf-grid.pdb -extrab {1ake-extrabonds.txt 1ake-extrabonds-cispeptide.txt 1ake-extrabonds-chirality.txt} -gscale 0.3 -numsteps 50000' ]
    task_tcl_cmds += [ 'mdff setup -o adk -psf 1ake-initial_autopsf.psf -pdb 1ake-initial_autopsf-docked.pdb -griddx 4ake-target_autopsf-grid.dx -gridpdb 1ake-initial_autopsf-grid.pdb -extrab {1ake-extrabonds.txt 1ake-extrabonds-cispeptide.txt 1ake-extrabonds-chirality.txt} -gscale 10 -minsteps 2000 -numsteps 0 -step 2' ]

    set_vmd_run(task, task_tcl_cmds, "sixth_stage.tcl")
    sixth_stage.add_tasks(task)
    p.add_stages(sixth_stage)


    seventh_stage = Stage()
    seventh_stage.name = "NAMD simulation"
    task = Task()
    task.cpu_reqs['threads_per_process'] = sim_cpus
    task.executable = [ 'namd2' ]
    task.arguments = ['+ppn', sim_cpus, 'adk-step1.namd']
    seventh_stage.add_tasks(task)
    task = Task()
    task.executable = [ 'namd2' ]
    task.arguments = ['+ppn', sim_cpus, 'adk-step2.namd']
    seventh_stage.add_tasks(task)
    p.add_stage(seventh_stage)

    # Visualizing the MDFF trajectory
    #
    # mol new 4ake-target_autopsf.psf    
    # mol addfile 4ake-target_autopsf.pdb  
    # mol new 1ake-initial_autopsf.psf   
    # mol addfile 1ake-initial_autopsf-docked.pdb  
    # mol addfile adk-step1.dcd  
    # mol addfile adk-step2.dcd


    eighth_stage = Stage()
    eighth_stage.name = 'Calculating the root mean square deviation'
    task = Task()
    task.cpu_reqs['threads_per_process'] = sim_cpus
    task_tcl_cmds = [ 
            'package require mdff',
            'mdff check -rmsd -refpdb 4ake-target_autopsf.pdb',
            'set selbbref [atomselect 0 "backbone"]',
            'set selbb [atomselect 1 "backbone"]',
            '$selbb frame 0',
            'measure rmsd $selbb $selbbref',
            '$selbb frame last',
            'measure rmsd $selbb $selbbref'
            ]

    set_vmd_run(task, task_tcl_cmds, "eighth_stage.tcl")
    eighth_stage.add_tasks(task)
    p.add_stages(eighth_stage)


    ninth_stage = Stage()
    ninth_stage.name = 'Calculating the cross-correlation coefficient'
    task = Task()
    task.cpu_reqs['threads_per_process'] = sim_cpus
    task_tcl_cmds = [ 
            'package require mdff',
            'mdff check -ccc -map 4ake-target_autopsf.situs -res 5',
            'set selallref [atomselect 0 "all"]',
            'set selall [atomselect 1 "all"]',
            '$selall frame 0',
            'mdff ccc $selall -i 4ake-target_autopsf.situs -res 5',
            '$selall frame last',
            'mdff ccc $selall -i 4ake-target_autopsf.situs -res 5']

    set_vmd_run(task, task_tcl_cmds, "ninth_stage.tcl")
    ninth_stage.add_tasks(task)
    p.add_stages(ninth_stage)

    return p

if os.environ.get('RADICAL_ENTK_VERBOSE') == None:
    os.environ['RADICAL_ENTK_REPORT'] = 'True'


if __name__ == '__main__':

    '''
    This script is executed as:
    python example.py --resource <resource name>
    '''

    # Parse arguments from the command line
    parser = argparse.ArgumentParser(description='Process some arguments to get resource and workflow cfgs')
    parser.add_argument('--resource', help='path to workflow cfg file', required=False, default='xsede_supermic')
    args = parser.parse_args()
    resource = args.resource


    # Load resource cfg 
    with open('./resource_cfg.yml','r') as fp:
        resource_cfg = yaml.load(fp)

    # Load workflow cfg
    with open('./simple_mdff_cfg.yml','r') as fp:
        workflow_cfg = yaml.load(fp)


    # Create Pipeline
    p = get_pipeline(workflow_cfg, resource)


    # for stage in p.stages:
    #     for task in stage.tasks:
    #         pprint (task.to_dict())

    # Create Application Manager
    appman = AppManager(hostname=resource_cfg['rabbitmq']['hostname'], 
                        port=resource_cfg['rabbitmq']['port'])

    # Create a dictionary describe five mandatory keys:
    # resource, walltime, cores, queue and access_schema
    res_dict = {

        'resource': resource_cfg[resource]['label'],
        'walltime': resource_cfg[resource]['walltime'],
        'cpus': resource_cfg[resource]['cpus'],
        'queue': resource_cfg[resource]['queue'],
        'access_schema': resource_cfg[resource]['access_schema']
        }

    # Assign resource manager to the Application Manager
    appman.resource_desc = res_dict

    # Data shared between multiple tasks can be transferred while the 
    # job is waiting on queue
    appman.shared_data = []

    # Assign the workflow as a set or list of Pipelines to the Application Manager
    appman.workflow = [p]

    # Run the Application Manager
    appman.run()
