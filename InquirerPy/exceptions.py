"""Module contains exceptions dedicated to InquirerPy."""


class InvalidArgumentType(Exception):
    """Invalid parameter type."""

    def __init__(self, message="Invalid argument type, double check the type."):
        self.message = message
        super().__init__(self.message)


class RequiredKeyNotFound(Exception):
    """Required keys for question is not present."""

    pass
