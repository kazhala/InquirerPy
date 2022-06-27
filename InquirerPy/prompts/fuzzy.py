"""Module contains the class to create a fuzzy prompt."""
import asyncio
import math
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Tuple,
    Union,
    cast,
)

from pfzy import fuzzy_match
from pfzy.score import fzy_scorer, substr_scorer
from pfzy.types import HAYSTACKS
from prompt_toolkit.application.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.filters.cli import IsDone
from prompt_toolkit.layout.containers import (
    ConditionalContainer,
    FloatContainer,
    HSplit,
    Window,
)
from prompt_toolkit.layout.controls import BufferControl, DummyControl
from prompt_toolkit.layout.dimension import Dimension, LayoutDimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.processors import AfterInput, BeforeInput
from prompt_toolkit.lexers.base import SimpleLexer
from prompt_toolkit.validation import ValidationError
from prompt_toolkit.widgets.base import Frame

from InquirerPy.base import FakeDocument, InquirerPyUIListControl
from InquirerPy.base.list import BaseListPrompt
from InquirerPy.containers.instruction import InstructionWindow
from InquirerPy.containers.message import MessageWindow
from InquirerPy.containers.validation import ValidationFloat
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument
from InquirerPy.separator import Separator
from InquirerPy.utils import (
    InquirerPyDefault,
    InquirerPyKeybindings,
    InquirerPyListChoices,
    InquirerPyMessage,
    InquirerPySessionResult,
    InquirerPyStyle,
    InquirerPyValidate,
    calculate_height,
)

if TYPE_CHECKING:
    from prompt_toolkit.key_binding.key_processor import KeyPressEvent

__all__ = ["FuzzyPrompt"]


