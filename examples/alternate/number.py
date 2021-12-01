from InquirerPy import inquirer

result = inquirer.number(
    message="hello",
    long_instruction="asfasdfasdfa asdfas",
    raise_keyboard_interrupt=False,
    min_allowed=-10,
    max_allowed=10,
    default="2.7",
    float_allowed=True,
).execute()
