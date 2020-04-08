
# Simple MDFF

## Run

### Loading required environment setup

```
source $HOME/simple_mdff/bin/activate
export RMQ_HOSTNAME='two.radical-project.org'
export RMQ_PORT=33239
```

### OLCF Summit

```
 python simple_mdff.summit.py --resource ornl_summit
```

### PSC Bridges

```
 python simple_mdff.py --resource xsede_bridges
```

## Dependency

- VMD
- NAMD

## Installation

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

## Preparation

### HPC resource requests via YAML (resource_cfg.yml)

A job submission with a number of CPUs/GPUs, computing expected duration, and project ID to consume allocation is defined in the yaml file as several HPC platforms can be described, e.g. PSC Bridges and OLCF Summit.

```
ornl_summit:             # key name to recognize resource, this is also used in the parameter of `simple_mdff.py`. This has to be identical to the key name used in the workflow yaml file.
  label: 'ornl.summit'   # Unique name to identify HPC platform, find a full list here: https://github.com/radical-cybertools/radical.pilot/blob/devel/examples/config.json
  walltime: 30          # walltime in minute
  cpus: 168             # the number of CPUs, and the number of nodes is calculated based on the cpu counts. For example, Summit provides 168 usable processes per node, and then 168 requires 1 node. 169+ requires 2+ nodes as well.
  gpus: 0               # the number of GPUs, and the number of nodes is calculated based on the gpu counts. Upper bounds of CPUs/GPUs are used to calculate the number of nodes.
  queue: 'batch'
  access_schema: 'local' # remote access method, there are `ssh`, `gsissh`, and `local`
  project: 'CSC393'      # project id to gain allocation
```

### Workflow resource requests via YAML (simple_mdff_cfg.yml)

Simulation/analysis tasks have individual resource requirements such as cpu counts and a list of pre-executables.

```
ornl_summit:
  simulation:
    pre_exec:
        - 'module load fftw/3.3.8'
    cpus: 160
```

### RabbitMQ

```
export RMQ_HOSTNAME='two.radical-project.org'
export RMQ_PORT=33239
```

## Issue reporting

If there are any issues/questions, please create a ticket in the 
[EnTK repository](https://github.com/radical-cybertools/radical.entk)



