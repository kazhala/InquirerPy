"""Contains the content control class :class:`.InquirerPyUIListControl`."""
import inspect
from abc import abstractmethod
from typing import Any, Awaitable, Callable, Dict, List, Tuple, cast

from prompt_toolkit.layout.controls import FormattedTextControl

from InquirerPy.exceptions import InvalidArgument, RequiredKeyNotFound
from InquirerPy.separator import Separator
from InquirerPy.utils import ListChoices, SessionResult, transform_async


class InquirerPyUIListControl(FormattedTextControl):
    """A base class to create :class:`~prompt_toolkit.layout.UIControl` to display list type contents.

    Args:
        choices(ListChoices): List of choices to display as the content.
            Can also be a callable or async callable that returns a list of choices.
        default: Default value, this will affect the cursor position.
        multiselect: Indicate if the current prompt has `multiselect` enabled.
        session_result: Current session result.
    """

    def __init__(
        self,
        choices: ListChoices,
        default: Any = None,
        multiselect: bool = False,
        session_result: SessionResult = None,
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
            else cast(Callable, default)(self._session_result)
        )
        if isinstance(choices, Callable):
            self._choices = []
            self._choice_func = (
                choices
                if inspect.iscoroutinefunction(choices)
                else transform_async(cast(Callable, choices))
            )
            self._loading = True
        else:
            self._raw_choices = choices
            self._choices = self._get_choices(cast(List, choices), self._default)
            self._safety_check()
        self._format_choices()
        super().__init__(self._get_formatted_choices)

    async def retrieve_choices(self) -> None:
        """Retrieve the callable choices and format them.

        Should be called in the :meth:`~InquirerPy.base.complex.BaseComplexPrompt._on_rendered` method.

        Examples:
            >>> import asyncio
            >>> asyncio.create_task(self.retrieve_choices())
        """
        self._raw_choices = await cast(
            Callable[..., Awaitable[Any]], self._choice_func
        )(self._session_result)
        self.choices = self._get_choices(self._raw_choices, self._default)
        self._loading = False
        self._safety_check()
        self._format_choices()

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
                "argument choices should contain content other than separator"
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
