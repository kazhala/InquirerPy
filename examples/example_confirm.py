from InquirerPy import prompt, inquirer


def classic():
    questions = [
        {
            "type": "confirm",
            "message": "Proceed?",
            "name": "proceed",
            "default": True,
        },
        {
            "type": "confirm",
            "message": "Require 1 on 1?",
            "when": lambda result: result["proceed"],
        },
        {
            "type": "confirm",
            "message": "Confirm?",
            "when": lambda result: result.get("1", False),
        },
    ]

    result = prompt(questions)


def alternate():
    proceed, service, confirm = False, False, False
    proceed = inquirer.confirm(message="Proceed?", default=True).execute()
    if proceed:
        service = inquirer.confirm(message="Require 1 on 1?").execute()
    if service:
        confirm = inquirer.confirm(message="Confirm?").execute()


alternate()
# classic()
