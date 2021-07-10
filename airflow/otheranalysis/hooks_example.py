from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from datetime import datetime, timedelta
from psycopg2.extras import execute_values


args = dict(
    owner="Nakul Bajaj",
    start_date=datetime(2020,4,18),
    email=["bajaj.nakul@gmail.com"],
    email_on_retry=False,
    email_on_failure=True,
    retries=3,
    retry_delay=timedelta(minutes=1),
    catchup=False,
    depends_on_past=False
)

query = """SELECT store_location, ROUND(sum(sp - cp),2) as loc_profit  from clean_store_transactions
where date = (select max(date) from clean_store_transactions)
group by store_location
order by loc_profit desc"""

def transfer_data(query='',**context):
    query = query
    source_hook = PostgresHook(postgres_conn_id="pg_conn_id", schema=context["source_schema"])
    source_conn = source_hook.get_conn()
    destination_hook = PostgresHook(postgres_conn_id="pg_conn_id", schema=context["destination_schema"]) #define if schema or database is different
    destination_conn = destination_hook.get_conn()
    source_cursor = source_conn.cursor()
    destination_cursor = destination_conn.cursor()

    source_cursor.execute(query)
    records = source_cursor.fetchall()
    if records:
        execute_values(destination_cursor, "CREATE table if not exists store_profit (STORE_LOCATION varchar(50), LOC_PROFIT decimal); INSERT INTO store_profit values %s ",records)
        destination_conn.commit()
    source_cursor.close()
    destination_cursor.close()
    source_conn.close()
    destination_conn.close()
    if records:
        print("data transferred successfully")
    else:
        print("no records found to transfer")

with DAG("hooks_example", default_args=args, default_view='graph', schedule_interval="@daily") as dag:

    t1 = PythonOperator(task_id="transfer_data",
    python_callable=transfer_data,
    op_args=[query],
    op_kwargs={
        "source_schema":"sales",
        "destination_schema":"sales"
    },
    provide_context=True
    )
t1
