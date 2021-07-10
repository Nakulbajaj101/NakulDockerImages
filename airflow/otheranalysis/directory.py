from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta


default_args = {
"owner": "Nakul Bajaj",
"depends_on_past": False,
"start_date": datetime(2020, 4, 3),
"email": ["bajaj.nakul@gmail.com"],
"email_on_failure": False,
"email_on_retry": False,
"retries": 1,
"catchup": False,
"retry_delay": timedelta(minutes=5)
}

dag = DAG("createdir", default_args=default_args, default_view='graph',schedule_interval='@once')


directory = "~/dags"
folder = "test_dir"

templated_create_directory = """
echo "{{ ds }}"
echo $PWD
echo {{ params.directory }}
echo creating directory if doesnt exist in {{ params.directory }}
if [ ! -d {{ params.directory }} ]; then
  mkdir {{ params.directory }};
fi
echo creating folder "{{ params.folder }}"  inside "{{ params.directory }}"
if [ ! -d {{ params.directory }}/{{ params.folder }} ]; then
  mkdir {{ params.directory }}/{{ params.folder }};
fi
"""
templated_print_directory = """
shasum {{ params.directory }}/{{ params.folder }}
echo directory created is: {{ params.directory }}/{{ params.folder }}
"""

t1 = BashOperator(task_id = "create_dir",
bash_command=templated_create_directory,
retries=2,
params={"directory":directory,"folder":folder},
dag=dag)

t2 = BashOperator(task_id = "print_dir_created",
bash_command=templated_print_directory,
retries=2,
params={"directory":directory,"folder":folder},
dag=dag
)

t2.set_upstream(t1)
#or t1 >> t2
