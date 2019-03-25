__author__ = "Vivek Balasubramanian <vivek.balasubramanian@rutgers.edu>"
__copyright__ = "Copyright 2016, http://radical.rutgers.edu"
__license__ = "MIT"

from radical.entk import Pipeline, Stage, Task, AppManager 

import argparse
import os
import re
import pprint
import glob
import yaml
from pprint import pprint

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
    p.name = 'msm'

    task_names = []
    for it in range(total_iters):

        sim_stage = Stage()
        # We use names of pipelines, stages, tasks to refer to data of a
        # particular task
        sim_stage.name = 'sim-stage-%s'%it

        sim_task_names = []

        # Create simulation tasks and add them to sim_stage
        for e in range(ensemble_size):
            sim_task = Task()
            sim_task.name = 'sim-task-%s' %e
            sim_task.pre_exec = sim_pre_exec
            sim_task.executable = ['python']
            sim_task.cpu_reqs['threads_per_process'] = sim_cpus
            sim_task.arguments = ['simulate.py', '--ns', sim_duration]
            if it == 0:
                sim_task.link_input_data = ['$SHARED/ala2.pdb', '$SHARED/simulate.py']
            else:
                sim_task.link_input_data = [   '$SHARED/simulate.py',
                                                '%s/ala2-%s.pdb > ala2.pdb' %(
                                                    # Data of msm task from previous iteration
                                                    task_names[it-1]['ana'][0], 
                                                    e)]

            sim_stage.add_tasks(sim_task)
            sim_task_names.append('$Pipeline_%s_Stage_%s_Task_%s'%(p.name, sim_stage.name, sim_task.name))

        # Add sim_stage to Pipeline
        p.add_stages(sim_stage)

        # Store names of simuation tasks
        task_names.append({'sim': sim_task_names})

        ana_stage = Stage()
        ana_stage.name = 'ana-stage-%s'%it
        ana_task_names = []

        # Create analysis tasks and add them to ana_stage
        ana_task = Task()
        ana_task.name = 'ana-task-%s'%it
        ana_task.pre_exec = ana_pre_exec
        ana_task.executable = ['python']
        ana_task.arguments = [ 'analyze.py',
                            '--lag', '2',
                            '--clusters', '100',
                            '--pdb', 'ala2.pdb',
                            '--components', '4',
                            '--stride', '10' ]
        ana_task.cpu_reqs['threads_per_process'] = ana_cpus

        ana_task.link_input_data = ['$SHARED/ala2.pdb', '$SHARED/analyze.py']
        ana_task.download_output_data = [ 'microstate_info.txt > dur-%s-ensemble-%s-iters-%s/microstate_info-%s.txt' % (sim_duration,
                                                                                                                ensemble_size, 
                                                                                                                total_iters, 
                                                                                                                it),
                                    'macrostate_info.txt > dur-%s-ensemble-%s-iters-%s/macrostate_info-%s.txt' % (sim_duration, 
                                                                                                                ensemble_size, 
                                                                                                                total_iters, 
                                                                                                                it)]

        for i in range(it+1):
            for j in range(ensemble_size):
                ana_task.link_input_data += ['%s/trajectory.dcd > trajectory-%s_%s.dcd' %(task_names[i]['sim'][j], i, j)]

        ana_task_names.append('$Pipeline_%s_Stage_%s_Task_%s'%(p.name,ana_stage.name, ana_task.name))

        # Add analysis task to ana_stage
        ana_stage.add_tasks(ana_task)

        # Add ana stage to Pipeline
        p.add_stages(ana_stage)

        # Store names of analysis tasks
        task_names[it]['ana'] = ana_task_names

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
    with open('./workflow_cfg.yml','r') as fp:
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
    appman.shared_data = [ './ala2.pdb','./simulate.py','./analyze.py' ]

    # Assign the workflow as a set or list of Pipelines to the Application Manager
    appman.workflow = [p]

    # Run the Application Manager
    appman.run()
