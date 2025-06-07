import os
import boto3
import logging
import dlt
import xmltodict
import json 
import pandas as pd 
from typing import Any, Optional
from dlt.sources.rest_api import (
    RESTAPIConfig,
    rest_api_resources,
)


# Environment Variables
ENVIRONMENT = os.getenv('ENVIRONMENT', 'local')
ENDPOINT_URL = os.getenv('ENDPOINT_URL', 'http://localhost:4566')
FILE_LOCATION = os.getenv('FILE_LOCATION', '50-years/src/data/apc250606.xml')

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS Clients
aws_config = (
	{'region_name': 'eu-west-2', 'endpoint_url': ENDPOINT_URL}
	if ENVIRONMENT == 'local'
	else {}
)
s3_client = boto3.client('s3', **aws_config)


def load_local_file(file_location: str) -> dict:
    """
    Load and parse a local file (XML, CSV, or JSON), returning the content as a dictionary or list of dicts.
    """
    try:
        _, ext = os.path.splitext(file_location)
        ext = ext.lower()

        if ext == '.xml':
            with open(file_location, 'r', encoding='utf-8') as f:
                return xmltodict.parse(f.read())

        elif ext == '.csv':
            df = pd.read_csv(file_location)
            return df.to_dict(orient="records")

        elif ext == '.json':
            with open(file_location, 'r', encoding='utf-8') as f:
                return json.load(f)

        else:
            raise ValueError(f"Unsupported file type: {ext}")

    except Exception as e:
        return {"error": str(e)}



@dlt.source(name="api_patents")
def load_patent_api_source(
    base_url: str = "https://jsonplaceholder.typicode.com/",
    access_token: Optional[str] = dlt.secrets.value
    ) -> Any:
    """
    The base_url should be set to below, provided the user is US-based & has a relevant API Key
    https://api.uspto.gov/api/v1/datasets/products/search?latest=true
    """
    config: RESTAPIConfig = {
        "client": {
            "base_url": base_url,
            # we add an auth config if the auth token is present
            "auth": (
                {
                    "type": "bearer",
                    "token": access_token,
                }
                if access_token
                else None
            ),
        },
        # The default configuration for all resources and their endpoints
        "resource_defaults": {
            "primary_key": "id",
            "write_disposition": "merge",
            "endpoint": {
                "params": {
                    "per_page": 100,
                },
            },
        },
        "resources": [
            "posts"
        ],
    }

    yield from rest_api_resources(config)


def load_api_patents():
    """
    This invokes the API pipeline for production, at the minute this should only be used for testing the 
    pipeline & not necessarily assume the schema or data contents
    """

    try: 
        pipeline = dlt.pipeline(
            pipeline_name="rest_api_patents",
            destination='duckdb',
            dataset_name="patents",
        )

        load_info = pipeline.run(load_patent_api_source())

        logger.info(f"Load info: {load_info}")

    except Exception as e: 
        logger.error(f"Failed to load patents data: {e}")


if __name__ == "__main__":
    try: 
        logger.info(f"Starting in {ENVIRONMENT}")
        data = load_local_file(FILE_LOCATION) if ENVIRONMENT == 'local' else load_api_patents()
        logger.info("Finished!")

    except Exception: 
        logger.error("Failed to pull data from API endpoint")
