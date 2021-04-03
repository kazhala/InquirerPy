"""Module contains the class to construct fuzzyfinder prompt."""
import asyncio
import math
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from prompt_toolkit.application.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.filters.cli import IsDone
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import Dimension, LayoutDimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.processors import AfterInput, BeforeInput
from prompt_toolkit.lexers.base import SimpleLexer
from prompt_toolkit.validation import ValidationError, Validator
from prompt_toolkit.widgets.base import Frame

from InquirerPy.base import BaseComplexPrompt, FakeDocument, InquirerPyUIControl
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument
from InquirerPy.prompts.fuzzy.fzy import fuzzy_match_py_async
from InquirerPy.separator import Separator
from InquirerPy.utils import InquirerPyStyle, SessionResult, calculate_height


class InquirerPyFuzzyControl(InquirerPyUIControl):
    """A UIControl element intended to be used by `prompt_toolkit` Window class.

    This UIControl is for listing the available choices based on filtering.
    The actual input buffer will be handled by a separate BufferControl.

    :param choices: List of choices to display.
    :param pointer: The pointer symbol.
    :param marker: Marker symbol for the selected choice in the case of multiselect.
    :param current_text: Current buffer text.
    :param max_lines: Maximum height.
    """

    def __init__(
        self,
        choices: Union[Callable[[SessionResult], List[Any]], List[Any]],
        pointer: str,
        marker: str,
        current_text: Callable[[], str],
        max_lines: int,
        session_result: Optional[SessionResult],
    ) -> None:
        self._pointer = pointer
        self._marker = marker
        self._current_text = current_text
        self._max_lines = max_lines if max_lines > 0 else 1
        super().__init__(choices=choices, default=None, session_result=session_result)

    def _format_choices(self) -> None:
        for index, choice in enumerate(self.choices):
            if isinstance(choice["value"], Separator):
                raise InvalidArgument("fuzzy type prompt does not accept Separator.")
            choice["enabled"] = False
            choice["index"] = index
            choice["indices"] = []
        self._filtered_choices = self.choices
        self._first_line = 0
        self._last_line = min(self._max_lines, self.choice_count)
        self._height = self._last_line - self._first_line

    def _get_hover_text(self, choice) -> List[Tuple[str, str]]:
        """Get the current highlighted line of text in `FormattedText`.

        If in the middle of filtering, loop through the char and color
        indices matched char into `class:fuzzy_match`.

        :return: List of formatted text.
        """
        display_choices = []
        display_choices.append(("class:pointer", self._pointer))
        display_choices.append(
            (
                "class:marker",
                self._marker if self.choices[choice["index"]]["enabled"] else " ",
            )
        )
        display_choices.append(("[SetCursorPosition]", ""))
        if not choice["indices"]:
            display_choices.append(("class:pointer", choice["name"]))
        else:
            indices = set(choice["indices"])
            for index, char in enumerate(choice["name"]):
                if index in indices:
                    display_choices.append(("class:fuzzy_match", char))
                else:
                    display_choices.append(("class:pointer", char))
        return display_choices

    def _get_normal_text(self, choice) -> List[Tuple[str, str]]:
        """Get the line of text in `FormattedText`.

        If in the middle of filtering, loop through the char and color
        indices matched char into `class:fuzzy_match`.

        Calculate spaces of pointer to make the choice equally align.

        :return: List of formatted text.
        """
        display_choices = []
        display_choices.append(("class:pointer", len(self._pointer) * " "))
        display_choices.append(
            (
                "class:marker",
                self._marker if self.choices[choice["index"]]["enabled"] else " ",
            )
        )
        if not choice["indices"]:
            display_choices.append(("", choice["name"]))
        else:
            indices = set(choice["indices"])
            for index, char in enumerate(choice["name"]):
                if index in indices:
                    display_choices.append(("class:fuzzy_match", char))
                else:
                    display_choices.append(("", char))
        return display_choices

    def _get_formatted_choices(self) -> List[Tuple[str, str]]:
        """Get all available choices in formatted text format.

        Overriding this method because `self.choice` will be the
        full choice list. Using `self.filtered_choice` to get
        a list of choice based on current_text.

        :return: List of formatted choices.
        """
        display_choices = []
        if self.choice_count == 0:
            self._selected_choice_index = 0
            return display_choices

        if self._selected_choice_index < 0:
            self._selected_choice_index = 0
        elif self._selected_choice_index >= self.choice_count:
            self._selected_choice_index = self.choice_count - 1

        if (self._last_line - self._first_line) < min(self.choice_count, self._height):
            self._last_line = min(self.choice_count, self._height)
            self._first_line = self._last_line - min(self.choice_count, self._height)

        if self._selected_choice_index <= self._first_line:
            self._first_line = self._selected_choice_index
            self._last_line = self._first_line + min(self._height, self.choice_count)
        elif self._selected_choice_index >= self._last_line:
            self._last_line = self._selected_choice_index + 1
            self._first_line = self._last_line - min(self._height, self.choice_count)

        if self._last_line > self.choice_count:
            self._last_line = self.choice_count
            self._first_line = self._last_line - min(self._height, self.choice_count)
        if self._first_line < 0:
            self._first_line = 0
            self._last_line = self._first_line + min(self._height, self.choice_count)

        for index in range(self._first_line, self._last_line):
            if index == self.selected_choice_index:
                display_choices += self._get_hover_text(self._filtered_choices[index])
            else:
                display_choices += self._get_normal_text(self._filtered_choices[index])
            display_choices.append(("", "\n"))
        if display_choices:
            display_choices.pop()
        return display_choices

    async def _filter_choices(self, wait_time: float) -> List[Dict[str, Any]]:
        """Call to filter choices using fzy fuzzy match.

        :param wait_time: Delay time for this task.
        :return: Filtered result.
        """
        if not self._current_text():
            choices = self.choices
        else:
            await asyncio.sleep(wait_time)
            choices = await fuzzy_match_py_async(self._current_text(), self.choices)
        return choices

    @property
    def selection(self) -> Dict[str, Any]:
        """Override this value since `self.choice` does not indicate the choice displayed.

        `self.filtered_choice` is the up to date choice displayed.

        :return: A dictionary of name and value for the current pointed choice
        """
        return self._filtered_choices[self.selected_choice_index]

    @property
    def choice_count(self) -> int:
        """int: Filtered choice count."""
        return len(self._filtered_choices)


