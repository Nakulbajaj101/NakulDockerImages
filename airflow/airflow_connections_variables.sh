#!/bin/bash
date_today=$(date +"%Y-%b-%d")
echo $date_today
airflow connections --add --conn_id=pg_conn_id --conn_uri=postgresql://${ADDITIONAL_USER}:${ADDITIONAL_USER_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${ADDITIONAL_DATABASE}
airflow variables --set gcp_project bridge_data_analytics
airflow variables --set todays_date ${date_today} 
airflow pool --set bigquery 10 "BigQuery operations"
airflow pool --set pipeline 4 "Max pipeline operations"
