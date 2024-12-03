import os
from dagster import sensor, RunRequest, RunConfig, define_asset_job, Config, OpExecutionContext, job, op
from dagster_clowder import ops

MY_DIRECTORY="/Users/bengal1/dev/Clowder/dagster-clowder/data"

asset_job = define_asset_job("log_file_job", "*")

class FileConfig(Config):
    filename: str


@op
def process_file(context: OpExecutionContext, config: FileConfig):
    context.log.info(config.filename)


@job
def log_file_job():
    process_file()

@sensor(job=asset_job)
def my_directory_sensor():
    for filename in os.listdir(MY_DIRECTORY):
        filepath = os.path.join(MY_DIRECTORY, filename)
        if os.path.isfile(filepath):
            yield RunRequest(
                run_key=filename,
                run_config=RunConfig(
                    ops={"process_file": FileConfig(filename=filename)}
                ),
            )
