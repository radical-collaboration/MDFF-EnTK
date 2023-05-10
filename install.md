# R-MDFF Installation

This page provides an easy way of installing R-MDFF on Linux machines.

## Prerequisites

- Python 3.8 or higher
- pip for python3
- radical.entk
- Conda package management tool or virtualenv
- MongoDB

## (Optional) Python 3 via Conda

Conda manages system libraries and python package dependencies. First, you need to install conda if your machine doesn't have it. Please refer to the offical [website](https://docs.conda.io/en/latest/miniconda.html#linux-installers) to download, but here is one example to obtain miniconda:

### Conda Env

```
curl -L https://repo.anaconda.com/miniconda/Miniconda3-py310_23.3.1-0-Linux-x86_64.sh > Miniconda3-py310_23.3.1-0-Linux-x86_64.sh
bash Miniconda3-py310_23.3.1-0-Linux-x86_64.sh
```

After an successful installation of miniconda, you create a new python environment using conda named 'r-mdff' like:

```
conda create -n r-mdff python=3.10
conda activate r-mdff
``` 

Now, you have python3 is ready to use for R-MDFF.

*NOTE* make sure you have the label `(r-mdff)` in your prompt to activate the env : `(r-mdff) ubuntu@ip-172-30-1-66:~/MDFF-EnTK$`

### Cloning MDFF Repository

We need to download r-mdff script to run, and we use git clone like:

```
git clone https://github.com/radical-collaboration/MDFF-EnTK.git
```

### radical.entk Installation

We use `pip` to install radical.entk:

```
cd MDFF-EnTK
pip install -r requirements.txt
```

### MongoDB Installation

MongoDB is required to store workflow status for radical.entk and the commands below will require system administration (root priviledge) 
```
sudo apt-get update
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
mongosh default --eval "db.createUser({user: 'guest', pwd: 'guest', \
    roles: [{role: 'readWrite', db: 'default'}]});"
sudo systemctl restart mongod
sudo systemctl status mongod
```

- sudo is the elevation command of the priviledge
- apt-get update is refreshing cache to download
- systemctl is a daemon manage on Ubuntu and use it to manage mongodb service
- mongosh is a mongo shell command to create a user for radical.entk
- restart is a sub-command for systemctl to restart
- status is a sub-command to check e.g., whether it is running or not

### DB Environment Configuration

Once you have mongodb service running and r-mdff ready to use, you need to define db uri in a shell environment:

```
export RADICAL_PILOT_DBURL=mongodb://guest:guest@localhost:27017/default
``` 
```

## Run R-MDFF Example

On your local machine, you can run a quick test of using r-mdff. You may have to set NAMD, and VMD paths in the configuration.

If you use an editor to open a file, `./MDFF-EnTK/cfg/workflow_cfg.yml`, you can find sections for `localhost`, in specific the line number between 26 and 28:

```

  path:
    namd: './namd/bin/namd2'
    vmd: './vmd/bin/vmd'
```

Make changes accordingly to locate these commands in your machine.

Once you have the configuration YAML updated, you can run a test using python script like:

```
python simple_mdff_vds.py --resource=localhost
```
