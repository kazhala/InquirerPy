import boto3

from InquirerPy import prompt
from InquirerPy.validator import PathValidator

client = boto3.client("s3")


class S3:
    def __init__(self):
        self.bucket = None

    def get_bucket(self):
        return [bucket["Name"] for bucket in client.list_buckets()["Buckets"]]

    def walk_s3_bucket(self):
        response = []
        paginator = client.get_paginator("list_objects")
        for result in paginator.paginate(Bucket=self.bucket):
            for file in result["Contents"]:
                response.append(file["Key"])
        return response

    def set_bucket(self, bucket):
        self.bucket = bucket
        return self.bucket


def is_upload(result):
    return result["0"] == "Upload"


s3 = S3()

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
        "choices": s3.get_bucket,
        "filter": s3.set_bucket,
    },
    {
        "message": "Select files to download:",
        "type": "fuzzy",
        "when": lambda _: not is_upload(_),
        "choices": s3.walk_s3_bucket,
        "multiselect": True,
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

result = prompt(questions, vi_mode=True)

# Download or Upload the file based on result ...
