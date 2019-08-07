# FRINX-machine
The project is a containerized package of: 

* [FRINX ODL]
* FRINX fork of Netflix's [Conductor]
* Elastic's
    * [Elasticsearch]
    * [Kibana]
    * [Logstash]
* FRINX microservices to execute conductor tasks
* Device simulation container
* [Uniconfig-ui]


## Documentation & Use Cases
https://frinxio.github.io/Frinx-docs/

## Requirements
* [Docker](https://www.docker.com/)
* [Docker Compose](https://github.com/docker/compose)
* License for FRINX ODL (you can find a trial license in the "Installation Guide" section below)

min 16GB RAM & min 4 vCPUs with normal startup, and 8GB RAM & 4 vCPUs with minimal config has been successfully tested for POCs and demos. 

### Tested on
* Ubuntu 16.04 / 18.04 /
* docker 18.03.1-ce, v18.06.1-ce, 18.09.5
* docker-compose 1.21.2, v1.22.0

## Installation preparation

### Docker

To install the Ubuntu repository version, execute the following command

	sudo apt-get install docker.io

Check the version with

	docker --version

You'll see output similar to this:

	Docker version 18.06.1-ce, build e68fc7a

### Docker Compose

To install Docker Compose, at first, install the `curl` command

Type the following apt or apt-get command:
	
	sudo apt install curl
	
After installing `curl`, use following command to get *Docker Compose*:

	sudo curl -L "https://github.com/docker/compose/releases/download/1.23.1/docker-compose-$(uname -s)-$(uname -m)" -o 	/usr/local/bin/docker-compose
	sudo chmod 755 /usr/local/bin/docker-compose
	
_Note: You can download the latest version of Docker Composer after checking Release Notes https://github.com/docker/compose/releases and finding the latest version, e.g. 1.23.2. Then you can edit the download link release version number to get the latest release._

## Installation Guide
#### Trial license
We offer a 30 day trial license. No signup needed!
License token:
```
0e57a786f7dbd27fa77db684cf3b234d6f23ed784e52cbfb107fd4317ba2646c66f7a141b0e823946d8f9d956852c95d33dc82f945779b1c9969049e94935b2a
```

30 days after your first installation, your token will expire and you will see an error message during ODL startup. If you would like to continue with your evaluation, please register as a user on our homepage, where you will find another 30 day token under the section "My License Information". After the second trial period has expired, you can continue with a commercial license that has no time limitations. 

#### Get the project
Clone the repository:
```bash
git clone https://github.com/FRINXio/FRINX-machine.git
```
Navigate into the project folder:
```bash
cd FRINX-machine
```

#### Services used in the project
* odl
* conductor-server
* elasticsearch
* kibana
* logstash
* micros
* uniconfig-ui
* sample-topology
 
### Installation

The installation script `install.sh` is in the FRINX-machine folder. 

*The installation script does the following things:*
* Updates project submodules (e.g. conductor)
* Copies license token
* Pulls conductor project parts from maven repository
* Builds conductor-server .jar file
* Pulls and creates docker images
* Creates external volumes for data persistence


We recommend to run the install script as regular user and not as sudo, so all files can be edited by the regular user later.
Installation with the trial license token:
```
./install.sh -l 0e57a786f7dbd27fa77db684cf3b234d6f23ed784e52cbfb107fd4317ba2646c66f7a141b0e823946d8f9d956852c95d33dc82f945779b1c9969049e94935b2a
```
After the first run the license token is saved to a <git directory>/odl/frinx.license.cfg and will be copied to image after each update.

Once images were downloaded, to update images from Docker Hub:
```
./install.sh [service]
```

To build image from cloned repository:
```
./install.sh -b [service]
```
If no container is specified all are updated.

To replace running service with new one run after updating the image:
```
sudo docker stop [service]
sudo docker rm [service]
sudo docker-compose up -d [service]
```

### Startup
The startup script `startup.sh` can be found in the FRINX-machine folder.
Here is what it does:
* Creates the docker containers from the images and starts them.
* Imports workflow definitions.


Docker needs privileged mode, so `startup.sh` should be executed with sudo. Otherwise it will prompt for password while executing.
```bash
sudo ./startup.sh
```
Min 16GB RAM & min 4 vCPUs with normal startup and 8GB RAM with 4 vCPUs for minimal startup are recommended.

#### Web interface
Open web page:
 http://localhost:3000


### Teardown
The `teardown.sh` script in the FRINX-machine folder:
* Stops and removes containers
* Does not remove external volumes

Using docker, also needs privileged mode:
```bash
sudo ./teardown.sh
```

### Removal of external volumes
#### **Caution all data will be lost!**

To remove the volumes use:
```bash
sudo docker volume rm redis_data elastic_data odl_logs
```

### Exposed ports
* Conductor-server: 
	* localhost:8080
	* localhost:8000

* ODL: 
	* localhost:8181

* Microservices: 
	* localhost:6000

* Elasticsearch: 
	* localhost:9200
	* localhost:9300
* Kibana:
    * localhost:5601
    
* Uniconfig-ui:
    * localhost:3000

	

[FRINX ODL]: <https://frinx.io/odl_distribution>
[Conductor]: <https://github.com/FRINXio/conductor>
[Elasticsearch]: <https://www.elastic.co/products/elasticsearch>
[Kibana]: <https://www.elastic.co/products/kibana>
[Logstash]: <https://www.elastic.co/products/logstash>
[Uniconfig-ui]: <https://github.com/FRINXio/frinx-uniconfig-ui>
