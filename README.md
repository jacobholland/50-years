# 50-Years Patent Webscraper

This project provides a flexible, environment-aware pipeline for loading **local data files (CSV, XML, JSON)** or remote API responses (mocked via placeholder APIs), transforming them with **Pandas**, and writing the result to an **S3 bucket (Localstack by default)** using **DLT** for orchestration and structure.

This project uses (Astral)[https://astral.sh/] for package management (uv) & linting (ruff). 

It mocks cloud services with [localstack](https://github.com/localstack/localstack)

---

## Features

- 🔄 Load files from local disk (`.csv`, `.json`, `.xml`)
- 🔌 Alternative mode to ingest from a REST API (using `dlt.sources.rest_api`)
- 🧹 Basic filtering of loaded data using `pandas`
- ☁️ Output to **S3 bucket** (local or cloud)
- 🐳 Compatible with **Localstack** for local AWS simulation

---

## Getting Started

### 0. Pre-requisites 
- uv 
- Docker


### 1. Docker
Setup a mock local cloud environment (AWS) as a datastore to which data can be written 
`docker compose up --build -d` 

### 2. Activate Virtual Environment 
Activate a local virtual environment:
`uv venv`



`uv run src/app/src/main.py`

`ruff check --fix`
