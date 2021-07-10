#!/usr/bin/env python
# coding: utf-8


import pandas as pd
from google.cloud import bigquery

class BigqueryService():
    def __init__(self, project_id):
        self.project_id = project_id
        self.client = bigquery.Client(project_id)


    def get_data_bq(self, query='', dialect='standard', *args):
        df = pd.read_gbq(query=query, project_id=self.project_id, dialect=dialect, use_bqstorage_api=True, *args)
        return df

    def get_schema(self, dataset_id="", table_id=""):
        dataset_ref = bigquery.DatasetReference(self.project_id, dataset_id)
        table_ref = dataset_ref.table(table_id)
        table = self.client.get_table(table_ref)
        return table.schema

    def get_source_format_config(self, config="CSV"):
        if config == 'CSV':
            return bigquery.SourceFormat.CSV
        elif config == 'ORC':
            return bigquery.SourceFormat.ORC
        elif config == "JSON":
            return bigquery.SourceFormat.NEWLINE_DELIMITED_JSON


    def get_destination_format_config(self, config="CSV"):
        if config == 'CSV':
            return bigquery.DestinationFormat.CSV
        elif config == "JSON":
            return bigquery.DestinationFormat.NEWLINE_DELIMITED_JSON
        elif config == "AVRO":
            return bigquery.DestinationFormat.AVRO

    def get_write_disposition(self,disposition="empty"):
        if disposition == "empty":
            return bigquery.WriteDisposition.WRITE_EMPTY #This job should only be writing to empty tables.
        elif disposition == "truncate":
            return bigquery.WriteDisposition.WRITE_TRUNCATE #This job will truncate table data and write from the beginning.
        elif disposition == "append":
            return bigquery.WriteDisposition.WRITE_APPEND #This job will append to a table.

    def bq_to_bq(self, query='', table_id='',**kwargs):
        job_config = bigquery.QueryJobConfig(destination=table_id)
        job_config.write_disposition = bigquery.WriteDisposition.WRITE_TRUNCATE
        # Start the query, passing in the extra configuration.
        query_job = self.client.query(query, job_config=job_config)  # Make an API request.
        query_job.result()  # Wait for the job to complete.

        print("Query results loaded to the table {}".format(table_id))

    def bq_run_query(self, query = ""):
        # Perform a query.
        query_job = self.client.query(query)  # API request
        query_job.result()
        print("Job finished!")


    def delete_bq_table(self, dataset_id='', table_id=''):
        table_ref = self.client.dataset(dataset_id).table(table_id)
        # If the table does not exist, delete_table raises
        try:
            self.client.delete_table(table_ref)  # Make an API request.
        except Exception as e:
            print(e)
        print("Deleted table '{}'.".format(table_id))
