import asyncio

from InquirerPy import inquirer, prompt_async


async def main():
    questions = [
        {"type": "input", "message": "Name:"},
        {"type": "number", "message": "Number:"},
        {"type": "confirm", "message": "Confirm?"},
    ]
    result = await prompt_async(questions)
    name = await inquirer.text(message="Name:").execute_async()
    number = await inquirer.number(message="Number:").execute_async()
    confirm = await inquirer.confirm(message="Confirm?").execute_async()


if __name__ == "__main__":
    asyncio.run(main())
