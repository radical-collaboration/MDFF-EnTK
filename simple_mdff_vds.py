from radical.entk import Pipeline, Stage, Task, AppManager 

import argparse
import os
import re
import glob
import yaml
from pprint import pprint

def to_file(list_of_cmd, fname):
    with open(fname, "w") as f:
        for l in list_of_cmd:
            f.write(l + "\n")
        f.close()
        return fname


def set_executable_path(workflow_cfg, resource):
    global vmd_path, namd_path
    vmd_path = "vmd"
    namd_path = "namd2"
    if 'path' in workflow_cfg[resource]:
        if 'vmd' in workflow_cfg[resource]['path']:
            vmd_path = workflow_cfg[resource]['path']['vmd']
        if 'namd' in workflow_cfg[resource]['path']:
            namd_path = workflow_cfg[resource]['path']['namd']


def set_vmd_run(task, list_of_cmd, name=None):
    #fname = to_file(list_of_cmd, name or "input.tcl")
    tcl_script_in_string = "\n".join(list_of_cmd) + "\nexit"
    task.pre_exec += [ "echo '{}' > {}".format(tcl_script_in_string, name or "input.tcl")]
    task.executable =  vmd_path + ' -dispdev text -e ' +  name or "input.tcl" # to source a tcl script using command line version of vmd 
    #task.arguments = [ '-eofexit', '<', fname ]


def get_pipelines(workflow_cfg, resource):

    ## Extract resource-independent global parameters
    total_iters = workflow_cfg['global']['total_iters']
    ensemble_size = workflow_cfg['global']['ensemble_size']
    sim_duration = workflow_cfg['global']['sim_duration']

    # Create one Pipeline for the entire workflow. The Pipeline contains 1 
    # Simulation stage and 1 Analysis stage per iteration.
    # Please refer to the API reference for more details about Pipeline, Stage,
    # Task. Link: https://radicalentk.readthedocs.io/en/latest/api/app_create.html
    pipes = []
    for rep_idx in range(ensemble_size):
        p = Pipeline()
        p.name = 'simple-mdff-replica-%s' % rep_idx

        for iter_idx in range(total_iters):
            one_cycle(p, workflow_cfg, resource, rep_idx, iter_idx) # update pipeline, p 
        pipes.append(p)
    return pipes