class InquirerPyFuzzyControl(InquirerPyUIListControl):
    """An :class:`~prompt_toolkit.layout.UIControl` class that displays a list of choices.

    This only displays the chocies. The actual input buffer will be handled by a separate
    :class:`~prompt_toolkit.layout.BufferControl`.

    Reference the parameter definition in :class:`.FuzzyPrompt`.
    """

    def __init__(
        self,
        choices: InquirerPyListChoices,
        pointer: str,
        marker: str,
        current_text: Callable[[], str],
        max_lines: int,
        session_result: Optional[InquirerPySessionResult],
        multiselect: bool,
        marker_pl: str,
        match_exact: bool,
    ) -> None:
        self._pointer = pointer
        self._marker = marker
        self._marker_pl = marker_pl
        self._current_text = current_text
        self._max_lines = max_lines if max_lines > 0 else 1
        self._scorer = fzy_scorer if not match_exact else substr_scorer
        super().__init__(
            choices=choices,
            default=None,
            session_result=session_result,
            multiselect=multiselect,
        )

    def _format_choices(self) -> None:
        for index, choice in enumerate(self.choices):
            if isinstance(choice["value"], Separator):
                raise InvalidArgument(
                    "fuzzy prompt argument choices should not contain Separator"
                )
            choice["index"] = index
            choice["indices"] = []
        self._filtered_choices = self.choices
        self._first_line = 0
        self._last_line = min(self._max_lines, self.choice_count)
        self._height = self._last_line - self._first_line

    def _get_hover_text(self, choice) -> List[Tuple[str, str]]:
        """Get the current highlighted line of text.

        If in the middle of filtering, loop through the char and color
        indices matched char into style class `class:fuzzy_match`.

        Returns:
            FormattedText in list of tuple format.
        """
        display_choices = []
        display_choices.append(("class:pointer", self._pointer))
        display_choices.append(
            (
                "class:marker",
                self._marker
                if self.choices[choice["index"]]["enabled"]
                else self._marker_pl,
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

        Returns:
            FormattedText in list of tuple format.
        """
        display_choices = []
        display_choices.append(("class:pointer", len(self._pointer) * " "))
        display_choices.append(
            (
                "class:marker",
                self._marker
                if self.choices[choice["index"]]["enabled"]
                else self._marker_pl,
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

        Returns:
            FormattedText in list of tuple format.
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

        Args:
            wait_time: Additional time to wait before filtering the choice.

        Returns:
            Filtered choices.
        """
        if not self._current_text():
            for choice in self.choices:
                choice["indices"] = []
            choices = self.choices
        else:
            await asyncio.sleep(wait_time)
            choices = await fuzzy_match(
                self._current_text(),
                cast(HAYSTACKS, self.choices),
                key="name",
                scorer=self._scorer,
            )
        return choices

    @property
    def selection(self) -> Dict[str, Any]:
        """Override this value since `self.choice` does not indicate the choice displayed.

        `self.filtered_choice` is the up to date choice displayed.

        Returns:
            A dictionary of name and value for the current pointed choice.
        """
        return self._filtered_choices[self.selected_choice_index]

    @property
    def choice_count(self) -> int:
        """int: Filtered choice count."""
        return len(self._filtered_choices)


class FuzzyPrompt(BaseListPrompt):
    """Create a prompt that lists choices while also allowing fuzzy search like fzf.

    A wrapper class around :class:`~prompt_toolkit.application.Application`.

    Fuzzy search using :func:`pfzy.match.fuzzy_match` function.

    Override the default keybindings for up/down as j/k cannot be bind even if `editing_mode` is vim
    due to the input buffer.

    Args:
        message: The question to ask the user.
            Refer to :ref:`pages/dynamic:message` documentation for more details.
        choices: List of choices to display and select.
            Refer to :ref:`pages/dynamic:choices` documentation for more details.
        style: An :class:`InquirerPyStyle` instance.
            Refer to :ref:`Style <pages/style:Alternate Syntax>` documentation for more details.
        vi_mode: Use vim keybinding for the prompt.
            Refer to :ref:`pages/kb:Keybindings` documentation for more details.
        default: Set the default value in the search buffer.
            Different than other list type prompts, the `default` parameter tries to replicate what fzf does and
            add the value in `default` to search buffer so it starts searching immediatelly.
            Refer to :ref:`pages/dynamic:default` documentation for more details.
        qmark: Question mark symbol. Custom symbol that will be displayed infront of the question before its answered.
        amark: Answer mark symbol. Custom symbol that will be displayed infront of the question after its answered.
        pointer: Pointer symbol. Customer symbol that will be used to indicate the current choice selection.
        instruction: Short instruction to display next to the question.
        long_instruction: Long instructions to display at the bottom of the prompt.
        validate: Add validation to user input.
            The main use case for this prompt would be when `multiselect` is True, you can enforce a min/max selection.
            Refer to :ref:`pages/validator:Validator` documentation for more details.
        invalid_message: Error message to display when user input is invalid.
            Refer to :ref:`pages/validator:Validator` documentation for more details.
        transformer: A function which performs additional transformation on the value that gets printed to the terminal.
            Different than `filter` parameter, this is only visual effect and won’t affect the actual value returned by :meth:`~InquirerPy.base.simple.BaseSimplePrompt.execute`.
            Refer to :ref:`pages/dynamic:transformer` documentation for more details.
        filter: A function which performs additional transformation on the result.
            This affects the actual value returned by :meth:`~InquirerPy.base.simple.BaseSimplePrompt.execute`.
            Refer to :ref:`pages/dynamic:filter` documentation for more details.
        height: Preferred height of the prompt.
            Refer to :ref:`pages/height:Height` documentation for more details.
        max_height: Max height of the prompt.
            Refer to :ref:`pages/height:Height` documentation for more details.
        multiselect: Enable multi-selection on choices.
            You can use `validate` parameter to control min/max selections.
            Setting to True will also change the result from a single value to a list of values.
        prompt: Input prompt symbol. Custom symbol to display infront of the input buffer to indicate for input.
        border: Create border around the choice window.
        info: Display choice information similar to fzf --info=inline next to the prompt.
        match_exact: Use exact sub-string match instead of using fzy fuzzy match algorithm.
        exact_symbol: Custom symbol to display in the info section when `info=True`.
        marker: Marker Symbol. Custom symbol to indicate if a choice is selected.
            This will take effects when `multiselect` is True.
        marker_pl: Marker place holder when the choice is not selected.
            This is empty space by default.
        keybindings: Customise the builtin keybindings.
            Refer to :ref:`pages/kb:Keybindings` for more details.
        cycle: Return to top item if hit bottom during navigation or vice versa.
        wrap_lines: Soft wrap question lines when question exceeds the terminal width.
        raise_keyboard_interrupt: Raise the :class:`KeyboardInterrupt` exception when `ctrl-c` is pressed. If false, the result
            will be `None` and the question is skiped.
        mandatory: Indicate if the prompt is mandatory. If True, then the question cannot be skipped.
        mandatory_message: Error message to show when user attempts to skip mandatory prompt.
        session_result: Used internally for :ref:`index:Classic Syntax (PyInquirer)`.

    Examples:
        >>> from InquirerPy import inquirer
        >>> result = inquirer.fuzzy(message="Select one:", choices=[1, 2, 3]).execute()
        >>> print(result)
        1
    """

    def __init__(
        self,
        message: InquirerPyMessage,
        choices: InquirerPyListChoices,
        default: InquirerPyDefault = "",
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        style: Optional[InquirerPyStyle] = None,
        vi_mode: bool = False,
        qmark: str = "?",
        amark: str = "?",
        transformer: Optional[Callable[[Any], Any]] = None,
        filter: Optional[Callable[[Any], Any]] = None,
        instruction: str = "",
        long_instruction: str = "",
        multiselect: bool = False,
        prompt: str = INQUIRERPY_POINTER_SEQUENCE,
        marker: str = INQUIRERPY_POINTER_SEQUENCE,
        marker_pl: str = " ",
        border: bool = False,
        info: bool = True,
        match_exact: bool = False,
        exact_symbol: str = " E",
        height: Optional[Union[str, int]] = None,
        max_height: Optional[Union[str, int]] = None,
        validate: Optional[InquirerPyValidate] = None,
        invalid_message: str = "Invalid input",
        keybindings: Optional[InquirerPyKeybindings] = None,
        cycle: bool = True,
        wrap_lines: bool = True,
        raise_keyboard_interrupt: bool = True,
        mandatory: bool = True,
        mandatory_message: str = "Mandatory prompt",
        session_result: Optional[InquirerPySessionResult] = None,
    ) -> None:
        if not keybindings:
            keybindings = {}
        self._prompt = prompt
        self._info = info
        self._task = None
        self._rendered = False
        self._exact_symbol = exact_symbol

        keybindings = {
            "up": [{"key": "up"}, {"key": "c-p"}],
            "down": [{"key": "down"}, {"key": "c-n"}],
            "toggle": [],
            "toggle-exact": [],
            **keybindings,
        }
        super().__init__(
            message=message,
            style=style,
            border=border,
            vi_mode=vi_mode,
            qmark=qmark,
            amark=amark,
            transformer=transformer,
            filter=filter,
            validate=validate,
            invalid_message=invalid_message,
            multiselect=multiselect,
            instruction=instruction,
            long_instruction=long_instruction,
            keybindings=keybindings,
            cycle=cycle,
            wrap_lines=wrap_lines,
            raise_keyboard_interrupt=raise_keyboard_interrupt,
            mandatory=mandatory,
            mandatory_message=mandatory_message,
            session_result=session_result,
        )
        self.kb_func_lookup = {"toggle-exact": [{"func": self._toggle_exact}]}
        self._default = (
            default
            if not isinstance(default, Callable)
            else cast(Callable, default)(self._result)
        )
        self._height_offset += 1  # search input
        self._dimmension_height, self._dimmension_max_height = calculate_height(
            height, max_height, height_offset=self.height_offset
        )

        self._content_control: InquirerPyFuzzyControl = InquirerPyFuzzyControl(
            choices=choices,
            pointer=pointer,
            marker=marker,
            current_text=self._get_current_text,
            max_lines=self._dimmension_max_height,
            session_result=session_result,
            multiselect=multiselect,
            marker_pl=marker_pl,
            match_exact=match_exact,
        )

        self._buffer = Buffer(on_text_changed=self._on_text_changed)
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
            max=self._dimmension_max_height,
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
            FloatContainer(
                content=HSplit(
                    [
                        MessageWindow(
                            message=self._get_prompt_message,
                            filter=True,
                            wrap_lines=self._wrap_lines,
                            show_cursor=True,
                        ),
                        ConditionalContainer(
                            main_content_window,
                            filter=~IsDone(),
                        ),
                        ConditionalContainer(
                            Window(content=DummyControl()),
                            filter=~IsDone() & self._is_displaying_long_instruction,
                        ),
                        InstructionWindow(
                            message=self._long_instruction,
                            filter=~IsDone() & self._is_displaying_long_instruction,
                            wrap_lines=self._wrap_lines,
                        ),
                    ],
                ),
                floats=[
                    ValidationFloat(
                        invalid_message=self._get_error_message,
                        filter=self._is_invalid & ~IsDone(),
                        wrap_lines=self._wrap_lines,
                        left=0,
                        bottom=self._validation_window_bottom_offset,
                    ),
                ],
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

    def _toggle_exact(self, _, value: Optional[bool] = None) -> None:
        """Toggle matching algorithm.

        Switch between fzy fuzzy match or sub-string exact match.

        Args:
            value: Specify the value to toggle.
        """
        if value is not None:
            self.content_control._scorer = fzy_scorer if not value else substr_scorer
        else:
            self.content_control._scorer = (
                fzy_scorer
                if self.content_control._scorer == substr_scorer
                else substr_scorer
            )

    def _on_rendered(self, _) -> None:
        """Render callable choices and set the buffer default text.

        Setting buffer default text has to be after application is rendered and choice are loaded,
        because `self._filter_choices` will use the event loop from `Application`.
        """
        if self._default:
            default_text = str(self._default)
            self._buffer.text = default_text
            self._buffer.cursor_position = len(default_text)

    def _handle_toggle_all(self, _, value: Optional[bool] = None) -> None:
        """Toggle all choice `enabled` status.

        Args:
            value: Specify the value to toggle.
        """
        if not self._multiselect:
            return
        for choice in self.content_control._filtered_choices:
            raw_choice = self.content_control.choices[choice["index"]]
            if isinstance(raw_choice["value"], Separator):
                continue
            raw_choice["enabled"] = value if value else not raw_choice["enabled"]

    def _generate_after_input(self) -> List[Tuple[str, str]]:
        """Virtual text displayed after the user input."""
        display_message = []
        if self._info:
            display_message.append(("", "  "))
            display_message.append(
                (
                    "class:fuzzy_info",
                    f"{self.content_control.choice_count}/{len(self.content_control.choices)}",
                )
            )
            if self._multiselect:
                display_message.append(
                    ("class:fuzzy_info", f" ({len(self.selected_choices)})")
                )
            if self.content_control._scorer == substr_scorer:
                display_message.append(("class:fuzzy_info", self._exact_symbol))
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

        Returns:
            Desired wait time before running the filter.
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

    def _handle_toggle_choice(self, _) -> None:
        """Handle tab event, alter the `selected` state of the choice."""
        if not self._multiselect:
            return
        current_selected_index = self.content_control.selection["index"]
        self.content_control.choices[current_selected_index][
            "enabled"
        ] = not self.content_control.choices[current_selected_index]["enabled"]

    def _handle_enter(self, event: "KeyPressEvent") -> None:
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
        except ValidationError as e:
            self._set_error(str(e))
        except IndexError:
            self.status["answered"] = True
            self.status["result"] = None if not self._multiselect else []
            event.app.exit(result=None if not self._multiselect else [])

    @property
    def content_control(self) -> InquirerPyFuzzyControl:
        """InquirerPyFuzzyControl: Override for type-hinting."""
        return cast(InquirerPyFuzzyControl, super().content_control)

    @content_control.setter
    def content_control(self, value: InquirerPyFuzzyControl) -> None:
        self._content_control = value

    def _get_current_text(self) -> str:
        """Get current input buffer text."""
        return self._buffer.text
