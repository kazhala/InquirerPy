"""Contains the content control class :class:`.InquirerPyUIListControl`."""
from abc import abstractmethod
from dataclasses import asdict, dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, cast

from prompt_toolkit.layout.controls import FormattedTextControl

from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.separator import Separator
from InquirerPy.utils import InquirerPyListChoices, InquirerPySessionResult

__all__ = ["Choice", "InquirerPyUIListControl"]


@dataclass
class Choice:
    """Class to create choices for list type prompts.

    A simple dataclass that can be used as an alternate to using :class:`dict`
    when working with choices.

    Args:
        value: The value of the choice when user selects this choice.
        name: The value that should be presented to the user prior/after selection of the choice.
            This value is optional, if not provided, it will fallback to the string representation of `value`.
        enabled: Indicates if the choice should be pre-selected.
            This only has effects when the prompt has `multiselect` enabled.
    """

    value: Any
    name: Optional[str] = None
    enabled: bool = False

    def __post_init__(self):
        """Assign strinify value to name if not present."""
        if self.name is None:
            self.name = str(self.value)


class InquirerPyUIListControl(FormattedTextControl):
    """A base class to create :class:`~prompt_toolkit.layout.UIControl` to display list type contents.

    Args:
        choices(InquirerPyListChoices): List of choices to display as the content.
            Can also be a callable or async callable that returns a list of choices.
        default: Default value, this will affect the cursor position.
        multiselect: Indicate if the current prompt has `multiselect` enabled.
        session_result: Current session result.
    """

    def __init__(
        self,
        choices: InquirerPyListChoices,
        default: Any = None,
        multiselect: bool = False,
        session_result: Optional[InquirerPySessionResult] = None,
    ) -> None:
        self._session_result = session_result or {}
        self._selected_choice_index: int = 0
        self._choice_func = None
        self._multiselect = multiselect
        self._default = (
            default
            if not isinstance(default, Callable)
            else cast(Callable, default)(self._session_result)
        )
        self._raw_choices = (
            choices
            if not isinstance(choices, Callable)
            else cast(Callable, choices)(self._session_result)
        )
        self._choices = self._get_choices(self._raw_choices, self._default)
        self._safety_check()
        self._format_choices()
        super().__init__(self._get_formatted_choices)

    def _get_choices(self, choices: List[Any], default: Any) -> List[Dict[str, Any]]:
        """Process the raw user input choices and format it into dictionary.

        Args:
            choices: List of chices to display.
            default: Default value, this will affect the :attr:`.InquirerPyUIListControl.selected_choice_index`

        Returns:
            List of choices.

        Raises:
            RequiredKeyNotFound: When the provided choice is missing the `name` or `value` key.
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
                elif isinstance(choice, Choice):
                    dict_choice = asdict(choice)
                    if dict_choice["value"] == default:
                        self.selected_choice_index = index
                    if not self._multiselect:
                        dict_choice["enabled"] = False
                    processed_choices.append(dict_choice)
                else:
                    if choice == default:
                        self.selected_choice_index = index
                    processed_choices.append(
                        {"name": str(choice), "value": choice, "enabled": False}
                    )
        except KeyError:
            raise RequiredKeyNotFound(
                "dictionary type of choice require a 'name' key and a 'value' key"
            )
        return processed_choices

    @property
    def selected_choice_index(self) -> int:
        """int: Current highlighted index."""
        return self._selected_choice_index

    @selected_choice_index.setter
    def selected_choice_index(self, value: int) -> None:
        self._selected_choice_index = value

    @property
    def choices(self) -> List[Dict[str, Any]]:
        """List[Dict[str, Any]]: Get all processed choices."""
        return self._choices

    @choices.setter
    def choices(self, value: List[Dict[str, Any]]) -> None:
        self._choices = value

    def _safety_check(self) -> None:
        """Validate processed choices.

        Check if the choices are empty or if it only contains :class:`~InquirerPy.separator.Separator`.
        """
        if not self.choices:
            raise InvalidArgument("argument choices cannot be empty")
        should_proceed: bool = False
        for choice in self.choices:
            if not isinstance(choice["value"], Separator):
                should_proceed = True
                break
        if not should_proceed:
            raise InvalidArgument(
                "argument choices should contain choices other than separator"
            )

    def _get_formatted_choices(self) -> List[Tuple[str, str]]:
        """Get all choices in formatted text format.

        Returns:
            List of choices in formatted text form.
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

    def _format_choices(self) -> None:
        """Perform post processing on the choices.

        Additional customisation to the choices after :meth:`.InquirerPyUIListControl._get_choices` call.
        """
        pass

    @abstractmethod
    def _get_hover_text(self, choice) -> List[Tuple[str, str]]:
        """Generate the formatted text for hovered choice.

        Returns:
            Formatted text in list of tuple format.
        """
        pass

    @abstractmethod
    def _get_normal_text(self, choice) -> List[Tuple[str, str]]:
        """Generate the formatted text for non-hovered choices.

        Returns:
            Formatted text in list of tuple format.
        """
        pass

    @property
    def choice_count(self) -> int:
        """int: Total count of choices."""
        return len(self.choices)

    @property
    def selection(self) -> Dict[str, Any]:
        """Dict[str, Any]: Current selected choice."""
        return self.choices[self.selected_choice_index]

    @property
    def loading(self) -> bool:
        """bool: Indicate if the content control is loading."""
        return self._loading

    @loading.setter
    def loading(self, value: bool) -> None:
        self._loading = value
