from pathlib import Path

from InquirerPy import prompt, inquirer
from InquirerPy.validator import PathValidator


def classic():
    questions = [
        {
            "type": "filepath",
            "message": "Enter file to upload:",
            "name": "location",
            "default": str(Path.cwd()),
            "validate": PathValidator(is_file=True, message="Input is not a file"),
            "only_files": True,
        },
        {
            "type": "filepath",
            "message": "Enter path to download:",
            "validate": PathValidator(is_dir=True, message="Input is not a directory"),
            "name": "destination",
            "only_directories": True,
        },
    ]

    result = prompt(questions)


def alternate():
    src_path = inquirer.filepath(
        message="Enter file to upload:",
        default=str(Path.cwd()),
        validate=PathValidator(is_file=True, message="Input is not a file"),
        only_files=True,
    ).execute()
    dest_path = inquirer.filepath(
        message="Enter path to download:",
        validate=PathValidator(is_dir=True, message="Input is not a directory"),
        only_directories=True,
    ).execute()


alternate()
# classic()
