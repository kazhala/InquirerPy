"""Contains the base class for all list type prompts."""
import shutil
from typing import Any, Callable, Dict, List, Tuple, Union

from prompt_toolkit.application import Application
from prompt_toolkit.filters import IsDone
from prompt_toolkit.filters.base import FilterOrBool
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension, LayoutDimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.validation import ValidationError, Validator

from InquirerPy.base.complex import BaseComplexPrompt, FakeDocument
from InquirerPy.separator import Separator
from InquirerPy.utils import InquirerPyStyle, SessionResult, calculate_height


class BaseListPrompt(BaseComplexPrompt):
    """A base class to create a complex prompt using `prompt_toolkit` Application.

    Consists of 2 horizontally splitted Window with one being the question and the second
    window responsible to dynamically generate the content.

    Upon entering the answer, update the first window's formatted text.

    :param message: The question to display to the user.
    :param style: Style to apply to the prompt.
    :param vi_mode: Use vi kb for the prompt.
    :param qmark: The custom symbol to display infront of the question before its answered.
    :param amark: THe custom symbol to display infront of the question after its answered.
    :param instruction: Instruction to display after the question message.
    :param transformer: A callable to transform the result, this is visual effect only.
    :param filter: A callable to filter the result, updating the user input before returning the result.
    :param height: The preferred height of the choice window.
    :param max_height: Max height choice window should reach.
    :param validate: A callable or Validator instance to validate user selection.
    :param invalid_message: Message to display when input is invalid.
    :param multiselect: Enable multiselect mode.
    :param keybindings: Custom keybindings to apply.
    :param cycle: Return to top item if hit bottom or vice versa.
    :param show_cursor: Display cursor at the end of the prompt.
    :param wrap_lines: Soft wrap question lines when question exceeds the terminal width.
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        qmark: str = "?",
        amark: str = "?",
        instruction: str = "",
        transformer: Callable[[Any], Any] = None,
        filter: Callable[[Any], Any] = None,
        height: Union[int, str] = None,
        max_height: Union[int, str] = None,
        validate: Union[Callable[[Any], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        multiselect: bool = False,
        keybindings: Dict[str, List[Dict[str, Union[str, FilterOrBool]]]] = None,
        show_cursor: bool = True,
        cycle: bool = True,
        wrap_lines: bool = True,
        session_result: SessionResult = None,
    ) -> None:
        """Initialise the Application with Layout and keybindings."""
        super().__init__(
            message=message,
            style=style,
            vi_mode=vi_mode,
            qmark=qmark,
            amark=amark,
            transformer=transformer,
            filter=filter,
            invalid_message=invalid_message,
            validate=validate,
            multiselect=multiselect,
            instruction=instruction,
            keybindings=keybindings,
            cycle=cycle,
            wrap_lines=wrap_lines,
            session_result=session_result,
        )
        self._show_cursor = show_cursor
        self._dimmension_height, self._dimmension_max_height = calculate_height(
            height,
            max_height,
            wrap_lines_offset=self.wrap_lines_offset,
        )

        self.layout = HSplit(
            [
                Window(
                    height=LayoutDimension.exact(1) if not self._wrap_lines else None,
                    content=FormattedTextControl(
                        self._get_prompt_message_with_cursor
                        if self._show_cursor
                        else self._get_prompt_message,
                        show_cursor=self._show_cursor,
                    ),
                    wrap_lines=self._wrap_lines,
                    dont_extend_height=True,
                ),
                ConditionalContainer(
                    Window(
                        content=self.content_control,
                        height=Dimension(
                            max=self._dimmension_max_height,
                            preferred=self._dimmension_height,
                        ),
                        dont_extend_height=True,
                    ),
                    filter=~IsDone() & ~self._is_loading,
                ),
                ConditionalContainer(
                    Window(FormattedTextControl([("", "")])),
                    filter=~IsDone(),  # force validation bar to stay bottom
                ),
                ConditionalContainer(
                    Window(
                        FormattedTextControl(
                            [
                                (
                                    "class:validation-toolbar",
                                    self._invalid_message,
                                )
                            ]
                        ),
                        dont_extend_height=True,
                    ),
                    filter=self._is_invalid & ~IsDone(),
                ),
            ]
        )

        self.application = Application(
            layout=Layout(self.layout),
            style=self._style,
            key_bindings=self._kb,
            after_render=self._after_render,
        )

    def _get_prompt_message_with_cursor(self) -> List[Tuple[str, str]]:
        """Obtain the prompt message to display.

        Introduced a new method instead of using the `_get_prompt_message`
        due to `expand` and `rawlist` make changes after calling `super()._get_prompt_message()`.

        This ensures that cursor is always at the end of the window no matter
        when the changes is made to the `_get_prompt_message`.
        """
        message = self._get_prompt_message()
        message.append(("[SetCursorPosition]", ""))
        message.append(("", " "))  # [SetCursorPosition] require char behind it
        return message

    def _toggle_choice(self) -> None:
        """Toggle the `enabled` status of the choice."""
        self.content_control.selection["enabled"] = not self.content_control.selection[
            "enabled"
        ]

    def _toggle_all(self, value: bool = None) -> None:
        """Toggle all choice `enabled` status.

        :param value: Sepcify a value to toggle.
        """
        for choice in self.content_control.choices:
            if isinstance(choice["value"], Separator):
                continue
            choice["enabled"] = value if value else not choice["enabled"]

    def _handle_up(self) -> None:
        """Handle the event when user attempt to move up."""
        while True:
            cap = super()._handle_up()
            if not isinstance(self.content_control.selection["value"], Separator):
                break
            else:
                if cap and not self._cycle:
                    self._handle_down()
                    break

    def _handle_down(self) -> None:
        """Handle the event when user attempt to move down."""
        while True:
            cap = super()._handle_down()
            if not isinstance(self.content_control.selection["value"], Separator):
                break
            else:
                if cap and not self._cycle:
                    self._handle_up()
                    break

    def _handle_enter(self, event) -> None:
        """Handle the event when user hit Enter key.

        * Set the state to answered for an update to the prompt display.
        * Set the result to user selected choice's name for display purpose.
        * Let the app exit with the user selected choice's value and return the actual value back to resolver.

        In multiselect scenario, if nothing is selected, return the current highlighted choice.
        """
        try:
            fake_document = FakeDocument(self.result_value)
            self._validator.validate(fake_document)  # type: ignore
        except ValidationError:
            self._invalid = True
        else:
            self.status["answered"] = True
            if self._multiselect and not self.selected_choices:
                self.status["result"] = [self.content_control.selection["name"]]
                event.app.exit(result=[self.content_control.selection["value"]])
            else:
                self.status["result"] = self.result_name
                event.app.exit(result=self.result_value)

    @property
    def wrap_lines_offset(self) -> int:
        """Get extra offset due to line wrapping.

        Overriding it to count the cursor as well.

        :return: Extra offset.
        """
        if not self._wrap_lines:
            return 0
        total_message_length = self.total_message_length
        if self._show_cursor:
            total_message_length += 1
        term_width, _ = shutil.get_terminal_size()
        return total_message_length // term_width
