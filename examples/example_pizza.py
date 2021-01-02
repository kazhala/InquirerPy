from InquirerPy import prompt
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.validator import EmptyInputValidator

questions = [
    {
        "message": "Delivery or Takeaway?",
        "type": "list",
        "choices": ["Takeaway", "Delivery"],
    },
    {
        "message": "What's your name?",
        "type": "input",
        "validate": EmptyInputValidator(),
    },
    {
        "message": "What's your address",
        "type": "input",
        "validate": EmptyInputValidator("Address cannot be empty"),
        "when": lambda x: x["0"] == "Delivery",
    },
    {
        "message": "What pizza would you like?",
        "type": "rawlist",
        "choices": [
            "Pepperoni",
            "Hawaii",
            "Simple Cheese",
            "Peri Peri Chicken",
            "Meath Lover",
        ],
        "pointer": INQUIRERPY_POINTER_SEQUENCE,
    },
    {
        "message": "Select toppings:",
        "type": "fuzzy",
        "choices": [
            "Pepperoni",
            "Mushrooms",
            "Sausage",
            "Onions",
            "Bacon",
            "Extra Cheese",
            "Peppers",
            "Black Olives",
            "Chicken",
            "Pineapple",
            "Spinach",
            "Fresh Basil",
            "Ham",
            "Pesto",
            "Beef",
        ],
        "multiselect": True,
    },
    {"message": "Confirm order?", "type": "confirm", "default": False},
]
result = prompt(questions, style={"questionmark": "#ff9d00 bold"}, editing_mode="vim")
