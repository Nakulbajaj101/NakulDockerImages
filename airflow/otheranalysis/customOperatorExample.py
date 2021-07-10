from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.python_operator import PythonOperator
from airflow.operators import CleanStringOperator, CustomSensorOperator
from airflow.hooks import LocalToGcsHook

args=dict(
    owner="Nakul Bajaj",
    email=['bajaj.nakul@gmail.com'],
    email_on_failure=True,
    email_on_retry=False,
    depends_on_past=False,
    retries=2
    )

dag=DAG('custom_operator_example',default_view="graph", schedule_interval="@once",start_date=datetime(2020,5,1), catchup=False, default_args=args)

def trigger_local_to_gcs_hook():
    LocalToGcsHook().copy_directory("/usr/local/airflow/sales", "bridge_data_analytics","Nakul", "fs_default")

t1 = CleanStringOperator(task_id="clean_file",
                        original_file_path="/usr/local/airflow/sales/raw_file.txt",
                        destination_file_path="/usr/local/airflow/sales/clean_file.txt",
                        matchStrings=["airflow","python"],
                        dag=dag
                        )

t2 = CustomSensorOperator(task_id="check_files",
                        dir_path="usr/local/airflow/sales/reports",
                        conn_id="fs_default",
                        poke_interval=10,
                        timeout=150,
                        soft_fail=True,
                        dag=dag
                        )
t3 = PythonOperator(task_id="custom_hook_test",
                    python_callable=trigger_local_to_gcs_hook,
                    dag=dag)
t1>>t2>>t3
