#!/bin/bash

echo "setting environment variables..."
# Set local variables
export AWS_ENDPOINT_URL=http://localhost:4566
export AWS_REGION=eu-west-2
export ENVIRONMENT=local

echo "configuring aws cli..."
# Configure the AWS CLI profile to default to local aws setup
aws configure set aws_access_key_id "xxx"
aws configure set aws_secret_access_key "xxx"
aws configure set default.region "$AWS_REGION"
aws configure set endpoint-url "$AWS_ENDPOINT_URL"

echo "creating buckets..."
aws s3api create-bucket \
    --bucket "$ENVIRONMENT-bucket" \
    --region "$AWS_REGION" \
    --create-bucket-configuration LocationConstraint="$AWS_REGION"

echo "done!"