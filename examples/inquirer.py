from InquirerPy import inquirer
from InquirerPy.validator import NumberValidator

age = inquirer.text(
    message="Enter your age:",
    validate=NumberValidator(),
    default="18",
    filter=lambda result: int(result),
    transformer=lambda result: "Adult" if int(result) >= 18 else "Youth",
).execute()

drinks = ["Soda", "Cidr", "Water", "Milk"] if age < 18 else ["Wine", "Beer"]

drink = inquirer.rawlist(
    message="What drinks would you like to buy:", default=2, choices=drinks
).execute()

if drink in {"Wine", "Beer"}:
    bag = inquirer.select(
        message="Would you like a bag:", choices=["Yes", "No"]
    ).execute()

confirm = inquirer.confirm(message="Confirm?", default=True).execute()
