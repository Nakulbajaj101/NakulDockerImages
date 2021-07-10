from airflow.plugins_manager import AirflowPlugin
from airflow.models import BaseOperator
from airflow.operators.sensors import BaseSensorOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.fs_hook import FSHook
from airflow.hooks.base_hook import BaseHook
from airflow.contrib.hooks.gcs_hook import GoogleCloudStorageHook
import logging as log
import os

class CleanStringOperator(BaseOperator):
    @apply_defaults
    def __init__(self, original_file_path, destination_file_path, matchStrings, *args, **kwargs):
        self.original_file_path=original_file_path
        self.destination_file_path=destination_file_path
        self.matchStrings=matchStrings
        super().__init__(*args, **kwargs)

    def execute(self, context):
        sourceFile=self.original_file_path
        destinationFile=self.destination_file_path
        matchStrings=self.matchStrings

        fileIn=open(sourceFile)
        fileOut=open(destinationFile,'a')

        for line in fileIn:
            log.info("reading line {}".format(line))
            for word in matchStrings:
                log.info('matching line with word %s' % (word))
                line=line.replace(word,"")
            log.info("output line is %s" % (line))
            fileOut.write(line)
        fileIn.close()
        fileOut.close()

class CustomSensorOperator(BaseSensorOperator):

    @apply_defaults
    def __init__(self, dir_path, conn_id, *args, **kwargs):
        self.dir_path=dir_path
        self.conn_id=conn_id
        super().__init__(*args, **kwargs)

    def poke(self, context):
        hook=FSHook(self.conn_id)
        basepath=hook.get_path()
        full_path=os.path.join(basepath,self.dir_path)
        log.info("Poking location %s", full_path)

        try:
            for root, dirs, files in os.walk(full_path):
                if len(files) > 5:
                    return True
        except OSError as e:
            log.info(e)
            return False
        return False

class LocalToGcsHook(BaseHook):

    def __init__(self):
        log.info("custom local to gcs hook started")

    def copy_directory(self, fs_path, bucket,destination, fs_conn_id):
        log.info("starting file transfer of file %s ", fs_path)
        local_hook=FSHook(fs_conn_id)
        basepath=local_hook.get_path()
        full_path=os.path.join(basepath,fs_path)

        gcs_hook = GoogleCloudStorageHook()
        files_and_dirs = os.listdir(full_path)
        files_to_upload = [file for file in files_and_dirs]

        for file in files_to_upload:
            if os.path.isfile(full_path + "/" + file):
                object = destination + "/" + file
                gcs_hook.upload(bucket, object, full_path + "/" + file, mime_type='application/octet-stream')
        return True


class DemoPlugin(AirflowPlugin):
    name = "demo-plugin"
    operators = [CleanStringOperator]
    sensors = [CustomSensorOperator]
    hooks = [LocalToGcsHook]
