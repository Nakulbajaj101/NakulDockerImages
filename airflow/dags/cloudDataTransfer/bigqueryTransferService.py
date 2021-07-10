import subprocess
import logging
import pandas as pd
from google.cloud import bigquery
from bigqueryService import BigqueryService

logging.basicConfig(level=logging.INFO)

class BigqueryTransferService(BigqueryService):
    def __init__(self, project_id, bucket_uri, dataset):
        BigqueryService.__init__(self, project_id=project_id)
        self.bucket_uri = bucket_uri
        self.dataset = dataset

    def find_tables(self):
        query="""SELECT table_name
            FROM
            {}.INFORMATION_SCHEMA.TABLES
            where table_catalog = '{}'
            and table_schema = '{}'
            """.format(self.dataset,self.project_id, self.dataset)
            
        df = self.get_data_bq(query=query,dialect="standard")
        return list(df["table_name"])
    
    def get_compression_config(self, compression="gzip"):
        if compression == "gzip":
            return bigquery.Compression.GZIP
        elif compression == "snappy":
            return bigquery.Compression.SNAPPY
        elif compression == "deflate":
            return bigquery.Compression.DEFLATE
        else:
            return bigquery.Compression.NONE


    def move_data_bq_gcs(self, table_id="",table_location="EU",file_name="", file_extension='csv',compression="",field_delimiter='|'):
        # from google.cloud import bigquery
        destination_uri = "{}/{}/{}".format(self.bucket_uri,table_id,file_name+"-*.{}".format(file_extension))
    
        dataset_ref = bigquery.DatasetReference(self.project_id, self.dataset)
        table_ref = dataset_ref.table(table_id)
        job_config = bigquery.job.ExtractJobConfig()
        job_config.destination_format = self.get_destination_format_config(config=file_extension.upper())
        job_config.compression = self.get_compression_config(compression)
        if file_extension == 'csv':
            job_config.field_delimiter = field_delimiter
        try: 
            extract_job = self.client.extract_table(
                table_ref,
                destination_uri,
                # Location must match that of the source table.
                location=table_location, job_config=job_config)  # API request
            extract_job.result()  # Waits for job to complete.
            logging.info("Exported {}:{}.{} to {}".format(self.project_id, self.dataset, table_id, destination_uri))
        except Exception as e:
            logging.info(f"Cannot extract table {table_id} due to {e}")
        


    def move_data_gcs_new_bq_table(self, table_id='', config='csv',schema=None, rows_skip=0, write_disposition="empty",time_partitioning=False, time_partitioning_field=None, time_partitioning_type=bigquery.TimePartitioningType.DAY, require_partition_filter=False, field_delimiter='|'):
        dataset_ref = self.client.dataset(self.dataset)
        if config == "json":
            job_config = bigquery.LoadJobConfig()
        else:
            job_config = bigquery.LoadJobConfig(skip_leading_rows=rows_skip, field_delimiter=field_delimiter, allow_jagged_rows=True,allow_quoted_newlines=True)
        
        job_config.source_format = self.get_source_format_config(config.upper())
        job_config.write_disposition = self.get_write_disposition(disposition=write_disposition)
        
        table_ref = self.client.dataset(self.dataset).table(table_id)
        table = bigquery.Table(table_ref, schema=schema)
        
        if time_partitioning:
            table.time_partitioning = bigquery.TimePartitioning(type_=time_partitioning_type,
                field=time_partitioning_field,  # name of column to use for partitioning
                require_partition_filter=require_partition_filter                                                    
                )  
        if schema == None:
            logging.info("No schema provided so will try auto create")
        table = self.client.create_table(table,exists_ok=True)
        table_uri = "{}/{}/*".format(self.bucket_uri,table_id)
        try:
            load_job = self.client.load_table_from_uri(table_uri, dataset_ref.table(table_id), job_config=job_config)  # API request
            logging.info("Starting job {} for table {}".format(load_job.job_id, table_id))

            load_job.result()  # Waits for table load to complete.
            logging.info("Job finished.")

        except Exception as e:
            logging.info(f"Cannot load data from {table_uri} to table {table_id} due to {e} ")

    def move_data_gcs_bq_table(self, table_id='', config='CSV', rows_skip=0, write_disposition="truncate",field_delimiter='|'):
        dataset_ref = self.client.dataset(self.dataset)
        if config == "JSON":
            job_config = bigquery.LoadJobConfig()
        else:
            job_config = bigquery.LoadJobConfig(skip_leading_rows=rows_skip,field_delimiter=field_delimiter,allow_jagged_rows=True,allow_quoted_newlines=True)
    
        job_config.source_format = self.get_source_format_config(config)
        job_config.write_disposition = self.get_write_disposition(disposition=write_disposition)
        job_config.create_disposition = bigquery.CreateDisposition.CREATE_IF_NEEDED
        
        try:
            load_job = self.client.load_table_from_uri(self.bucket_uri, dataset_ref.table(table_id), job_config=job_config)
            logging.info("Starting job {} for table {}".format(load_job.job_id, table_id))
            
            load_job.result()  # Waits for table load to complete.
            logging.info("Job finished.")
        
        except Exception as e:
            logging.info(f"Cannot load data from {self.bucket_uri} to table {table_id} due to {e} ")
