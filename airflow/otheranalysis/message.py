
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
from datetime import datetime, timedelta
from settings import start_date

args = dict(
        owner = 'Nakul Bajaj',
        start_date=datetime(2020,4,18),
        email=["bajaj.nakul@gmail.com"],
        email_on_failure=True,
        email_on_retry=False,
        retries=0,
        retry_delay=timedelta(minutes=3),
        catchup=False
)

def push_message(**kwargs):
    message = "The actual start date is: {}".format(start_date)
    ti = kwargs["ti"]
    ti.xcom_push(key="message", value=message)

def push_new_date(days=0):
    message = "new date should be {}".format(start_date + timedelta(days=days))
    return message

def push_message_2(**kwargs):
    message = "The tomorrow date is: {}".format(start_date + timedelta(days=1))
    ti = kwargs["ti"]
    ti.xcom_push(key="message", value=message)

def pull_message(**kwargs):
    ti = kwargs["ti"]
    message = ti.xcom_pull(key="message")
    print("The message I received is '{}'".format(message))

def pull_message_2(**kwargs):
    ti = kwargs["ti"]
    message = ti.xcom_pull(key="message", task_ids='push_message_2')
    print("The message I received is '{}'".format(message))

def pull_new_date(**kwargs):
    ti = kwargs["ti"]
    new_date = ti.xcom_pull(key="return_value",task_ids='push_new_date')
    print("{}".format(new_date))

with DAG("xcomms_example", default_args=args, default_view="graph", schedule_interval=None) as dag:

    t1 = PythonOperator(
                task_id='push_message',
                python_callable=push_message,
                provide_context=True,
                pool='default_pool'
                )
    t2 = PythonOperator(
                task_id='push_new_date',
                python_callable=push_new_date,
                op_args=[3],
                pool='default_pool'
    )

    t3 = PythonOperator(
                task_id='push_message_2',
                python_callable=push_message_2,
                provide_context=True,
                pool='default_pool'
    )

    t4 = PythonOperator(
                task_id="pull_message",
                python_callable=pull_message,
                provide_context=True,
                pool='default_pool'
                )
    t5 = PythonOperator(
                task_id="pull_message_2",
                python_callable=pull_message_2,
                provide_context=True,
                pool='default_pool',
                priority_weight=2    #default is 1, higher means, get assigned first
    )

    t6 = PythonOperator(
                task_id='get_new_date',
                python_callable=pull_new_date,
                provide_context=True,
                pool='default_pool'
    )

    dummy = DummyOperator(task_id="dummy_for_control")

[t1,t2,t3] >> dummy >> [t4,t5,t6]
