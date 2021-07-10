from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.email_operator import EmailOperator
from airflow.contrib.sensors.gcs_sensor import GoogleCloudStorageObjectSensor
from airflow.contrib.sensors.file_sensor import FileSensor
from airflow.models import Variable
from economics.datacleaner import datacleaner

default_args = {
    "owner" : "Nakul Bajaj",
    "start_date" : datetime(2020,4,12),
    "retries" : 2,
    "retry_delay" : timedelta(seconds=30),
    "depends_on_past" : False,
    "email" : ["bajaj.nakul@gmail.com"],
    "email_on_failure" : True,
    "email_on_retry" : False,
    "catchup": False
}

check_file_template="""shasum {{params.file}}"""
new_folder_template="""cd {{params.directory}}
                       mkdir -p {{params.folder}}"""
yesterday_date=datetime.strftime(datetime.today()-timedelta(days=1),'%Y-%m-%d')

with DAG('store_dag', default_args=default_args, schedule_interval="@daily", default_view='graph',template_searchpath=['/usr/local/airflow/sales/templates']) as dag:


    gcsSensor = GoogleCloudStorageObjectSensor(
            task_id='check_file_exists_in_gcs',
            bucket='anz-insto-dev-economics-import',
            object='raw_store_transactions.csv',
            google_cloud_conn_id='google_cloud_default',
            poke_interval=30,
            timeout=150,
            soft_fail=True,
            delegate_to=None)

    fileSensor = FileSensor(
            task_id='check_file_exists_local',
            filepath='/usr/local/airflow/sales/raw_store_transactions.csv',
            fs_conn_id='fs_default',
            poke_interval=30,
            timeout=150,
            soft_fail=True
    )

    t1 = BashOperator(task_id="check_raw_file",
            bash_command=check_file_template,
            retries=2,
            retry_delay=timedelta(seconds=15),
            params={"file":"~/sales/raw_store_transactions.csv"},
            )


    t2 = PythonOperator(task_id="clean_transaction_file",
            python_callable=datacleaner,
            )

    t3 = PostgresOperator(task_id="create_transactions_table",
            sql="create_transaction_table.sql",
            postgres_conn_id="pg_conn_id",
            )

    t4 = PostgresOperator(task_id="insert_daily_data",
            sql="insert_clean_data.sql",
            postgres_conn_id="pg_conn_id",
            )

    t5 = PostgresOperator(task_id="create_profit_reports",
            sql="create_profit_reports.sql",
            postgres_conn_id="pg_conn_id",
            )

    t6 = BashOperator(task_id="move_location_report",
            bash_command=new_folder_template + ' && mv {{params.directory}}/{{params.file}}.csv {{params.directory}}/{{params.folder}}/{{params.file}}_%s.csv' % yesterday_date,
            params={"directory":"/usr/local/airflow/sales","folder":"reports", "file":"location_daily_profit"},
            )

    t7 = BashOperator(task_id="move_store_report",
            bash_command=new_folder_template + ' && mv {{params.directory}}/{{params.file}}.csv {{params.directory}}/{{params.folder}}/{{params.file}}_%s.csv' % yesterday_date,
            params={"directory":"/usr/local/airflow/sales","folder":"reports", "file":"store_daily_profit"},
            )

    t8 = EmailOperator(task_id="email_profitability_reports",
            to="bajaj.nakul@gmail.com",
            subject="Profitability Reports",
            html_content="""<h1> Profitability reports for store and location are ready </h1>""",
            files=["/usr/local/airflow/sales/reports/location_daily_profit_%s.csv" % yesterday_date,
                "/usr/local/airflow/sales/reports/store_daily_profit_%s.csv" % yesterday_date],
            )

    t9 = BashOperator(task_id="move_raw_file",
            bash_command= 'mv {{params.directory}}/{{params.file}}.csv {{params.directory}}/{{params.folder}}/{{params.file}}_%s.csv' % yesterday_date,
            params={"directory":"/usr/local/airflow/sales","folder":"reports", "file":"raw_store_transactions"},
            )
    t10 = BashOperator(task_id="variable_test",
            bash_command='echo "bq project is " {{var.value.personal_project}}')


[gcsSensor,fileSensor] >> t1 >> t2 >> t3 >> t4 >> t5 >> [t6,t7] >> t8 >> t9
t10
