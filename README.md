
# NAMD-EnTK

## Run

### Python virtualenv activation

```
source $HOME/simple_mdff/bin/activate
```


### ORNL Summit

```
 python simple_mdff.summit.py
```

### XSEDE Bridges

```
 python simple_mdff.py --resource xsede_bridges
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

- [Results on Summit](experiments#summit)
- [Results on Bridges](experiments#bridges)

## FAQ

- Q. Does an argument exist to specify the number of nodes in the resource file [resource_cfg.yml](resource_cfg.yml)? 
- A. It does not have an argument for node counts but cpu counts. For example, you place 56 cpus on Bridges (56cpus = 2nodes; 28 each according to [the document](https://portal.xsede.org/psc-bridges)). For summit, 168 cpus indicate 1 node (2 sockets * 21 cpus * 4 hw threads) according to [the document](https://docs.olcf.ornl.gov/systems/summit_user_guide.html).
For more number of nodes e.g. 4,8,16, … you can multiply cpu counts in the file.

## Issue reporting

If there are any issues/questions, please create a ticket in the 
[EnTK repository](https://github.com/radical-cybertools/radical.entk)