def one_cycle(p, workflow_cfgs, resource, rep_idx, iter_idx):

    ## Simulation related parameters
    sim_pre_exec = workflow_cfg[resource]['simulation']['pre_exec'] or []
    sim_cpus = workflow_cfg[resource]['simulation']['cpus']

    ## Analysis related parameters
    ana_pre_exec = workflow_cfg[resource]['analysis']['pre_exec'] or []
    ana_cpus = workflow_cfg[resource]['analysis']['cpus']

    resolution = workflow_cfg['global']['resolution']

    gscale = workflow_cfg['global']['gscale']
    minsteps = workflow_cfg['global']['minsteps']
    numsteps = workflow_cfg['global']['numsteps']

    task1_output = ['4ake-target_autopsf.dx']
    task2_output = ['4ake-target_autopsf-grid.dx']
    task3_output = ['1ake-docked-noh_autopsf-grid.pdb']
    task4_output = ['1ake-extrabonds.txt', '1ake-extrabonds-cispeptide.txt', '1ake-extrabonds-chirality.txt']

    if resource[0:11] == "ornl_summit":
        summit_hw_thread_cnt = 4
        ana_thread_cnt = summit_hw_thread_cnt
        ana_process_cnt = ana_cpus // summit_hw_thread_cnt
        sim_thread_cnt = summit_hw_thread_cnt
        sim_process_cnt = int(sim_cpus) // summit_hw_thread_cnt
    else:
        ana_thread_cnt = ana_cpus
        ana_process_cnt = 1
        sim_thread_cnt = int(sim_cpus)
        sim_process_cnt = 1

    first_stage = Stage()
    # We use names of pipelines, stages, tasks to refer to data of a
    # particular task
    first_stage.name = 'Generating a simulated density map'


    # Create tasks and add them to stage

    # Generating target simulated density map at specified resoulution
    task1 = Task()
    task1.name = 'Starting to load the target PDB'
    task1.pre_exec = ana_pre_exec.copy()
    task1.cpu_reqs = {
            'threads_per_process': ana_thread_cnt,
            'processes': ana_process_cnt,
            'process_type': None,
            'thread_type': None}
    task1_tcl_cmds = [ 'mol new 4ake-target.pdb' ]
    task1_tcl_cmds += [ 'package require autopsf' ]
    task1_tcl_cmds += [ 'autopsf 4ake-target.pdb' ]
    task1_tcl_cmds += [ 'set sel [atomselect top all]' ]
    task1_tcl_cmds += [ 'package require mdff']
    task1_tcl_cmds += [ 'mdff sim $sel -res {} -o {}'.format(resolution, task1_output[0]) ]

    set_vmd_run(task1, task1_tcl_cmds, "first_stage.tcl")
    task1.link_input_data = [ "$SHARED/%s" % os.path.basename(x) for x in
            workflow_cfg[resource]['shared_data'] ]
    first_stage.add_tasks(task1)
    # Add sim_stage to Pipeline
    p.add_stages(first_stage)


    # Generating the griddx file
    second_stage = Stage()
    second_stage.name = 'Converting the density map to an MDFF potential'

    task2 = Task()
    task2.name = 'generate griddx file'
    task2.pre_exec = ana_pre_exec.copy()
    task2.cpu_reqs = {
            'threads_per_process': ana_thread_cnt,
            'processes': ana_process_cnt,
            'process_type': None,
            'thread_type': None}
    task2_tcl_cmds = [ 'package require mdff' ]
    task2_tcl_cmds += [ 'mdff griddx -i {} -o {}'.format(task1_output[0], task2_output[0]) ]
    task2.copy_input_data = ['$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, first_stage.name, task1.name, task1_output[0])]
    #task2.link_input_data = [ ("$SHARED/%s" % os.path.basename(x)) for x in \
    #        workflow_cfg[resource]['shared_data'] ]

    set_vmd_run(task2, task2_tcl_cmds, "second_stage.tcl")
    second_stage.add_tasks(task2)
    p.add_stages(second_stage)


    # Generating the gridpdb file
    third_stage = Stage()
    third_stage.name = 'Preparing the initial structure'

    task3 = Task()
    task3.name = 'Starting to load the initial structure'
    task3.pre_exec = ana_pre_exec.copy()
    task3.cpu_reqs = {
            'threads_per_process': ana_thread_cnt,
            'processes': ana_process_cnt,
            'process_type': None,
            'thread_type': None}
    task3_tcl_cmds = [ 'mol new 1ake-docked-noh.pdb' ]
    task3_tcl_cmds += [ 'package require autopsf' ]
    task3_tcl_cmds += [ 'autopsf 1ake-docked-noh.pdb' ]
    task3_tcl_cmds += [ 'package require mdff' ]
    task3_tcl_cmds += [ 'mdff gridpdb -psf 1ake-docked-noh_autopsf.psf -pdb 1ake-docked-noh_autopsf.pdb -o {}'.format(task3_output[0]) ]
    task3.link_input_data = [ "$SHARED/%s" % os.path.basename(x) for x in
            workflow_cfg[resource]['shared_data']]


    set_vmd_run(task3, task3_tcl_cmds, "third_stage.tcl")
    third_stage.add_tasks(task3)
    p.add_stages(third_stage)

    # generating secondary structure restraints
    fourth_stage = Stage()
    fourth_stage.name = 'Defining secondary structure restraints'

    task4 = Task()
    task4.name = "task4"
    task4.pre_exec = ana_pre_exec.copy()
    task4.cpu_reqs = {
            'threads_per_process': ana_thread_cnt,
            'processes': ana_process_cnt,
            'process_type': None,
            'thread_type': None}
    task4_tcl_cmds = [ 'package require ssrestraints',
            'mol new 1ake-docked-noh_autopsf.psf',
            'mol addfile 1ake-docked-noh_autopsf.pdb',
            'ssrestraints -psf 1ake-docked-noh_autopsf.psf -pdb 1ake-docked-noh_autopsf.pdb -o {} -hbonds'.format(task4_output[0]) ]

    task4_tcl_cmds += ['package require cispeptide']
    task4_tcl_cmds += ['package require chirality']
    task4_tcl_cmds += ['cispeptide restrain -o {}'.format(task4_output[1])]
    task4_tcl_cmds += ['chirality restrain -o {}'.format(task4_output[2])]   
    task4.copy_input_data = ['$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name, task3.name, '1ake-docked-noh_autopsf.pdb'),
            '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name, task3.name, '1ake-docked-noh_autopsf.psf')]

    set_vmd_run(task4, task4_tcl_cmds, "fourth_stage.tcl")
    fourth_stage.add_tasks(task4)
    p.add_stages(fourth_stage)

    if iter_idx != 0:
        minsteps = 0
        
    # Setting up MDFF
    fifth_stage = Stage()
    fifth_stage.name = 'Running the MDFF simulation with NAMD'
    task5 = Task()
    task5.name = "task5"
    task5.pre_exec = ana_pre_exec.copy()
    task5.cpu_reqs = {
            'threads_per_process': ana_thread_cnt,
            'processes': ana_process_cnt,
            'process_type': None,
            'thread_type': None}
    task5_tcl_cmds = [ 'package require mdff' ]
    task5_tcl_cmds += [ 'mdff setup -o adk -psf 1ake-docked-noh_autopsf.psf ' \
            + '-pdb 1ake-docked-noh_autopsf.pdb ' \
            + '-griddx 4ake-target_autopsf-grid.dx ' \
            + '-gridpdb 1ake-docked-noh_autopsf-grid.pdb ' \
            + '-extrab {1ake-extrabonds.txt 1ake-extrabonds-cispeptide.txt 1ake-extrabonds-chirality.txt} ' \
            + f'-gscale {gscale} -minsteps {minsteps} -numsteps {numsteps}' ]
    
    task5.copy_input_data = [ '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, second_stage.name, task2.name, '4ake-target_autopsf-grid.dx'),
            '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name, task3.name, '1ake-docked-noh_autopsf.pdb'),
            '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name, task3.name, '1ake-docked-noh_autopsf.psf'),
            '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name, task3.name, '1ake-docked-noh_autopsf-grid.pdb')]
    for filename in task4_output:
        task5.copy_input_data += [
            '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, fourth_stage.name, task4.name, filename)]

    set_vmd_run(task5, task5_tcl_cmds, "fifth_stage.tcl")
    fifth_stage.add_tasks(task5)
    p.add_stages(fifth_stage)

    # Running MDFF
    sixth_stage = Stage()
    sixth_stage.name = "NAMD simulation"
    task6 = Task()
    task6.name = "task6"
    task6.cpu_reqs = {
            'threads_per_process': sim_thread_cnt,
            'processes': sim_process_cnt,
            'process_type': 'MPI',
            'thread_type': 'OpenMP'}
    task6.pre_exec = sim_pre_exec.copy()
    task6.executable = namd_path
    task6.arguments = ['+ppn', sim_thread_cnt, 'adk-step1.namd']
    task6.copy_input_data = [ '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, fifth_stage.name, task5.name, 'adk-step1.namd'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, fifth_stage.name, task5.name, '1ake-docked-noh_autopsf.psf'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, fifth_stage.name, task5.name, '1ake-docked-noh_autopsf.pdb'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, fifth_stage.name, task5.name, '1ake-docked-noh_autopsf-grid.pdb'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, fifth_stage.name, task5.name, '4ake-target_autopsf-grid.dx'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, fifth_stage.name, task5.name, '1ake-extrabonds-chirality.txt'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, fifth_stage.name, task5.name, '1ake-extrabonds-cispeptide.txt'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, fifth_stage.name, task5.name, '1ake-extrabonds.txt'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, fifth_stage.name,task5.name, 'mdff_template.namd'),
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, fifth_stage.name, task5.name, 'par_all36_prot.prm')]

    if iter_idx != 0:
        task6.pre_exec += ['export fpath=`grep -v "a" $RP_PILOT_STAGING/*_{}_cc.dat|sort -k2 -n -r|head -n1|cut -d":" -f1`'.format(iter_idx-1),
              'export fname=`basename $fpath`', 
              'echo $fname',
              'echo $fpath',
              'replica_id=`echo $fname|cut -d_ -f1`',
              'iter_id=`echo $fname|cut -d_ -f2`',
              'echo $replica_id, $iter_id',
              'cp $RP_PILOT_STAGING/${replica_id}_${iter_id}_*restart.* .',
              'cp $fpath .',
              #'iter_idxpp={}'.format(iter_idx + 1),		
              #'touch adk-step${iter_idxpp}.namd',
              #'head -n 17 adk-step1.namd >> adk-step${iter_idxpp}.namd',
              #'echo "set OUTPUTNAME adk-step${iter_idxpp}" >> adk-step${iter_idxpp}.namd',
              #'echo "set INPUTNAME ${replica_id}_${iter_id}_adk-step{}" >> adk-step${iter_idxpp}.namd'.format(iter_idx),
              #'tail -n 23 adk-step1.namd >> adk-step${iter_idxpp}.namd'] 
              'sed -i -- "s/#####/set INPUTNAME ${replica_id}_${iter_id}_adk-step1\\n\\n#####/" adk-step1.namd']
    #task6.post_exec = ['if [ -f "adk-step${iter_idxpp}.dcd" ]; then ln -s adk-step${iter_idxpp}.dcd adk-step1.dcd; fi']
    # note: for now this remains but ideally should be changed. not changed because of subsequent stages
    task6.download_output_data = ['adk-step1.dcd']   
    sixth_stage.add_tasks(task6)
    p.add_stages(sixth_stage)

    
    ## Analysis stage

    seventh_stage = Stage()
    seventh_stage.name = 'Calculating the cross-correlation coefficient of full trajectory'
    task7 = Task()
    task7.name = "task7"
    task7.pre_exec = ana_pre_exec.copy()
    task7.cpu_reqs = {
            'threads_per_process': ana_thread_cnt,
            'processes': ana_process_cnt,
            'process_type': None,
            'thread_type': None}
    task7_tcl_cmds = [ 'mol new 1ake-docked-noh_autopsf.psf' ]
    task7_tcl_cmds += [ 'mol addfile adk-step1.dcd waitfor all' ]    # load the full mdff trajectory
    task7_tcl_cmds += [ 'package require mdff',
                        'mdff check -ccc -map 4ake-target_autopsf.dx -res {} waitfor -1 -cccfile all.cc.dat'.format(resolution)]

    task7.copy_input_data = [
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, first_stage.name,
            task1.name, '4ake-target_autopsf.dx'),

        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name,
            task3.name, '1ake-docked-noh_autopsf.psf'),

        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name,
            task6.name, 'adk-step1.dcd')
        ]
    #task7.link_input_data = [ "$SHARED/%s" % os.path.basename(x) for x in
    #        workflow_cfg[resource]['shared_data'] ]

    set_vmd_run(task7, task7_tcl_cmds, "seventh_stage.tcl")
    seventh_stage.add_tasks(task7)
    p.add_stages(seventh_stage)


    eight_stage = Stage()
    eight_stage.name = 'Calculating the cross-correlation coefficient'
    task8 = Task()
    task8.name = "task8"
    task8.pre_exec = ana_pre_exec.copy()
    task8.cpu_reqs = {
            'threads_per_process': ana_thread_cnt,
            'processes': ana_process_cnt,
            'process_type': None,
            'thread_type': None}
    task8_tcl_cmds = [ 'mol new 1ake-docked-noh_autopsf.psf' ]
    task8_tcl_cmds += [ 'mol addfile adk-step1.dcd waitfor all' ]    # load the full mdff trajectory
    task8_tcl_cmds += [ 'set outfilename cc.dat',
                         'package require mdff',
                         'set selall [atomselect 0 "all"]',
                         '$selall frame 0',
                         'set lcc [mdff ccc $selall -i 4ake-target_autopsf.dx -res {}]'.format(resolution),
                         '$selall frame last',
                         'set fcc [mdff ccc $selall -i 4ake-target_autopsf.dx -res {}]'.format(resolution),
                         'lappend cc $lcc $fcc',
                         'set outfile [open $outfilename w]',
                         'puts $outfile "$cc"']

    task8.copy_input_data = [
        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, first_stage.name,
            task1.name, '4ake-target_autopsf.dx'),

        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, third_stage.name,
            task3.name, '1ake-docked-noh_autopsf.psf'),

        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name,
            task6.name, 'adk-step1.dcd'),

        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name,
            task6.name, 'adk-step1.restart.coor'),

        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name,
            task6.name, 'adk-step1.restart.vel'),

        '$Pipeline_{}_Stage_{}_Task_{}/{}'.format(p.name, sixth_stage.name,
            task6.name, 'adk-step1.restart.xsc')
        ]
    #task8.link_input_data = [ "$SHARED/%s" % os.path.basename(x) for x in
    #        workflow_cfg[resource]['shared_data'] ]
    task8.copy_output_data = [
            'adk-step1.restart.coor > $SHARED/{}_{}_adk-step1.restart.coor'.format(rep_idx, iter_idx),
            'adk-step1.restart.vel > $SHARED/{}_{}_adk-step1.restart.vel'.format(rep_idx, iter_idx),
            'adk-step1.restart.xsc > $SHARED/{}_{}_adk-step1.restart.xsc'.format(rep_idx, iter_idx),
            'cc.dat > $SHARED/{}_{}_cc.dat'.format(rep_idx, iter_idx)]

    set_vmd_run(task8, task8_tcl_cmds, "eighth_stage.tcl")
    eight_stage.add_tasks(task8)
    p.add_stages(eight_stage)


