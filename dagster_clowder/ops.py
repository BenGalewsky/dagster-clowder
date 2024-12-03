from dagster import op, job, Config, OpExecutionContext


class FileConfig(Config):
    filename: str


@op
def process_file(context: OpExecutionContext, config: FileConfig):
    context.log.info(config.filename)


@job
def log_file_job():
    process_file()
