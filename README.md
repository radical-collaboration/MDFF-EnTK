
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

## Dependency

- VMD
- NAMD

## Installation

### Summit

```
module load python/3.7.0-anaconda3-5.3.0
module load py-virtualenv/16.0.0
```

### Bridges

```
module load python3
```

### Virtualenv

```
virtualenv $HOME/simple_mdff
source $HOME/simple_mdff/bin/activate
pip install radical.entk pyaml 
```

## Preparation

### RabbitMQ

```
export RMQ_HOSTNAME='two.radical-project.org'
export RMQ_PORT=33239
```

## Issue reporting

If there are any issues/questions, please create a ticket in the 
[EnTK repository](https://github.com/radical-cybertools/radical.entk)



