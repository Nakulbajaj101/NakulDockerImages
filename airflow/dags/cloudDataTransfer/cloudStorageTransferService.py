import subprocess

class CloudStorageTransfer():
    def __init__(self, source_uri, destination_uri, parallel=True):
        self.source_uri = source_uri
        self.destination_uri = destination_uri
        self.parallel = parallel

    def copy(self, mode="cp",directory=True):
        subcommand = ""
        if self.parallel:
            if directory:
                subcommand = "-m {} -r".format(mode)
            else:
                subcommand = "-m {} ".format(mode)
        else:
            if directory:
                subcommand = "{} -r".format(mode)
            else:
                subcommand = "{}".format(mode)

        command = """gsutil {} {} {}""".format(subcommand, self.source_uri, self.destination_uri)
        process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        output, error = process.communicate()
        print("output: {}" .format(output.decode('utf-8')) , "error: {}" .format(error))