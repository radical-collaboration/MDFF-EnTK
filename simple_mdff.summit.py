from radical.entk import Pipeline, Stage, Task, AppManager 

import argparse
import os
import re
import glob
import yaml
from pprint import pprint

summit_hw_thread_cnt = 4
vmd_path ='/gpfs/alpine/world-shared/bip115/VMD_binaries/VMD-1.9.3-xlc-build-2019-Dec-12/bin/vmd'
namd_path = '/gpfs/alpine/world-shared/bip115/NAMD_binaries/summit/NAMD_build.latest/Linux-POWER-MPI-smp-Summit/namd2'

def to_file(list_of_cmd, fname):
    with open(fname, "w") as f:
        for l in list_of_cmd:
            f.write(l + "\n")
        f.close()
        return fname


def set_vmd_run(task, list_of_cmd, name=None):
    fname = to_file(list_of_cmd, name or "input.tcl")
    tcl_script_in_string = "\n".join(list_of_cmd) + "\nexit"
    task.pre_exec += [ "echo '{}' > {}".format(tcl_script_in_string, name or "input.tcl")]
    task.executable = [ vmd_path + ' -dispdev text -e ' +  fname ] # to source a tcl script using command line version of vmd 
    #task.arguments = [ '-eofexit', '<', fname ]

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
    p.name = 'simple-mdff'

    task_names = []


    task1_output = ['4ake-target_autopsf.situs']
    task2_output = ['4ake-target_autopsf-grid.dx']
    task3_output = ['1ake-docked-noh_autopsf-grid.pdb']
    task4_output = ['1ake-extrabonds.txt']
    task5_output = ['1ake-extrabonds-cispeptide.txt', '1ake-extrabonds-chirality.txt']


    first_stage = Stage()
    # We use names of pipelines, stages, tasks to refer to data of a
    # particular task
    first_stage.name = 'Generating a simulated density map'


    # Create tasks and add them to stage
    task1 = Task()
    task1.name = 'Starting to load the target PDB'
    task1.cpu_reqs['threads_per_process'] = summit_hw_thread_cnt
    task1.cpu_reqs['processes'] = ana_cpus // summit_hw_thread_cnt
    task1_tcl_cmds = [ 'mol new 4ake-target.pdb' ]
    task1_tcl_cmds += [ 'package require autopsf' ]
    task1_tcl_cmds += [ 'autopsf 4ake-target.pdb' ]
    task1_tcl_cmds += [ 'set sel [atomselect top all]' ]
    task1_tcl_cmds += [ 'package require mdff']
    task1_tcl_cmds += [ 'mdff sim $sel -res 5 -o {}'.format(task1_output[0]) ]
    task1_tcl_cmds += [ 'mol new {}'.format(task1_output[0]) ]

    set_vmd_run(task1, task1_tcl_cmds, "first_stage.tcl")
    #task.copy_input_data = ["first_stage.tcl"]
    first_stage.add_tasks(task1)
    # Add sim_stage to Pipeline
    p.add_stages(first_stage)


    second_stage = Stage()
    second_stage.name = 'Converting the density map to an MDFF potential'

    task2 = Task()
    task2.name = 'generate dx file'
    task2.cpu_reqs['threads_per_process'] = summit_hw_thread_cnt
    task2.cpu_reqs['processes'] = ana_cpus // summit_hw_thread_cnt
    task2_tcl_cmds = [ 'package require mdff' ]
    task2_tcl_cmds += [ 'mdff griddx -i {} -o {}'.format(task1_output[0], task2_output[0]) ]
    task2.copy_input_data = ['$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, first_stage.name, task1.name, task1_output[0])]


    set_vmd_run(task2, task2_tcl_cmds, "second_stage.tcl")
    second_stage.add_tasks(task2)
    p.add_stages(second_stage)


    third_stage = Stage()
    third_stage.name = 'Preparing the initial structure'

    task3 = Task()
    task3.name = 'Starting to load the initial structure'
    task3.cpu_reqs['threads_per_process'] = summit_hw_thread_cnt
    task3.cpu_reqs['processes'] = ana_cpus // summit_hw_thread_cnt
    task3_tcl_cmds = [ 'mol new 1ake-docked-noh.pdb' ]
    task3_tcl_cmds += [ 'package require autopsf' ]
    task3_tcl_cmds += [ 'autopsf 1ake-docked-noh.pdb' ]
    task3_tcl_cmds += [ 'package require mdff' ]
    task3_tcl_cmds += [ 'mdff gridpdb -psf 1ake-docked-noh_autopsf.psf -pdb 1ake-docked-noh_autopsf.pdb -o {}'.format(task3_output[0]) ]

    set_vmd_run(task3, task3_tcl_cmds, "third_stage.tcl")
    third_stage.add_tasks(task3)
    p.add_stages(third_stage)


    fourth_stage = Stage()
    fourth_stage.name = 'Defining secondary structure restraints'

    task4 = Task()
    task4.cpu_reqs['threads_per_process'] = summit_hw_thread_cnt
    task4.cpu_reqs['processes'] = ana_cpus // summit_hw_thread_cnt
    task4_tcl_cmds = [ 'package require ssrestraints',
            'mol new 1ake-docked-noh_autopsf.psf',
            'mol addfile 1ake-docked-noh_autopsf.pdb',
            'ssrestraints -psf 1ake-docked-noh_autopsf.psf -pdb 1ake-docked-noh_autopsf.pdb -o {} -hbonds'.format(task4_output[0]) ]

    task4.copy_input_data = ['$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name, task3.name, '1ake-docked-noh_autopsf.pdb'),
            '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name, task3.name, '1ake-docked-noh_autopsf.psf')]

    set_vmd_run(task4, task4_tcl_cmds, "fourth_stage.tcl")
    fourth_stage.add_tasks(task4)
    p.add_stages(fourth_stage)

  
    fifth_stage = Stage()
    fifth_stage.name = 'cispeptide and chirality restraints'

    task5 = Task()
    task5.cpu_reqs['processes'] = ana_cpus // summit_hw_thread_cnt
    task5.cpu_reqs['threads_per_process'] = summit_hw_thread_cnt
    task5_tcl_cmds = [ 'mol new 1ake-docked-noh_autopsf.psf',
            'mol addfile 1ake-docked-noh_autopsf.pdb',
            'package require cispeptide',
            'package require chirality',
            'cispeptide restrain -o {}'.format(task5_output[0]),
            'chirality restrain -o {}'.format(task5_output[1])]

    task5.copy_input_data = ['$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name, task3.name, '1ake-docked-noh_autopsf.pdb'),
            '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name, task3.name, '1ake-docked-noh_autopsf.psf')]

    set_vmd_run(task5, task5_tcl_cmds, 'fifth_stage.tcl')
    fifth_stage.add_tasks(task5)
    p.add_stages(fifth_stage)

  
    sixth_stage = Stage()
    sixth_stage.name = 'Running the MDFF simulation with NAMD'
    task6 = Task()
    task6.cpu_reqs['threads_per_process'] = summit_hw_thread_cnt
    task6.cpu_reqs['processes'] = ana_cpus // summit_hw_thread_cnt
    task6_tcl_cmds = [ 'package require mdff' ]
    task6_tcl_cmds += [ 'mdff setup -o adk -psf 1ake-docked-noh_autopsf.psf ' \
            + '-pdb 1ake-docked-noh_autopsf-docked.pdb ' \
            + '-griddx 4ake-target_autopsf-grid.dx ' \
            + '-gridpdb 1ake-docked-noh_autopsf-grid.pdb ' \
            + '-extrab {1ake-extrabonds.txt 1ake-extrabonds-cispeptide.txt 1ake-extrabonds-chirality.txt} ' \
            + '-gscale 0.3 -numsteps 50000' ]
    
    task6.copy_input_data = [ '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, second_stage.name, task2.name, '4ake-target_autopsf-grid.dx'),
            '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name, task3.name, '1ake-docked-noh_autopsf.pdb'),
            '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name, task3.name, '1ake-docked-noh_autopsf.psf'),
            '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name, task3.name, '1ake-docked-noh_autopsf-grid.pdb'),
            '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, fourth_stage.name, task4.name, task4_output[0]),
            '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, fifth_stage.name, task5.name, task5_output[0]),
            '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, fifth_stage.name, task5.name, task5_output[1])]


    set_vmd_run(task6, task6_tcl_cmds, "sixth_stage.tcl")
    sixth_stage.add_tasks(task6)
    p.add_stages(sixth_stage)


    seventh_stage = Stage()
    seventh_stage.name = "NAMD simulation"
    task7 = Task()
    task7.cpu_reqs['processes'] = int(sim_cpus) // summit_hw_thread_cnt
    task7.cpu_reqs['threads_per_process'] = summit_hw_thread_cnt
    task7.pre_exec = sim_pre_exec
    task7.executable = [ namd_path ]
    task7.arguments = ['+ppn', summit_hw_thread_cnt, 'adk-step1.namd']
    task7.copy_input_data = [ '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name, task6.name, 'adk-step1.namd'),
        #'$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name, task6.name, 'adk-step2.namd'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name, task6.name, '1ake-docked-noh_autopsf.psf'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name, task6.name, '1ake-docked-noh_autopsf-docked.pdb'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name, task6.name, '1ake-docked-noh_autopsf-grid.pdb'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name, task6.name, '4ake-target_autopsf-grid.dx'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name, task6.name, '1ake-extrabonds-chirality.txt'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name, task6.name, '1ake-extrabonds-cispeptide.txt'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name, task6.name, '1ake-extrabonds.txt'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name,
            task6.name, 'mdff_template.namd'),
        #'$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name, task6.name, 'par_all27_prot_lipid_na.inp')
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name,
            task6.name, 'par_all36_prot.prm')
        ]
    task7.download_output_data = ['adk-step1.dcd']
    seventh_stage.add_tasks(task7)
    #task7_2 = Task()
    #task7_2.cpu_reqs['threads_per_process'] = sim_cpus    
    #task7_2.executable = [ 'namd2' ]
    #task7_2.executable = [ 'namd2' ]
    #task7_2.arguments = ['+ppn', sim_cpus, 'adk-step2.namd']
    #seventh_stage.add_tasks(task7_2)
    p.add_stages(seventh_stage)

    # Visualizing the MDFF trajectory
    #
    # mol new 4ake-target_autopsf.psf    
    # mol addfile 4ake-target_autopsf.pdb  
    # mol new 1ake-docked-noh_autopsf.psf   
    # mol addfile 1ake-docked-noh_autopsf-docked.pdb  
    # mol addfile adk-step1.dcd  
    # mol addfile adk-step2.dcd


    eighth_stage = Stage()
    eighth_stage.name = 'Calculating the root mean square deviation'
    task8 = Task()
    task8.cpu_reqs['threads_per_process'] = summit_hw_thread_cnt
    task8.cpu_reqs['processes'] = ana_cpus // summit_hw_thread_cnt
    task8_tcl_cmds = [ 'mol new 1ake-docked-noh_autopsf.psf',
            'mol addfile adk-step1.dcd waitfor all',
            'mol new 4ake-target_autopsf.pdb',
            'package require mdff',
            'mdff check -rmsd -refpdb 4ake-target_autopsf.pdb']

    task8.copy_input_data = [ '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name,
        first_stage.name, task1.name, '4ake-target_autopsf.pdb'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name,
            task3.name, '1ake-docked-noh_autopsf.psf'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, seventh_stage.name,
            task7.name, 'adk-step1.dcd')
        ]

    set_vmd_run(task8, task8_tcl_cmds, "eighth_stage.tcl")
    eighth_stage.add_tasks(task8)
    p.add_stages(eighth_stage)


    ninth_stage = Stage()
    ninth_stage.name = 'Calculating the root mean square deviation for backbone atoms'
    task9 = Task()
    task9.cpu_reqs['threads_per_process'] = summit_hw_thread_cnt
    task9.cpu_reqs['processes'] = ana_cpus // summit_hw_thread_cnt
    task9_tcl_cmds = [  'mol new 1ake-docked-noh_autopsf.psf',
            'mol addfile adk-step1.dcd waitfor all',
            'mol new 4ake-target_autopsf.pdb',
            'package require mdff',
            'set selbb [atomselect 0 "backbone"]',
            'set selbbref [atomselect 1 "backbone"]',
            '$selbb frame 0',
            'measure rmsd $selbb $selbbref',
            '$selbb frame last',
            'measure rmsd $selbb $selbbref' ]

    task9.copy_input_data = [ 
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, first_stage.name,
            task1.name, '4ake-target_autopsf.pdb'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name,
            task3.name, '1ake-docked-noh_autopsf.psf'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, seventh_stage.name,
            task7.name, 'adk-step1.dcd')
        ]

    set_vmd_run(task9, task9_tcl_cmds, "ninth_stage.tcl")
    ninth_stage.add_tasks(task9)
    p.add_stages(ninth_stage)

    tenth_stage = Stage()
    tenth_stage.name = 'Calculating the cross-correlation coefficient'
    task10 = Task()
    task10.cpu_reqs['threads_per_process'] = summit_hw_thread_cnt
    task10.cpu_reqs['processes'] = ana_cpus // summit_hw_thread_cnt
    task10_tcl_cmds = [ 'mol new 1ake-docked-noh_autopsf.psf' ]
    task10_tcl_cmds += [ 'mol addfile adk-step1.dcd waitfor all' ]    # load the full mdff trajectory
    #task10_tcl_cmds += [ 'mol new 4ake-target_autopsf.stius' ]        # load target EM density
    task10_tcl_cmds += [ 'package require mdff',
                         'set selall [atomselect 0 "all"]',
                         '$selall frame 0',
                         'mdff ccc $selall -i 4ake-target_autopsf-grid.dx -res 5',
                         '$selall frame last',
                         'mdff ccc $selall -i 4ake-target_autopsf-grid.dx -res 5' ]

    task10.copy_input_data = [
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, second_stage.name,
            task2.name, '4ake-target_autopsf-grid.dx'),

        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name,
            task3.name, '1ake-docked-noh_autopsf.psf'),

        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, seventh_stage.name,
            task7.name, 'adk-step1.dcd')
        ]

    set_vmd_run(task10, task10_tcl_cmds, "tenth_stage.tcl")
    tenth_stage.add_tasks(task10)
    p.add_stages(tenth_stage)


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

    if 'project' in resource_cfg[resource]:
        res_dict['project'] = resource_cfg[resource]['project']

    # Assign resource manager to the Application Manager
    appman.resource_desc = res_dict

    # Data shared between multiple tasks can be transferred while the 
    # job is waiting on queue
    appman.shared_data = []

    # Assign the workflow as a set or list of Pipelines to the Application Manager
    appman.workflow = [p]

    # Run the Application Manager
    appman.run()
