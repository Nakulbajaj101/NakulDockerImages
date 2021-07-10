from datetime import datetime, timedelta

import apache_beam as beam
from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from apache_beam.io.gcp.internal.clients import bigquery
from apache_beam.options.pipeline_options import PipelineOptions
from settings import bq_project, bq_external_dataset

source_path = '/usr/local/airflow/sales/input'
dest_path = '/usr/local/airflow/sales/output'
input_file = 'dept_data.txt'
output_file = 'dept_data'
table_name = "" #table name
column = "" #column name

options = {
    'project': bq_project,
    'runner:': 'DirectRunner',
    'streaming': True
}

options = PipelineOptions(flags=[], **options)  # create and set your PipelineOptions

def run_beam_test():
    p1 = beam.Pipeline()
    first_pipe = (p1
            |beam.io.ReadFromText(source_path+input_file)
            |beam.io.WriteToText(dest_path+output_file)
    )
    
    result = p1.run()
    result.wait_until_finish()

def beam_bq_table_to_local(project_id="", dataset_id="", table_id="",column="", file_path=""):
    table_spec = bigquery.TableReference(projectId=project_id,datasetId=dataset_id,tableId=table_id)
    p1 = beam.Pipeline(options=options)
    first_pipe = (
            p1
            | 'ReadTable' >> beam.io.Read(beam.io.BigQuerySource(table_spec))
            # Each row is a dictionary where the keys are the BigQuery columns
            | beam.Map(lambda elem: elem[column])
            | beam.io.WriteToText(file_path, header=column)

    )
    result = p1.run()
    result.wait_until_finish()





default_args = {
    "owner":"Nakul Bajaj",
    "start_date":datetime(2020,10,6),
    "retries":1,
    "retries_delay": timedelta(seconds=60),
    "depends_on_past":False,
    "email" : ["nakul.bajaj@anz.com"],
    "email_on_failure" : True,
    "email_on_retry" : False,
    "catchup": False,
}

with DAG("beam_test", default_args=default_args, schedule_interval=None, default_view="graph") as dag:
    task1 = PythonOperator(task_id="output_file",
                            python_callable=run_beam_test,
                            pool="default_pool")
    
    task2 = PythonOperator(
                            task_id="read_mcc_data",
                            python_callable=beam_bq_table_to_local,
                            op_kwargs={"project_id":bq_project,"dataset_id":bq_external_dataset,
                                        "table_id":table_name, "column":column,"file_path":dest_path+"bq_test"},
                            pool="default_pool"
                            )

    task1 >> task2
