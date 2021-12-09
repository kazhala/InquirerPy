import asyncio

from InquirerPy import inquirer


async def main():
    name = await inquirer.text(message="Name:").execute_async()
    number = await inquirer.number(message="Number:").execute_async()
    confirm = await inquirer.confirm(message="Confirm?").execute_async()


if __name__ == "__main__":
    asyncio.run(main())
