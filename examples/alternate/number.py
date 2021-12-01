from InquirerPy import inquirer
from InquirerPy.validator import EmptyInputValidator

result = inquirer.number(
    message="hello",
    long_instruction="asfasdfasdfa asdfas",
    raise_keyboard_interrupt=False,
    min_allowed=-10,
    max_allowed=10,
    default="2.7",
    float_allowed=True,
    validate=EmptyInputValidator(),
).execute()
