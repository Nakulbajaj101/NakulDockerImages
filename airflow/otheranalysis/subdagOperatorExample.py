from airflow import DAG
from datetime import datetime, timedelta
from economics.subdagExample import subdag
from economics.subdagMessageExample import subdagmessage
from airflow.operators.subdag_operator import SubDagOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.executors.local_executor import LocalExecutor

DAG_NAME = "nakul_subdag_example"

args = {
    'owner' : 'Nakul Bajaj',
    'start_date': datetime(2020,5,1),
    'catchup': False,
    'depends_on_past' : False,
    'email': ["bajaj.nakul@gmail.com"],
    'email_on_failure': True,
    'email_on_retry':False,
    'retry_delay': timedelta(minutes=1),
    'retries': 3
}

dag = DAG(dag_id=DAG_NAME, default_view="graph",schedule_interval='@once',default_args=args)

start = DummyOperator(task_id='start_section_1',
        dag=dag)

section_1 = SubDagOperator(task_id='section_1',
            subdag=subdag(DAG_NAME,'section_1', args),
            executor=LocalExecutor(),
            dag=dag)
other_task = DummyOperator(task_id="other",dag=dag)

section_2 = SubDagOperator(task_id='section_2',
            subdag=subdagmessage(DAG_NAME, 'section_2', args),
            executor=LocalExecutor(),
            dag=dag)
end_task = DummyOperator(task_id='secton_2_end',
            dag=dag)

start >> section_1 >> other_task >> section_2 >> end_task
