from InquirerPy import inquirer

result = inquirer.number(
    message="hello",
    long_instruction="asfasdfasdfa asdfas",
    raise_keyboard_interrupt=False,
    # float_allowed=True,
).execute()
