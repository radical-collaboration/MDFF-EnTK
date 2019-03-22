__author__ = "Vivek Balasubramanian <vivek.balasubramanian@rutgers.edu>"
__copyright__ = "Copyright 2016, http://radical.rutgers.edu"
__license__ = "MIT"

from radical.entk import Pipeline, Stage, Task, AppManager 

import argparse
import os
import re
import pprint
import glob


# USER PARS
ENSEMBLE_SIZE = int(os.environ.get('ENSEMBLE_SIZE', 1))
NS = int(os.environ.get('NS', 1))
TOTAL_ITERS = int(os.environ.get('TOTAL_ITERS', 1))

CPU_COUNT = 28

def get_pipeline():

    p = Pipeline()
    it_task_uids = []
    for it in range(TOTAL_ITERS):

        s1 = Stage()
        s1_task_uids = []
        for e in range(ENSEMBLE_SIZE):
            t = Task()
            t.pre_exec = [  'module load anaconda3',
                            'source activate openmm',
                            'export OPENMM_CPU_THREADS=20']
            t.executable = ['python']
            t.cores = CPU_COUNT
            t.arguments = ['simulate.py', '--ns', NS]
            if it == 0:
                t.link_input_data = ['$SHARED/ala2.pdb', '$SHARED/simulate.py']
            else:
                t.link_input_data = [   '$SHARED/simulate.py',
                                        '%s/ala2-%s.pdb > ala2.pdb' %(it_task_uids[it-1]['msm'][0], e)
                                    ]

            s1.add_tasks(t)
            s1_task_uids.append('$Pipeline_%s_Stage_%s_Task_%s'%(p.uid, s1.uid, t.uid))

        p.add_stages(s1)
        it_task_uids.append({'openmm': s1_task_uids})

        s2 = Stage()        
        s2_task_uid = list()

        t = Task()
        t.pre_exec = [  'module load anaconda3',
                        'source activate openmm']
        t.executable = ['python']
        t.arguments = [ 'analyze.py',
                        '--lag', '2',
                        '--clusters', '100',
                        '--pdb', 'ala2.pdb',
                        '--components', '4',
                        '--stride', '10' ]
        t.cores = 1

        t.link_input_data = ['$SHARED/ala2.pdb', '$SHARED/analyze.py']
        t.download_output_data = [ 'microstate_info.txt > dur-%s-ensemble-%s-iters-%s/microstate_info-%s.txt' % (NS, ENSEMBLE_SIZE, TOTAL_ITERS, it),
                                    'macrostate_info.txt > dur-%s-ensemble-%s-iters-%s/macrostate_info-%s.txt' % (NS, ENSEMBLE_SIZE, TOTAL_ITERS, it)]

        for i in range(it+1):
            for j in range(ENSEMBLE_SIZE):
                t.link_input_data += ['%s/trajectory.dcd > trajectory-%s_%s.dcd' %(it_task_uids[i]['openmm'][j], i, j)]

        s2_task_uid.append('$Pipeline_%s_Stage_%s_Task_%s'%(p.uid,s2.uid, t.uid))
        s2.add_tasks(t)
        p.add_stages(s2)

        it_task_uids[it]['msm'] = s2_task_uid

    return p

if os.environ.get('RADICAL_ENTK_VERBOSE') == None:
    os.environ['RADICAL_ENTK_REPORT'] = 'True'

# Description of how the RabbitMQ process is accessible
# No need to change/set any variables if you installed RabbitMQ has a system
# process. If you are running RabbitMQ under a docker container or another
# VM, set "RMQ_HOSTNAME" and "RMQ_PORT" in the session where you are running
# this script.
hostname = os.environ.get('RMQ_HOSTNAME', 'localhost')
port = os.environ.get('RMQ_PORT', 5672)

if __name__ == '__main__':

    p = get_pipeline()

    # Create Application Manager
    appman = AppManager(hostname=hostname, port=port)
    #appman = AppManager(port=) # if using docker, specify port here.

    # Create a dictionary describe four mandatory keys:
    # resource, walltime, cores and project
    # resource is 'local.localhost' to execute locally
    res_dict = {

            'resource': 'xsede.bridges',
            'walltime': 15 * TOTAL_ITERS,
            'cpus': ENSEMBLE_SIZE * CPU_COUNT
    }

    # Assign resource manager to the Application Manager
    appman.resource_desc = res_dict

    # Assign the workflow as a set of Pipelines to the Application Manager
    appman.workflow = set([p])

    # Run the Application Manager
    appman.run()
