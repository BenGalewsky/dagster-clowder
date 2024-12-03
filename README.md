# Clowder Dataset Loader
This [Dagster](https://dagster.io/) project automates the process of loading datasets into Clowder, a data management system. It scans specified directories for new datasets and triggers jobs to upload them to Clowder.
Features
	•	Automatic scanning of directory structures for new datasets
	•	Sensor-based triggering of dataset upload jobs
	•	Configurable dataset volume paths
	•	Integration with Clowder API for dataset uploads

## Getting started
First, install your Dagster code location as a Python package. By using the --editable flag, pip will install your Python package in ["editable mode"](https://pip.pypa.io/en/latest/topics/local-project-installs/#editable-installs) so that as you develop, local code changes will automatically apply.

```bash
pip install -e ".[dev]"
```

## Environment variables
1.	Set up the following environment variables:
	•	`CLOWDER_URL`: URL of your Clowder instance
	•	`CLOWDER_TOKEN`: Authentication token for Clowder API
	•	`SPACE_ID`: ID of the Clowder space where datasets will be uploaded
	•	`DATASET_DIRECTORY`: Path to the root directory containing datasets

Then, start the Dagster UI web server:

```bash
dagster dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the project.

## Project Structure
The main components of this project are:
	•	`DatasetVolume`: A configurable resource that represents the directory structure of datasets
	•	`file_sensor`: A sensor that detects new datasets and triggers upload jobs
	•	`load_clowder`: A job definition for loading datasets into Clowder

## How It Works
	1.	The `file_sensor` periodically scans the specified dataset directory
	2.	When new datasets are detected, it creates run requests for each dataset
	3.	The `load_clowder` job is triggered for each run request
	4.	Datasets are uploaded to Clowder using the provided API credentials


## ClowderResource
The `ClowderResource` is a configurable resource that handles communication with the Clowder API.
Configuration
	•	`clowder_url`: The base URL of the Clowder instance
	•	`clowder_token`: Authentication token for Clowder API
	•	`space_id`: ID of the Clowder space to use
	•	`timeout`: Request timeout (default: 5 seconds)
	•	`retries`: Number of retries for failed requests (default: 3)
	•	`ssl`: Whether to verify SSL certificates (default: True)
Methods
	•	`_get`: Performs GET requests to the Clowder API
	•	`_post`: Performs POST requests to the Clowder API
	•	`get_or_create_space`: Retrieves or creates a Clowder space
	•	`create_dataset`: Creates a new dataset in Clowder
	•	`add_files_to_dataset`: Adds files to a Clowder dataset

## Clowder Dataset Asset
The `clowder_dataset` asset is responsible for creating datasets and uploading files to Clowder.
Configuration
The asset uses a `DatasetRequest` configuration class with the following fields:
	•	`category`: Category for the dataset
	•	`dataset_title`: Title of the dataset (default: “Test Dataset”)
	•	`files`: List of file paths to upload
Functionality
	1.	Creates a new dataset in Clowder
	2.	Uploads specified files to the created dataset
	3.	Returns metadata about the uploaded files


## Development

### Adding new Python dependencies

You can specify new Python dependencies in `setup.py`.

### Unit testing

Tests are in the `dagster_clowder_tests` directory and you can run tests using `pytest`:

```bash
pytest dagster_clowder_tests
```

### Schedules and sensors

If you want to enable Dagster [Schedules](https://docs.dagster.io/concepts/partitions-schedules-sensors/schedules) or [Sensors](https://docs.dagster.io/concepts/partitions-schedules-sensors/sensors) for your jobs, the [Dagster Daemon](https://docs.dagster.io/deployment/dagster-daemon) process must be running. This is done automatically when you run `dagster dev`.

Once your Dagster Daemon is running, you can start turning on schedules and sensors for your jobs.
