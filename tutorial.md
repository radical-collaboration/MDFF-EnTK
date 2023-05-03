# R-MDFF Tutorial using Containers

This tutorial ensures a reproducibility of running R-MDFF. We use a Docker container for a quick demonstration of installing necessary software and launching an example on a local laptop. The tutorial may take 30 minutes to complete.

## 1. Building Docker Image of RADICAL-Cybertools

First, we show RADICAL-Cybertools installation based on the https://github.com/radical-cybertools/tutorials where `Dockerfile` is provided. Run the commands below to build the image (which is identical to the tutorial's README):

```
  git clone https://github.com/radical-cybertools/tutorials.git # 1.a., Clone the RADICAL tutorial
  sudo tutorials/docker/build.sh -n src/default -t r_mdff       # 1.b., Build Container Image
  sudo docker network create rct-network                        # 1.c., Prepare network for MongoDB
  sudo docker run -d --hostname mongodb --name rct-mongodb -p 27017:27017 \
           -e MONGO_INITDB_ROOT_USERNAME=root_user \
           -e MONGO_INITDB_ROOT_PASSWORD=root_pass \
           -e MONGO_INITDB_USERNAME=guest \
           -e MONGO_INITDB_PASSWORD=guest \
           -e MONGO_INITDB_DATABASE=default \
           --network rct-network mongo:4.4                      # 1.d., Run MongoDB service
  sudo docker exec rct-mongodb bash -c \
  "mongo --authenticationDatabase admin -u root_user -p root_pass default \
   --eval \"db.createUser({user: 'guest', pwd: 'guest', \
                           roles: [{role: 'readWrite', db: 'default'}]});\"" # 1.e., Setup MongoDB Default Account
```

To make sure the mongodb service is up and running:

```
sudo docker ps
```
and the output message looks like this with `Up` in the STATUS:
```
CONTAINER ID   IMAGE       COMMAND                  CREATED       STATUS         PORTS                                           NAMES
341a64f25f54   mongo:4.4   "docker-entrypoint.s…"   8 hours ago   Up 3 seconds   0.0.0.0:27017->27017/tcp, :::27017->27017/tcp   rct-mongodb
```

For those who needs to install Docker, please follow the official documentation: https://docs.docker.com/engine/install/

## 2. Run and Open an interactive shell

The following command runs the tutorial container, and provide a shell inside of the container instance:
```
sudo docker run --rm -it -p 8888:8888 --network rct-network \
    radicalcybertools/tutorials:r_mdff /bin/bash
```

and make sure you see the shell prompt like this which indicates you are inside of the container:
```
(base) jovyan@a86c4d2c1cdc:/tutorials$
```

## 3. Installation of R-MDFF

Now, we obtain R-MDFF code and pip install necessary packages from github:
```
sudo git clone https://github.com/radical-collaboration/MDFF-EnTK.git
pip install -r MDFF-EnTK/requirements.txt
```

## 4. Installation of NAMD and VMD

You may use the official documentation for installing NAMD and VMD:

- NAMD: https://www.ks.uiuc.edu/Development/Download/download.cgi?PackageName=NAMD
- VMD: https://www.ks.uiuc.edu/Development/Download/download.cgi?PackageName=VMD

## 5. Run of R-MDFF

```
export RADICAL_PILOT_DBURL=mongodb://guest:guest@mongodb:27017/default
python simple_mdff_vds.py --resource=localhost
```

For more details of running R-MDFF on HPC platforms, please see the README: https://github.com/radical-collaboration/MDFF-EnTK/blob/master/README.md
