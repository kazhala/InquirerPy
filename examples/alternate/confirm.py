from InquirerPy import inquirer


def main():
    proceed, service, confirm = False, False, False
    proceed = inquirer.confirm(message="Proceed?", default=True).execute()
    if proceed:
        service = inquirer.confirm(message="Require 1 on 1?").execute()
    if service:
        confirm = inquirer.confirm(message="Confirm?").execute()


if __name__ == "__main__":
    main()
