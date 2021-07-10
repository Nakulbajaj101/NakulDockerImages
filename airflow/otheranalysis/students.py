from airflow import DAG
from datetime import datetime, timedelta
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.sensors import SqlSensor

default_args = dict(
            owner='Nakul Bajaj',
            depends_on_past=False,
            email=["bajaj.nakul@gmail.com"],
            email_on_failure=True,
            email_on_retry=False,
            retries=3,
            catchup=False,
            retry_delay=timedelta(minutes=3),
)


with DAG('assignment_2', schedule_interval='@daily',start_date=datetime(2020, 4, 18), default_args=default_args, default_view="graph") as dag:


    t1  = PostgresOperator(
             task_id='create_table_students',
             postgres_conn_id="pg_conn_id",
             sql="CREATE TABLE IF NOT EXISTS students (id int, name varchar(50));",
             )

    t2  = PostgresOperator(
             task_id='insert_student_data',
             postgres_conn_id="pg_conn_id",
             sql="INSERT INTO students VALUES (1, 'John'), (2, 'Mark'), (3, 'Kelly'), (4, 'Smith');",
             )

    t3 = SqlSensor(
             task_id='check_data_arrived',
             conn_id="pg_conn_id",
             sql="SELECT COUNT(*) FROM students;",
             poke_interval=5,
             timeout=20
             )

    t4  = PostgresOperator(
             task_id='create_backup_student_table',
             postgres_conn_id="pg_conn_id",
             sql="CREATE TABLE students_backup AS (SELECT * FROM students LIMIT 0); INSERT INTO students_backup SELECT * FROM students;",
             )

t1 >> t2 >> t3 >> t4
