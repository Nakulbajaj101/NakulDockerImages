import calendar
import os
from datetime import datetime, timedelta
from economics.helperFunctions import get_offset, create_dates_yoy, dynamic_sql_dates_between
from airflow.models import Variable

########################################################################################################################
# The variables in this section are used by Airflow DAGs directly
########################################################################################################################

bq_conn_id = "bigquery_default"
#gcs_bucket = "anz-insto-data-analytics-dev"
#gcs_project = "anz-insto-data-analytics-dev"
nightly_schedule_interval = "0 10 * * 1-5"  # 10AM UTC is 8PM Local time in Melbourne, 9PM in day light saving
monthly_schedule_interval = "0 10 * * 6#1" # first Sat of the month



########################################################################################################################
# The variables below are all stored as variables in Airflow and can be changed in the Composer environment
########################################################################################################################

bq_project = Variable.get('gcp_project', default_var = 'bridge_data_analytics') 
todaysDate = Variable.get('todays_date',default_var=datetime.strftime(datetime.today(),'%Y-%b-%d'))


