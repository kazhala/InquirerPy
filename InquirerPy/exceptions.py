"""Module contains exceptions that will be raised by `InquirerPy`."""


class InvalidArgument(Exception):
    """Provided argument is invalid.

    Args:
        message: Exception message.
    """

    def __init__(self, message: str = "invalid argument"):
        self._message = message
        super().__init__(self._message)


class RequiredKeyNotFound(Exception):
    """Missing required keys in dictionary.

    Args:
        message: Exception message.
    """

    def __init__(self, message="required key not found"):
        self.message = message
        super().__init__(self.message)
