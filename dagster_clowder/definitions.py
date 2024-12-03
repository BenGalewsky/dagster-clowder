from dagster import ConfigurableResource, Definitions, Enum, load_assets_from_modules, sensor, SensorResult  # type: ignore
from dagster import op, job, Config, OpExecutionContext, RunRequest, RunConfig  # type: ignore
from dagster import EnvVar, define_asset_job, RunConfig
import os
from dagster_clowder import assets
from dagster_clowder.assets import DatasetRequest, clowder_dataset, ClowderResource  # type: ignore
from pathlib import Path

# Define a resource representing a dataset volume with a directory path
class DatasetVolume(ConfigurableResource):
    directory_path: str = "/Users/bengal1/dev/Clowder/dagster-clowder/data"

    def scan_leaf_directories(self):
        # Assume that the root directory defines the category these datasets belong to
        # and the leaf directories are the datasets themselves
        root_dir = Path(self.directory_path)
        for category in root_dir.iterdir():
            for dirpath, dirnames, filenames in os.walk(category):
                if not dirnames:  # This is a leaf directory (no subdirectories)
                    yield DatasetRequest(
                        category = category.name,
                        dataset_title = os.path.basename(dirpath),
                        files=[os.path.join(dirpath, file) for file in filenames])


# Define a job to load Clowder datasets
load_clowder = define_asset_job(
    "load_clowder", "clowder_dataset")

# Define a sensor that triggers the job based on new files in dataset directories
@sensor(job=load_clowder, required_resource_keys={"dataset_volume"})
def file_sensor(context):
    run_requests = []
    directory_source = context.resources.dataset_volume

    for dataset in directory_source.scan_leaf_directories():
        run_requests.append(
            RunRequest(
                run_key=f"clowder_dataset_{dataset.category}_{dataset.dataset_title}",
                run_config=RunConfig(
                    ops={
                        "clowder_dataset": DatasetRequest(
                            category=dataset.category,
                            dataset_title=dataset.dataset_title, files=dataset.files)
                    }
                )
            )
        )

    context.log.info(f"Sensor found {len(run_requests)} datasets")
    context.log.info(f"Sensor requests: {run_requests}")
    return SensorResult(run_requests=run_requests)

all_assets = load_assets_from_modules([assets])
all_sensor_defs = [file_sensor]

defs = Definitions(
    assets=all_assets,
    sensors=all_sensor_defs,
    jobs = [load_clowder],
    resources={"clowder":
        ClowderResource(
            clowder_url=EnvVar("CLOWDER_URL"),
            clowder_token=EnvVar("CLOWDER_TOKEN"),
            space_id=EnvVar("SPACE_ID")),
        "dataset_volume": DatasetVolume(
            directory_path=EnvVar("DATASET_DIRECTORY"))
    },
)
