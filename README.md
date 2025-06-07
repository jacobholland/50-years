# 50-Years Patent Webscraper

This project provides a flexible, environment-aware pipeline for loading **local data files (CSV, XML, JSON)** or remote API responses (mocked via placeholder APIs), transforming them with **Pandas**, and writing the result to an **S3 bucket (Localstack by default)** using **DLT** for orchestration and structure.

This project uses (Astral)[https://astral.sh/] for package management (uv) & linting (ruff). 

It mocks cloud services with [localstack](https://github.com/localstack/localstack).

## High Level Architecture
The basic idea is for an MVP we will manually download files from the portal (however, a path for proper API integration has been sketched out to be used in future. At the minute US Citizenship is required for programmatic downloads). This has been setup with Docker to assist with containerisation of this application in future so that it can be properly orchestrated & deployed in the cloud. 

Once files are available locally, an application is setup to read a single file (at the minute it assumes a specific `.csv` file with a specific schema). Although the portal appears to contain a variety of file types (e.g. `.xml`, `.json`).

This data is then written to a pd.DataFrame for in-memory processing (at the minute, it filters on a specific field of potential interest). 

Lastly, the resulting fileset is written to a mock local blob storage (S3) to be used for other services. 

## Getting Started

### 0. Pre-requisites 
- uv 
- Docker
- Manual download of data (example file [here](https://data.uspto.gov/ui/datasets/products/files/MOONSHOT/2016/Cancer%20Data12A.zip)); which looks approximate to the requested "synthetic biology" domain. These files should be staged here: `50-years/src/data/`

### 1. Docker
Setup a mock local cloud environment (AWS) as a datastore to which data can be written 
`docker compose up --build -d` 

### 2. Activate Virtual Environment 
Activate a local virtual environment:
`uv venv`

### 3. Run the script
This will run the `main.py` script 
`uv run src/app/src/main.py`

### 4. Lint
You can lint & standardise files with ruff via
`ruff check --fix` 
