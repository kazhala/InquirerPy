import os

from InquirerPy import inquirer
from InquirerPy.validator import PathValidator


def main():
    home_path = "~/" if os.name == "posix" else "C:\\"
    src_path = inquirer.filepath(
        message="Enter file to upload:",
        default=home_path,
        validate=PathValidator(is_file=True, message="Input is not a file"),
        only_files=True,
    ).execute()
    dest_path = inquirer.filepath(
        message="Enter path to download:",
        validate=PathValidator(is_dir=True, message="Input is not a directory"),
        only_directories=True,
    ).execute()


if __name__ == "__main__":
    main()
