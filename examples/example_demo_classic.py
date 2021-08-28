# NOTE: Following example requires boto3 package.
import boto3

from InquirerPy import prompt
from InquirerPy.exceptions import InvalidArgument
from InquirerPy.validator import PathValidator

client = boto3.client("s3")


def get_bucket(_):
    return [bucket["Name"] for bucket in client.list_buckets()["Buckets"]]


def walk_s3_bucket(result):
    response = []
    paginator = client.get_paginator("list_objects")
    for result in paginator.paginate(Bucket=result["bucket"]):
        for file in result["Contents"]:
            response.append(file["Key"])
    return response


def is_upload(result):
    return result[0] == "Upload"


questions = [
    {
        "message": "Select an S3 action:",
        "type": "list",
        "choices": ["Upload", "Download"],
    },
    {
        "message": "Enter the filepath to upload:",
        "type": "filepath",
        "when": is_upload,
        "validate": PathValidator(),
        "only_files": True,
    },
    {
        "message": "Select a bucket:",
        "type": "fuzzy",
        "choices": get_bucket,
        "name": "bucket",
        "spinner_enable": True,
    },
    {
        "message": "Select files to download:",
        "type": "fuzzy",
        "when": lambda _: not is_upload(_),
        "choices": walk_s3_bucket,
        "multiselect": True,
        "spinner_enable": True,
    },
    {
        "message": "Enter destination folder:",
        "type": "filepath",
        "when": lambda _: not is_upload(_),
        "only_directories": True,
        "validate": PathValidator(),
    },
    {"message": "Confirm?", "type": "confirm", "default": False},
]

try:
    result = prompt(questions, vi_mode=True)
except InvalidArgument:
    print("No available choices")

# Download or Upload the file based on result ...
