#!/bin/bash
docker-compose -f docker-compose-LocalExecutor.yml down -v
if [ -z "$1" ]
then
    echo "No argument supplied"
    echo "cleaning system with all images"
    docker stop $(docker ps -a -q)
    docker system prune --all -f

    docker-compose -f docker-compose-LocalExecutor.yml up -d
    sleep 50
    docker exec airflow-docker-kubernetes_webserver_1 bash airflow_connections_variables.sh
fi

if [[ $1 == 'start' ]]
then
    docker-compose -f docker-compose-LocalExecutor.yml up -d
    sleep 50
    docker exec airflow-docker-kubernetes_webserver_1 bash airflow_connections_variables.sh
fi
