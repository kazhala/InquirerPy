import os

import boto3

from InquirerPy import inquirer
from InquirerPy.validator import PathValidator

client = boto3.client("s3")
os.environ["INQUIRERPY_EDITING_MODE"] = "vim"


def get_bucket():
    return [bucket["Name"] for bucket in client.list_buckets()["Buckets"]]


def walk_s3_bucket(bucket):
    response = []
    paginator = client.get_paginator("list_objects")
    for result in paginator.paginate(Bucket=bucket):
        for file in result["Contents"]:
            response.append(file["Key"])
    return response


action = inquirer.select(
    message="Select an S3 action:", choices=["Upload", "Download"]
).execute()

if action == "Upload":
    file_to_upload = inquirer.filepath(
        message="Enter the filepath to upload:",
        validate=PathValidator(),
        only_files=True,
    ).execute()
    bucket = inquirer.fuzzy(message="Select a bucket:", choices=get_bucket).execute()
else:
    bucket = inquirer.fuzzy(message="Select a bucket:", choices=get_bucket).execute()
    file_to_download = inquirer.fuzzy(
        message="Select files to download:",
        choices=lambda: walk_s3_bucket(bucket),
        multiselect=True,
    ).execute()
    destination = inquirer.filepath(
        message="Enter destination folder:",
        only_directories=True,
        validate=PathValidator(),
    ).execute()

confirm = inquirer.confirm(message="Confirm?").execute()

# Download or Upload the file based on result ...
