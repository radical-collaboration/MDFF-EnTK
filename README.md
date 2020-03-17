
# Simple MDFF

## Run

### OLCF Summit

```
 python simple_mdff.py --resource ornl_summit
```

### PSC Bridges

```
 python simple_mdff.py --resource xsede_bridges
```










## Installation and environment setup on VM

* ssh into `two.radical-project.org` with the given credentials. We suggesting using [tmux](https://github.com/tmux/tmux) for attach/detach screens across ssh connections.

* Virtualenv creation

```
virtualenv $HOME/myenv
source $HOME/myenv/bin/activate
```

* EnTK Installation: You can directly install from pypi

```
pip install radical.entk
```

You can check the version with ```radical-stack```, this
should print 0.7.* (where * is a number indicating versions
of patches).

* RabbitMQ

A docker instance is already setup on radical.two with
hostname 'two.radical-project.org' and port '33211' that
you can specify to your EnTK script using two environment
variables:

```
export RMQ_HOSTNAME='two.radical-project.org'
export RMQ_PORT=33239
```

If you want to create your own, please see [EnTK docs](https://radicalentk.readthedocs.io/en/latest/install.html#installing-rabbitmq).

* MongoDB

You can create a new mongodb instance on [mlab](https://mlab.com/).
Steps broadly include:

1. Create a new db instance with approriate geographic location,
instance size, etc.
2. Once created, select the db and add an user to it. Specify
a user name and password.
3. Copy the db url and specify it as environment variable

```
export RADICAL_PILOT_DBURL='<mongo url>'
```

## Instructions to setup passwordless login to Bridges

If you would like to execute the simulations on Bridges, you will
need to setup passwordless login to Bridges. You can find
the instructions [here](https://www.psc.edu/bridges/user-guide/connecting-to-bridges#gsissh).

Some instructions to install Globus toolkit for Ubuntu 16 can
be found [here](https://github.com/vivek-bala/docs/blob/master/misc/gsissh_setup_stampede_ubuntu_xenial.sh).


## Executing your script

We have tested the example script on SuperMIC currently. You don't have to
install anything on SuperMIC, as we have already created a conda env with
OpenMM that is automatically used by the script.

You will be executing the EnTK script on your laptop/VM. EnTK
and underlying systems will launch your tasks on the compute
nodes of the HPC automatically. On your laptop/VM, you can
start execution using:

```
python example.py --resource xsede_supermic
```

The default verbosity should give you updates about each stage of the
pipeline. If you want to increase the verbosity, you can specify
```RADICAL_ENTK_VERBOSE``` to ```INFO```.


If required, we also have a configuration for the Bridges machine on XSEDE. But
this is untested currently (due to high queue wait times).

## Looking at output

If successfully run, a folder of the format 
```dur-(sim_duration)-ensemble-(ensemble_size)-iters-(total_iterations)``` is
created on your laptop in the current directory. You can view the contents of
this folder to check the output.

## Instruction for installing OpenMM on Bridges

- `module load anaconda3`
- `conda env create -f environment.yml`

## Issue reporting

If there are any issues/questions, please create a ticket in the 
[EnTK repository](https://github.com/radical-cybertools/radical.entk)



