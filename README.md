
# MDFF-EnTK

## Experiment

https://github.com/radical-experiments/MDFF-EnTK

## Run

### Python virtualenv activation

The command activate python with RADICAL Cybertools, otherwise python does not recognize RCT e.g. EnTK.

```
source $HOME/simple_mdff/bin/activate
```

Conda works fine, if preferred. e.g. `conda activate simple_mdff`

### ORNL Summit

The special script for Summit loads configuration files and start a workflow described by:

```
 python simple_mdff.summit.py
```

The example output message on the screen is like:

```
EnTK session: re.session.login4.hrlee.018391.0000
Creating AppManagerSetting up RabbitMQ system                                 ok
                                                                              ok
Validating and assigning resource manager                                     ok
Setting up RabbitMQ system                                                   n/a
new session: [re.session.login4.hrlee.018391.0000]                             \
database   : [mongodb://rct:rct_test@two.radical-project.org/rct_test]        ok
create pilot manager                                                          ok
submit 1 pilot(s)
        [ornl.summit:336]
                                                                              ok
All components created
create unit managerUpdate: simple-mdff state: SCHEDULING
Update: simple-mdff.Generating a simulated density map state: SCHEDULING
Update: simple-mdff.Generating a simulated density map.Starting to load the target PDB state: SCHEDULING
Update: simple-mdff.Generating a simulated density map.Starting to load the target PDB state: SCHEDULED
Update: simple-mdff.Generating a simulated density map state: SCHEDULED
...
```
It shows that one pilot job (here it is a EnTK workflow) is submitted to `ornl.summit` resource with 336 cpu cores (== 2 nodes, where 1 node has 168 cores by 42 physical cores * 4 hw threads), and the first stage is scheduled to start. The messages of the sebsequent stages are supressed but states are reported like `SCHEDULED`, `EXECUTED`, and `DONE`. If there was a problem executing the task, you may find `FAILED` with the stage/task name on your screen. Also note that this runs on foreground so the terminal needs to be active until a job finishes. `tmux`, `screen`, or `nohup` are recommended to avoid any interruption if a workflow runs very long time.


### XSEDE Bridges

We also have tested XSEDE Bridges with the following script. Run it like:

```
 python simple_mdff.py --resource xsede_bridges
```

## OUTPUT/RESULTS

If you remember your session id of your last run e.g. `re.session.login4.hrlee.018391.0000`, you will find raw output/results here on Summit:
```
$MEMBERWORK/[PROJECT ID]/radical.pilot.sandbox/[SESSION ID]/pilot.0000
```

for example with the session id above and project id `csc393`:

```
cd $MEMBERWORK/csc393/radical.pilot.sandbox/re.session.login4.hrlee.018391.0000/pilot.0000
$ ls -d uni*/
unit.000000/  unit.000001/  unit.000002/  unit.000003/  unit.000004/  unit.000005/  unit.000006/  unit.000007/  unit.000008/  unit.000009/
```

## Software Dependency

- VMD
- NAMD
  - fftw (Summit)
- radical.entk
- pyaml
  
## Installation

Necessary modules are loaded first before to use python and pip for installation.

### Modules on Summit

```
module load python/3.7.0-anaconda3-5.3.0
module load py-virtualenv/16.0.0
```

### Modules on Bridges

```
module load python3
```

### PIP via Virtualenv

```
virtualenv $HOME/simple_mdff
source $HOME/simple_mdff/bin/activate
pip install radical.entk pyaml 
```

Conda env also works fine.


## Configuration (cfg directory)

### HPC job description (cfg/resource_cfg.yml)

A job submission with a number of CPUs/GPUs, computing expected duration, and project ID to consume allocation is defined in the yaml file, and multiple HPC platforms are supported, e.g. ORNL Summit, XSEDE Bridges.

```
ornl_summit:             # key name to recognize resource, this is also used in the parameter of `simple_mdff.py`. This has to be identical to the key name used in the workflow yaml file.
  label: 'ornl.summit'   # Unique name to identify HPC platform, find a full list here: https://github.com/radical-cybertools/radical.pilot/blob/devel/examples/config.json
  walltime: 30          # walltime in minute
  cpus: 168             # the number of CPUs, and the number of nodes is calculated based on the cpu counts. For example, Summit provides 168 usable processes per node, and then 168 requires 1 node. 169+ requires 2+ nodes as well.
  gpus: 0               # the number of GPUs, and the number of nodes is calculated based on the gpu counts. Upper bounds of CPUs/GPUs are used to calculate the number of nodes.
  queue: 'batch'         # system queue name which the job will be dispatched, Summit has `batch` and `killable` queues with different policies.
  access_schema: 'local' # remote access method, there are `ssh`, `gsissh`, and `local`
  project: 'CSC393'      # project id to gain allocation
```

### Workflow description (cfg/workflow_cfg.yml)

Simulation/analysis tasks have individual resource requirements such as cpu counts and a list of pre-executables.

```
ornl_summit:
  simulation:
    pre_exec:                      # list of commands prior to execute
        - 'module load fftw/3.3.8' # new command can be added in a new line
    cpus: 160
```

### RabbitMQ and MongoDB

Workflow state and session data are exchanged by RabbitMQ and stored by MongoDB in RADICAL-Cybertools. The default values are provided but a local system can be used instead.

- cfg/resource_cfg.yml:
``` 
rabbitmq:
  hostname: '129.114.17.233'
  port: 33239
mongodb:
  url: 'mongodb://rct:rct_test@129.114.17.233:27017/rct_test'
```

 `129.114.17.233` is a temporal host IP address, `radical-project.org` will be back online soon.

## Results of Experiments

The raw results of the experiments are stored on the following directory, `experiments` per HPC system.
Find the [README](experiments/README.md) for the details of :

- [Results on Summit](https://github.com/radical-experiments/MDFF-EnTK/tree/main/experiments#summit)
- [Results on Bridges](https://github.com/radical-experiments/MDFF-EnTK/tree/main/experiments#bridges)

## FAQ

- Q. Does an argument exist to specify the number of nodes in the resource file [resource_cfg.yml](resource_cfg.yml)? 
- A. It does not have an argument for node counts but cpu counts. For example, you place 56 cpus on Bridges (56cpus = 2nodes; 28 each according to [the document](https://portal.xsede.org/psc-bridges)). For summit, 168 cpus indicate 1 node (2 sockets * 21 cpus * 4 hw threads) according to [the document](https://docs.olcf.ornl.gov/systems/summit_user_guide.html).
For more number of nodes e.g. 4,8,16, … you can multiply cpu counts in the file.

## Issue reporting

If there are any issues/questions, please create a ticket in the 
[EnTK repository](https://github.com/radical-cybertools/radical.entk)



