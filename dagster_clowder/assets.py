
from dagster import AssetExecutionContext, Output, asset, op, job, Config, OpExecutionContext, \
        AssetMaterialization, AssetKey, MetadataValue, sensor, SensorResult, RunRequest, RunConfig, \
        MaterializeResult, ConfigurableResource, AssetCheckResult
import os
import json
import requests
from logging import Logger
from typing import Any, ClassVar
from requests_toolbelt.multipart.encoder import MultipartEncoder

class DatasetRequest(Config):
    category: str
    dataset_title: str = "Test Dataset"
    files: list[str]  =[
        "/home/clowder/campuscluster/data/0_Imaging/052324/052324P_001.txt",
        "/home/clowder/campuscluster/data/0_Imaging/052324/052324P_002.txt",]

class ClowderResource(ConfigurableResource):
    clowder_url: str
    clowder_token: str
    space_id: str
    timeout: ClassVar[int] = 5
    retries: ClassVar[int] = 3
    ssl: ClassVar[bool] = True

    def _get(self, path:str, log: Logger)->dict[str, Any]:
        url = '%s/api/%s' % (self.clowder_url, path.lstrip('/'))
        params = dict()
        params['key'] = self.clowder_token
        attempt = 0
        while True:
            try:
                response = requests.get(url, params=params,
                                        timeout=self.timeout, verify=self.ssl)
                response.raise_for_status()
                return response.json()
            except requests.HTTPError as e:
                attempt += 1
                if attempt > self.retries:
                    log.exception("Error calling GET url %s: %s" % (url, str(e)))
                    raise e
                else:
                    log.debug("Error calling GET url %s: %s" % (url, str(e)))

    def _post(self, path:str, data: dict[str, Any], log: Logger)->dict[str, str]:
        url = '%s/api/%s' % (self.clowder_url, path.lstrip('/'))
        params = dict()
        params['key'] = self.clowder_token
        attempt = 0
        while True:
            try:
                response = requests.post(url, params=params, json=data,
                                        timeout=self.timeout, verify=self.ssl)
                response.raise_for_status()
                return response.json()
            except requests.HTTPError as e:
                attempt += 1
                if attempt > self.retries:
                    log.exception("Error calling POST url %s: %s" % (url, str(e)))
                    raise e
                else:
                    log.debug("Will retry calling POST url %s: %s" % (url, str(e)))

    def get_or_create_space(self, space_name: str, log: Logger):
        space_list = self._get('spaces', log)
        space = [s for s in space_list if s['name'] == space_name]
        if len(space) == 1:
            return space[0]['id']
        else:
            log.info(f"Creating space: {space_name}")
            data = {
                'name': space_name,
                'description': f"Created by Dagster"
            }
            result = self._post('spaces', data=data, log=log)
            space_id = result['id']
            log.info(f"Created space: {space_id}")
            return space_id

        log.info(f"Found spaces: {space}")

    def create_dataset(self, category: str, dataset_title: str, log: Logger):
        space_id = self.get_or_create_space(category, log)
        data = {'description': f"Imported as part of {category}",
            'name': dataset_title,
            'space': [space_id]}
        log.info(f"Creating dataset: {json.dumps(data)}")

        result = self._post(f'datasets/createempty',
            data=data,
            log=log)

        dataset_id = result['id']
        log.info(f"Created dataset: {dataset_id}")
        return dataset_id


    def add_files_to_dataset(self, category: str, dataset_title: str, filenames: list[str], log: Logger):
        dataset_id = self.create_dataset(category, dataset_title, log)

        url = f'{self.clowder_url}/api/uploadToDataset/{dataset_id}?extract=true'
        params = {'key': self.clowder_token}

        m = MultipartEncoder([('file', f'{{"path": "{filename}"}}') for filename in filenames])

        log.info(f"Uploading file to dataset: {url}")

        response = requests.post(url, data=m, params=params,
                                    headers={'Content-Type': m.content_type},
                                    timeout=self.timeout, verify=self.ssl)
        response.raise_for_status()
        log.info(f"Uploaded file to dataset: {response.status_code}")
        if response.text == "No files uploaded":
            log.error(f"Error uploading file to dataset: {response.text}")
            raise Exception(f"Error uploading file to dataset: {response.text}")
        return response.json()


@asset
def clowder_dataset(context: AssetExecutionContext,
    config: DatasetRequest,
    clowder: ClowderResource) -> MaterializeResult:

    context.log.info(f"Processing files: {config.files}")
    response = clowder.add_files_to_dataset(config.category, config.dataset_title, config.files, context.log)

    # If single file was sent, Clowder will return a single id
    if "id" in response:
        metadata={
            "num_records": 1,
            "files": {
                "filename": config.files[0],
                "file_id": response['id']
            }
        }
    else:
        metadata={
            "num_records": 1,
            "files": [{
                "filename": r['name'],
                "file_id": r['id']
            } for r in response['ids']]
        }

    # Return the AssetMaterialization to record that the asset was materialized
    return MaterializeResult(
        metadata=metadata
    )
