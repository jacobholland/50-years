import os
import boto3
import io 
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
FILE_LOCATION = os.getenv('FILE_LOCATION', '50-years/src/data/Cancer Data12A.csv')
S3_BUCKET = os.getenv('S3_BUCKET', 'local-bucket')

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# AWS Clients
aws_config = {'region_name': 'eu-west-2', 'endpoint_url': ENDPOINT_URL, 'aws_access_key_id': 'xxx', 'aws_secret_access_key': 'xxx'} if ENVIRONMENT == 'local' else {}
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


def load_api_patents() -> None:
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


def filter_results(data: Any) -> pd.DataFrame:
    """
    Converts the input data to a DataFrame and applies basic filtering logic.
    Returns the cleaned DataFrame.
    """
    try:
        logger.info("Filtering results...")
        if isinstance(data, list):
            df = pd.DataFrame(data)
        elif isinstance(data, dict): 
            if len(data) == 1 and isinstance(list(data.values())[0], list):
                df = pd.DataFrame(list(data.values())[0])
            else:
                df = pd.json_normalize(data)
        else: 
            logger.error("Failed to write data to dataframe, confirm the structure of data")
            raise

        logger.info(f"DataFrame created with shape: {df.shape}")

        filtered_df = df[df['Drugs_and_Chemistry'] == 1]

        logger.info(f"DataFrame filtered: {filtered_df.shape}")

        return filtered_df 

    except Exception as e:
        logger.error(f"Failed to filter results: {e}")
        return pd.DataFrame()
    

def write_df_to_s3(df: pd.DataFrame, bucket: str, key: str) -> bool:
    """
    Writes resulting DataFrame to S3
    """
    try:
        csv_buffer = io.StringIO()
        df.to_csv(csv_buffer, index=False)

        s3_client.put_object(
            Bucket=bucket,
            Key=key,
            Body=csv_buffer.getvalue()
        )

        logger.info(f"Successfully wrote DataFrame to s3://{bucket}/{key}")
        return True

    except Exception as e:
        logger.error(f"Failed to write DataFrame to S3: {e}")
        return False


if __name__ == "__main__":
    try: 
        logger.info(f"Starting in {ENVIRONMENT}")
        if ENVIRONMENT == 'local': 
            data = load_local_file(FILE_LOCATION) 
            result = filter_results(data)
            write_df_to_s3(result, S3_BUCKET, FILE_LOCATION)
        else: 
            # This path should only be expanded post-MVP to programmatically retrieve data
            load_api_patents()
        logger.info("Finished!")

    except Exception: 
        logger.error("Failed to pull data from API endpoint")
