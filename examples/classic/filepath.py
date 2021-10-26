from InquirerPy import prompt
from InquirerPy.validator import PathValidator


def main():
    questions = [
        {
            "type": "filepath",
            "message": "Enter file to upload:",
            "name": "location",
            "default": "~/",
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


if __name__ == "__main__":
    main()