class FuzzyPrompt(BaseComplexPrompt):
    """A filter prompt that allows user to input value.

    Filters the result using fuzzy finding. The fuzzy finding logic
    is contains in the file fzy.py which is copied from `vim-clap`
    python provider.

    The Application have mainly 3 layers.
    1. question
    2. input
    3. choices

    The content of choices content_control is bounded by the input buffer content_control
    on_text_changed event.

    Once Enter is pressed, hide both input buffer and choices buffer as well as
    updating the question buffer with user selection.

    Override the default keybindings as j/k cannot be bind even if editing_mode is vim
    due to the input buffer.

    :param message: message to display to the user
    :param choices: list of choices available to select
    :param default: default value to insert into buffer
    :param pointer: pointer symbol
    :param style: style dict to apply
    :param vi_mode: use vi kb for the prompt
    :param qmark: question mark symbol
    :param transformer: transform the result to output, this is only visual effect
    :param filter: a callable to filter the result, updating the user input before returning the result
    :param instruction: instruction to display after the message
    :param multiselect: enable multi selection of the choices
    :param prompt: prompt symbol for buffer
    :param marker: marker symbol for the selected choice in the case of multiselect
    :param border: enable border around the fuzzy prompt
    :param info: display info as virtual text after input
    :param height: preferred height of the choice window
    :param max_height: max height choice window should reach
    :param validate: a callable or Validator instance to validate user selection
    :param invalid_message: message to display when input is invalid
    :param keybindings: custom keybindings to apply
    """

    def __init__(
        self,
        message: Union[str, Callable[[SessionResult], str]],
        choices: Union[Callable[[SessionResult], List[Any]], List[Any]],
        default: Union[str, Callable[[SessionResult], str]] = "",
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        style: InquirerPyStyle = None,
        vi_mode: bool = False,
        qmark: str = "?",
        transformer: Callable[[Any], Any] = None,
        filter: Callable[[Any], Any] = None,
        instruction: str = "",
        multiselect: bool = False,
        prompt: str = INQUIRERPY_POINTER_SEQUENCE,
        marker: str = INQUIRERPY_POINTER_SEQUENCE,
        border: bool = True,
        info: bool = True,
        height: Union[str, int] = None,
        max_height: Union[str, int] = None,
        validate: Union[Callable[[Any], bool], Validator] = None,
        invalid_message: str = "Invalid input",
        keybindings: Dict[str, List[Dict[str, Any]]] = None,
        session_result: SessionResult = None,
    ) -> None:
        if not keybindings:
            keybindings = {}
        self._prompt = prompt
        self._border = border
        self._info = info
        self._task = None
        self._rendered = False
        self._content_control: InquirerPyFuzzyControl

        keybindings = {
            "up": [{"key": "up"}, {"key": "c-p"}],
            "down": [{"key": "down"}, {"key": "c-n"}],
            **keybindings,
        }
        super().__init__(
            message=message,
            style=style,
            vi_mode=vi_mode,
            qmark=qmark,
            transformer=transformer,
            filter=filter,
            validate=validate,
            invalid_message=invalid_message,
            multiselect=multiselect,
            instruction=instruction,
            keybindings=keybindings,
            session_result=session_result,
        )
        self._default = default if not isinstance(default, Callable) else default(self._result)  # type: ignore
        self._dimmension_height, self._dimmension_max_height = calculate_height(
            height, max_height, offset=3 if not self._border else 5
        )

        self._content_control = InquirerPyFuzzyControl(
            choices=choices,
            pointer=pointer,
            marker=marker,
            current_text=self._get_current_text,
            max_lines=self._dimmension_max_height
            if not self._border
            else self._dimmension_max_height - 2,
            session_result=session_result,
        )

        self._buffer = Buffer(on_text_changed=self._on_text_changed)
        message_window = Window(
            height=LayoutDimension.exact(1),
            content=FormattedTextControl(self._get_prompt_message, show_cursor=False),
        )
        input_window = Window(
            height=LayoutDimension.exact(1),
            content=BufferControl(
                self._buffer,
                [
                    AfterInput(self._generate_after_input),
                    BeforeInput(self._generate_before_input),
                ],
                lexer=SimpleLexer("class:input"),
            ),
        )

        choice_height_dimmension = lambda: Dimension(
            max=self._dimmension_max_height
            if not self._border
            else self._dimmension_max_height - 2,
            preferred=self._dimmension_height,
            min=self.content_control._height if self.content_control._height > 0 else 1,
        )
        self.choice_window = Window(
            content=self.content_control,
            height=choice_height_dimmension,
            dont_extend_height=True,
        )

        main_content_window = HSplit([input_window, self.choice_window])
        if self._border:
            main_content_window = Frame(main_content_window)
        self._layout = Layout(
            HSplit(
                [
                    message_window,
                    ConditionalContainer(
                        main_content_window, filter=~IsDone() & ~self._is_loading
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
        )
        self._layout.focus(input_window)

        self._application = Application(
            layout=self._layout,
            style=self._style,
            key_bindings=self._kb,
            editing_mode=self._editing_mode,
            after_render=self._after_render,
        )

    def _after_render(self, application) -> None:
        """Render callable choices and set the buffer default text.

        Setting buffer default text has to be after application is rendered,
        because `self._filter_choices` will use the event loop from `Application`.

        Forcing a check on `self._rendered` as this event is fired up on each
        render, we only want this to fire up once.
        """
        if not self._rendered:
            super()._after_render(application)
            if self._default:
                default_text = str(self._default)
                self._buffer.text = default_text
                self._buffer.cursor_position = len(default_text)

    def _toggle_all(self, value: bool = None) -> None:
        """Toggle all choice `enabled` status.

        :param value: Specify a value to toggle.
        """
        for choice in self.content_control.choices:
            if isinstance(choice["value"], Separator):
                continue
            choice["enabled"] = value if value else not choice["enabled"]

    def _generate_after_input(self) -> List[Tuple[str, str]]:
        """Virtual text displayed after the user input."""
        display_message = []
        if self._info:
            display_message.append(("", "  "))
            display_message.append(
                (
                    "class:fuzzy_info",
                    "%s/%s"
                    % (
                        self.content_control.choice_count,
                        len(self.content_control.choices),
                    ),
                )
            )
            if self._multiselect:
                display_message.append(
                    ("class:fuzzy_info", " (%s)" % len(self.selected_choices))
                )
        return display_message

    def _generate_before_input(self) -> List[Tuple[str, str]]:
        """Display prompt symbol as virtual text before user input."""
        display_message = []
        display_message.append(("class:fuzzy_prompt", "%s " % self._prompt))
        return display_message

    def _filter_callback(self, task):
        """Redraw `self._application` when the filter task is finished."""
        if task.cancelled():
            return
        self.content_control._filtered_choices = task.result()
        self._application.invalidate()

    def _calculate_wait_time(self) -> float:
        """Calculate wait time to smoother the application on big data set.

        Using digit of the choices lengeth to get wait time.
        For digit greater than 6, using formula 2^(digit - 5) * 0.3 to increase the wait_time.

        Still experimenting, require improvement.
        """
        wait_table = {
            2: 0.05,
            3: 0.1,
            4: 0.2,
            5: 0.3,
        }
        digit = 1
        if len(self.content_control.choices) > 0:
            digit = int(math.log10(len(self.content_control.choices))) + 1

        if digit < 2:
            return 0.0
        if digit in wait_table:
            return wait_table[digit]
        return wait_table[5] * (2 ** (digit - 5))

    def _on_text_changed(self, _) -> None:
        """Handle buffer text change event.

        1. Check if there is current task running.
        2. Cancel if already has task, increase wait_time
        3. Create a filtered_choice task in asyncio event loop
        4. Add callback

        1. Run a new filter on all choices.
        2. Re-calculate current selected_choice_index
            if it exceeds the total filtered_choice.
        3. Avoid selected_choice_index less than zero,
            this fix the issue of cursor lose when:
            choice -> empty choice -> choice

        Don't need to create or check asyncio event loop, `prompt_toolkit`
        application already has a event loop running.
        """
        if self._invalid:
            self._invalid = False
        wait_time = self._calculate_wait_time()
        if self._task and not self._task.done():
            self._task.cancel()
        self._task = asyncio.create_task(
            self.content_control._filter_choices(wait_time)
        )
        self._task.add_done_callback(self._filter_callback)

    def _handle_down(self) -> None:
        """Move down."""
        self.content_control.selected_choice_index = (
            self.content_control.selected_choice_index + 1
        ) % self.content_control.choice_count

    def _handle_up(self) -> None:
        """Move up."""
        self.content_control.selected_choice_index = (
            self.content_control.selected_choice_index - 1
        ) % self.content_control.choice_count

    def _toggle_choice(self) -> None:
        """Handle tab event, alter the `selected` state of the choice."""
        current_selected_index = self.content_control.selection["index"]
        self.content_control.choices[current_selected_index][
            "enabled"
        ] = not self.content_control.choices[current_selected_index]["enabled"]

    def _handle_enter(self, event) -> None:
        """Handle enter event.

        Validate the result first.

        In multiselect scenario, if no TAB is entered, then capture the current
        highlighted choice and return the value in a list.
        Otherwise, return all TAB choices as a list.

        In normal scenario, reutrn the current highlighted choice.

        If current UI contains no choice due to filter, return None.
        """
        try:
            fake_document = FakeDocument(self.result_value)
            self._validator.validate(fake_document)  # type: ignore
            if self._multiselect:
                self.status["answered"] = True
                if not self.selected_choices:
                    self.status["result"] = [self.content_control.selection["name"]]
                    event.app.exit(result=[self.content_control.selection["value"]])
                else:
                    self.status["result"] = self.result_name
                    event.app.exit(result=self.result_value)
            else:
                self.status["answered"] = True
                self.status["result"] = self.content_control.selection["name"]
                event.app.exit(result=self.content_control.selection["value"])
        except ValidationError:
            self._invalid = True
        except IndexError:
            self.status["answered"] = True
            self.status["result"] = None if not self._multiselect else []
            event.app.exit(result=None if not self._multiselect else [])

    @property
    def content_control(self) -> InquirerPyFuzzyControl:
        """InquirerPyFuzzyControl: Override for type-hinting."""
        return self._content_control

    def _get_current_text(self) -> str:
        """Get current input buffer text."""
        return self._buffer.text
