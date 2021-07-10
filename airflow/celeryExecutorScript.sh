#!/bin/bash

workers=$2

if [ -z "$1" ]
then
    docker-compose -f docker-compose-CeleryExecutor.yml down -v
    echo "No argument supplied"
    echo "cleaning system with all images"
    docker stop $(docker ps -a -q)
    docker system prune --all -f

    docker-compose -f docker-compose-CeleryExecutor.yml up -d

    sleep 50

    docker exec airflow-docker-kubernetes_webserver_1 bash airflow_connections_variables.sh

    exit
fi

if [[ $1 == 'start' && -z "$2" ]]
then 
    docker-compose -f docker-compose-CeleryExecutor.yml down -v
    docker-compose -f docker-compose-CeleryExecutor.yml up -d

    sleep 50

    docker exec airflow-docker-kubernetes_webserver_1 bash airflow_connections_variables.sh
fi

if [ -z "$2" ]
then 
    echo "No workers specified defaulting to 1"
    exit
fi


if ! [[ "$workers" =~ ^[0-9]+$ ]]
then 
    echo "Sorry integers only for number of workers"
fi

if [[ $workers < 1 || $workers > 3 ]]
then 
    echo "Sorry choose number of workers between 1 and 3"
fi

if [[ "$workers" =~ ^[0-9]+$ && $workers > 0 && $workers < 4 && ! -z "$1" ]] 
then 
    docker-compose -f docker-compose-CeleryExecutor.yml scale worker=$workers

fi


