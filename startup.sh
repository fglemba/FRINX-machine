#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

# Common functions
script="startup.sh"

function example {
    echo -e "example: $script"
}

function usage {
 echo -e "usage: $script [OPTION]  \n"
}

function help {
  usage
    echo -e "OPTION:"
    echo -e "  -s | --skip      Skips health check."
    echo -e "\n"
  example
}

function check_success {
  if [[ $? -ne 0 ]]
  then
  RED='\033[0;31m'
  NC='\033[0m' # No Color
  printf "${RED}System is not healthy. Shutting down.\n${NC}"
  echo "Removing containers."
  ./teardown.sh
  exit
fi
}

function start_container {
  sudo docker-compose up -d "$1"
}

function start_containers {
local containers_to_start=("dynomite" "elasticsearch" "logstash" "conductor-server" "odl" "micros" "sample-topology" "uniconfig-ui" "kibana" "portainer")


for i in "${containers_to_start[@]}"; do

start_container $i
if [ "$skip" = false ]; then
  ./health_check.sh $i
  check_success $?
fi
echo "################"
done

}

function import_workflows {
sudo docker exec micros bash -c "cd /home/app/netinfra_utils && ./importWorkflow.sh"
if [ "$skip" = false ]; then
  check_success $?
fi

}

function import_devices {
# Import cli devices
sudo docker exec micros bash -c "cd /home/app && newman run netinfra_utils/devices/device_import.postman_collection.json --folder 'cli' -d netinfra_utils/devices/device_data.csv"
if [ "$skip" = false ]; then
  check_success $?
fi

#Import netconf devices
sudo docker exec micros bash -c "cd /home/app && newman run netinfra_utils/devices/device_import.postman_collection.json --folder 'netconf' -d netinfra_utils/devices/netconf_device_data.csv"
if [ "$skip" = false ]; then
  check_success $?
fi

}


# Loop arguments
skip=false
browser=flase
while [ "$1" != "" ];
do
case $1 in
    -s | --skip)
    skip=true
    shift
    ;;
    -b | --browser)
    browser=true
    shift
    ;;
    -h | --help )
    help
    exit
    ;;
    *)    # unknown option
    echo "$script: illegal option $1"
    exit 1 #error
    ;;
esac
done

# Clean up docker
sudo docker system prune -f

# Starts containers
start_containers

# Imports workflows
import_workflows

# Import devices
import_devices

echo -e 'Startup finished!\n'
echo -e 'FRINX UniConfig UI is ready and listening on port 3000. e.g. http://localhost:3000/\n'

if [ "$browser" = true ]; then
  if which google-chrome > /dev/null
  then
    google-chrome --disable-gpu http://localhost:3000/
  fi
fi