if os.environ.get('RADICAL_ENTK_VERBOSE') == None:
    os.environ['RADICAL_ENTK_REPORT'] = 'True'


if __name__ == '__main__':

    # Parse arguments from the command line
    parser = argparse.ArgumentParser(description='Process some arguments to get resource and workflow cfgs')
    parser.add_argument('--resource', help='path to workflow cfg file',
            required=False, default='ornl_summit')
    parser.add_argument('--nodes', help='the number of nodes to use',
            required=False)
    args = parser.parse_args()
    resource = args.resource


    # Load resource cfg 
    with open('cfg/resource_cfg.yml','r') as fp:
        resource_cfg = yaml.load(fp, Loader=yaml.Loader)

    # Load workflow cfg
    with open('cfg/workflow_cfg.yml','r') as fp:
        workflow_cfg = yaml.load(fp, Loader=yaml.Loader)
        set_executable_path(workflow_cfg, resource)


    # Create Pipeline
    pipes = get_pipelines(workflow_cfg, resource)


    # configure mongodb
    if 'mongodb' in resource_cfg:
        os.environ['RADICAL_PILOT_DBURL'] = resource_cfg['mongodb']['url']

    # Create Application Manager
    appman = AppManager(hostname=os.environ.get('RMQ_HOSTNAME',
        resource_cfg['rabbitmq']['hostname']), 
        port=os.environ.get('RMQ_PORT', resource_cfg['rabbitmq']['port']),
        username=os.environ.get('RMQ_USERNAME',None),
        password=os.environ.get('RMQ_PASSWORD',None))

    # override the number of nodes to start from user input parameter
    if args.nodes and int(args.nodes) > 0:
        resource_cfg[resource]['cpus'] = \
                int(resource_cfg[resource]['cpus_per_node']) * int(args.nodes)

    # Create a dictionary describe five mandatory keys:
    # resource, walltime, cores, queue and access_schema
    res_dict = {

        'resource': resource_cfg[resource]['label'],
        'walltime': resource_cfg[resource]['walltime'],
        'cpus': resource_cfg[resource]['cpus'] * workflow_cfg['global']['ensemble_size'],
        'access_schema': resource_cfg[resource]['access_schema']
        }
    if 'queue' in resource_cfg[resource]:
        res_dict['queue'] = resource_cfg[resource]['queue']

    if 'project' in resource_cfg[resource]:
        res_dict['project'] = resource_cfg[resource]['project']

    # Assign resource manager to the Application Manager
    appman.resource_desc = res_dict

    # Data shared between multiple tasks can be transferred while the 
    # job is waiting on queue
    appman.shared_data = workflow_cfg[resource]['shared_data']

    # Assign the workflow as a set or list of Pipelines to the Application Manager
    appman.workflow = pipes

    # Run the Application Manager
    appman.run()
