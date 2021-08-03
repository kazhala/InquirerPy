"""Contains the content control class `InquirerPyUIControl`."""
from abc import abstractmethod
from typing import Any, Callable, Dict, List, Tuple, Union

from prompt_toolkit.layout.controls import FormattedTextControl

from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.separator import Separator
from InquirerPy.utils import SessionResult


class InquirerPyUIControl(FormattedTextControl):
    """A UIControl class intended to be consumed by `prompt_toolkit` window.

    Dynamically adapt to user input and update formatted text.

    :param choices: List of choices to display as the content.
    :param default: Default value, will impact the cursor position.
    :param session_result: Current session result.
    :param multiselect: Indicate if the current prompt is multiselect enabled.
    """

    def __init__(
        self,
        choices: Union[Callable[[SessionResult], List[Any]], List[Any]],
        default: Any = None,
        session_result: SessionResult = None,
        multiselect: bool = False,
    ) -> None:
        self._session_result = session_result or {}
        self._selected_choice_index: int = 0
        self._choice_func = None
        self._loading = False
        self._raw_choices = []
        self._multiselect = multiselect
        self._default = (
            default
            if not isinstance(default, Callable)
            else default(self._session_result)  # type: ignore
        )
        if isinstance(choices, Callable):
            self._loading = True
            self._choices = []
            self._choice_func = choices
            self._loading = True
        else:
            self._raw_choices = choices
            self._choices = self._get_choices(choices, self._default)  # type: ignore
            self._safety_check()
        self._format_choices()
        super().__init__(self._get_formatted_choices)

    def _retrieve_choices(self) -> None:
        """Retrieve the callable choices and format them.

        Should be called in the `after_render` call in `Application`.
        """
        self._raw_choices = self._choice_func(self._session_result)  # type: ignore
        self.choices = self._get_choices(self._raw_choices, self._default)
        self._loading = False
        self._safety_check()
        self._format_choices()

    def _get_choices(self, choices: List[Any], default: Any) -> List[Dict[str, Any]]:
        """Process the raw user input choices and format it into dictionary.

        :param choices: List of choices to display.
        :param default: The default value, this affect selected_choice_index.
        :return: Formatted choices.
        """
        processed_choices: List[Dict[str, Any]] = []
        try:
            for index, choice in enumerate(choices, start=0):
                if isinstance(choice, dict):
                    if choice["value"] == default:
                        self.selected_choice_index = index
                    processed_choices.append(
                        {
                            "name": str(choice["name"]),
                            "value": choice["value"],
                            "enabled": choice.get("enabled", False)
                            if self._multiselect
                            else False,
                        }
                    )
                elif isinstance(choice, Separator):
                    if self.selected_choice_index == index:
                        self.selected_choice_index = (
                            self.selected_choice_index + 1
                        ) % len(choices)
                    processed_choices.append(
                        {"name": str(choice), "value": choice, "enabled": False}
                    )
                else:
                    if choice == default:
                        self.selected_choice_index = index
                    processed_choices.append(
                        {"name": str(choice), "value": choice, "enabled": False}
                    )
        except KeyError:
            raise RequiredKeyNotFound(
                "dictionary choice require a name key and a value key."
            )
        return processed_choices

    @property
    def selected_choice_index(self) -> int:
        """Get current highlighted index."""
        return self._selected_choice_index

    @selected_choice_index.setter
    def selected_choice_index(self, value) -> None:
        """Set index to highlight."""
        self._selected_choice_index = value

    @property
    def choices(self) -> List[Dict[str, Any]]:
        """Get all processed choices."""
        return self._choices

    @choices.setter
    def choices(self, value) -> None:
        """Set processed choices."""
        self._choices = value

    def _safety_check(self) -> None:
        """Validate choices, check empty or all Separator."""
        if not self.choices:
            raise InvalidArgument("choices cannot be empty.")
        should_proceed: bool = False
        for choice in self.choices:
            if not isinstance(choice["value"], Separator):
                should_proceed = True
                break
        if not should_proceed:
            raise InvalidArgument(
                "choices should contain content other than separator."
            )

    def _get_formatted_choices(self) -> List[Tuple[str, str]]:
        """Get all choices in formatted text format.

        :return: A list of formatted choices.
        """
        display_choices = []

        for index, choice in enumerate(self.choices):
            if index == self.selected_choice_index:
                display_choices += self._get_hover_text(choice)
            else:
                display_choices += self._get_normal_text(choice)
            display_choices.append(("", "\n"))
        if display_choices:
            display_choices.pop()
        return display_choices

    @abstractmethod
    def _format_choices(self) -> None:
        """Perform post processing on the choices.

        Customise the choices after `self._get_choices` call.
        """
        pass

    @abstractmethod
    def _get_hover_text(self, choice) -> List[Tuple[str, str]]:
        """Generate the formatted text for hovered choice.

        :return: List of formatted text.
        """
        pass

    @abstractmethod
    def _get_normal_text(self, choice) -> List[Tuple[str, str]]:
        """Generate the formatted text for non-hovered choices.

        :return: List of formatted text.
        """
        pass

    @property
    def choice_count(self) -> int:
        """Get the choice count.

        :return: The total count of choices.
        """
        return len(self.choices)

    @property
    def selection(self) -> Dict[str, Any]:
        """Get current selection value.

        :return: A dictionary of name and value for the current pointed choice.
        """
        return self.choices[self.selected_choice_index]
