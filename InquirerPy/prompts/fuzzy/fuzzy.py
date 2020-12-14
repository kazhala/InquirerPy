"""Module contains the class to construct fuzzyfinder prompt."""
from typing import Any, Callable, Dict, List, Literal, Tuple

from prompt_toolkit.application.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.filters.base import Condition
from prompt_toolkit.filters.cli import IsDone
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import LayoutDimension
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.processors import AfterInput, BeforeInput
from prompt_toolkit.widgets.base import Frame

from InquirerPy.base import BaseSimplePrompt, InquirerPyUIControl
from InquirerPy.enum import INQUIRERPY_POINTER_SEQUENCE
from InquirerPy.exceptions import InvalidArgument
from InquirerPy.prompts.fuzzy.fzy import fuzzy_match_py
from InquirerPy.separator import Separator


class InquirerPyFuzzyControl(InquirerPyUIControl):
    """A UIControl element intended to be used by `prompt_toolkit` Window class.

    This UIControl is for lisint the available choices based on filtering.

    The actual input filtering will be handled by a separate BufferControl.

    :param choices: list of choices to display
    :type choices: List[Any]
    :param default: default value, move selected_choice_index
    :type default: Any
    :param pointer: pointer symbol
    :type pointer: str
    :param marker: marker symbol for the selected choice in the case of multiselect
    :type marker: str
    :param current_text: current buffer text
    :type current_text: Callable[[], str]
    """

    def __init__(
        self,
        choices: List[Any],
        default: Any,
        pointer: str,
        marker: str,
        current_text: Callable[[], str],
    ) -> None:
        """Construct UIControl and initialise choices."""
        self._pointer = pointer
        self._marker = marker
        super().__init__(choices, default)
        self._current_text = current_text

        for index, choice in enumerate(self.choices):
            if isinstance(choice["value"], Separator):
                raise InvalidArgument("fuzzy type prompt does not accept Separator.")
            choice["selected"] = False
            choice["index"] = index

        self._filtered_choice = self.choices
        self._filtered_indices = []

    def _get_hover_text(self, choice, indices) -> List[Tuple[str, str]]:
        display_choices = []
        display_choices.append(("class:pointer", self._pointer))
        display_choices.append(
            ("class:fuzzy_marker", self._marker if choice["selected"] else " ")
        )
        display_choices.append(("[SetCursorPosition]", ""))
        if not indices:
            display_choices.append(("class:pointer", choice["name"]))
        else:
            indices = set(indices)
            for index, char in enumerate(choice["name"]):
                if index in indices:
                    display_choices.append(("class:fuzzy_match", char))
                else:
                    display_choices.append(("class:pointer", char))
        return display_choices

    def _get_normal_text(self, choice, indices) -> List[Tuple[str, str]]:
        display_choices = []
        display_choices.append(("class:pointer", len(self._pointer) * " "))
        display_choices.append(
            (
                "class:fuzzy_marker",
                self._marker if choice["selected"] else " ",
            )
        )
        if not indices:
            display_choices.append(("", choice["name"]))
        else:
            indices = set(indices)
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

        :return: a list of formatted choices
        :rtype: List[Tuple[str, str]]
        """
        display_choices = []

        for index, choice in enumerate(self._filtered_choice):
            if index == self.selected_choice_index:
                display_choices += self._get_hover_text(
                    choice,
                    None
                    if len(self._filtered_choice) == len(self.choices)
                    else self._filtered_indices[index],
                )
            else:
                display_choices += self._get_normal_text(
                    choice,
                    None
                    if len(self._filtered_choice) == len(self.choices)
                    else self._filtered_indices[index],
                )
            display_choices.append(("", "\n"))
        if display_choices:
            display_choices.pop()
        return display_choices

    def filter_choices(self) -> None:
        """Call to filter choices using fzy fuzzy match.

        Making it callable so that it can be called duing `prompt_toolkit` buffer
        event `on_text_changed`. This allows to get the `self.selected_choice_index`
        a more realtime and accurate adjustment.
        """
        if not self._current_text():
            self._filtered_choice = self.choices
        else:
            indices, choices = fuzzy_match_py(self._current_text(), self.choices)
            self._filtered_choice = choices
            self._filtered_indices = indices

    @property
    def selection(self) -> Dict[str, Any]:
        """Override this value since `self.choice` does not indicate the choice displayed.

        `self.filtered_choice` is the up to date choice displayed.

        :return: a dictionary of name and value for the current pointed choice
        :rtype: Dict[str, Any]
        """
        return self._filtered_choice[self.selected_choice_index]

    @property
    def choice_count(self) -> int:
        """Get the filtered choice count.

        :return: total count of choices
        :rtype: int
        """
        return len(self._filtered_choice)


class FuzzyPrompt(BaseSimplePrompt):
    """A filter prompt that allows user to input value.

    Filters the result using fuzzy finding. The fuzzy finding logic
    is contains in the file fzy.py which is copied from `vim-clap`
    python provider.

    :param message: message to display to the user
    :type message: str
    :param choices: list of choices available to select
    :type choices: List[Any]
    :param default: default value
    :type default: Any
    :param pointer: pointer symbol
    :type pointer: str
    :param style: style dict to apply
    :type style: Dict[str, str]
    :param editing_mode: keybinding mode
    :type editing_mode: Literal["default", "vim", "emacs"]
    :param qmark: question mark symbol
    :type qmark: str
    :param transformer: transform the result to output, this is only visual effect
    :type transformer: Callable
    :param instruction: instruction to display after the message
    :type instruction: str
    :param multiselect: enable multi selection of the choices
    :type multiselect: bool
    :param prompt: prompt symbol for buffer
    :type prompt: str
    :param marker: marker symbol for the selected choice in the case of multiselect
    :type marker: str
    """

    def __init__(
        self,
        message: str,
        choices: List[Any],
        default: Any = None,
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        style: Dict[str, str] = {},
        editing_mode: Literal["default", "vim", "emacs"] = "default",
        qmark: str = "?",
        transformer: Callable = None,
        instruction: str = "",
        multiselect: bool = False,
        prompt: str = INQUIRERPY_POINTER_SEQUENCE,
        marker: str = INQUIRERPY_POINTER_SEQUENCE,
        boarder: bool = False,
    ) -> None:
        """Initialise the layout and create Application."""
        self._instruction = instruction
        self._multiselect = multiselect
        self._prompt = prompt
        self._boarder = boarder
        super().__init__(
            message=message,
            style=style,
            editing_mode=editing_mode,
            qmark=qmark,
            transformer=transformer,
        )
        self.content_control = InquirerPyFuzzyControl(
            choices=choices,
            default=default,
            pointer=pointer,
            marker=marker,
            current_text=self._get_current_text,
        )
        self.buffer = Buffer(on_text_changed=self._on_text_changed)
        message_window = Window(
            height=LayoutDimension.exact(1),
            content=FormattedTextControl(self._get_prompt_message, show_cursor=False),
        )
        input_window = Window(
            height=LayoutDimension.exact(1),
            content=BufferControl(
                self.buffer,
                [
                    AfterInput(self._generate_after_input),
                    BeforeInput(self._generate_before_input),
                ],
            ),
        )
        choice_window = Window(content=self.content_control)
        main_content_window = HSplit([input_window, choice_window])
        if self._boarder:
            main_content_window = Frame(main_content_window)
        self.layout = Layout(
            HSplit(
                [
                    message_window,
                    ConditionalContainer(main_content_window, filter=~IsDone()),
                ]
            )
        )
        self.layout.focus(input_window)

        @Condition
        def is_multiselect() -> bool:
            return self._multiselect

        @self.kb.add(Keys.Enter)
        def _(event):
            self._handle_enter(event)

        @self.kb.add(Keys.Tab, filter=is_multiselect)
        def _(event):
            self._handle_tab()
            self._handle_down()

        @self.kb.add(Keys.BackTab, filter=is_multiselect)
        def _(event):
            self._handle_tab()
            self._handle_up()

        @self.kb.add(Keys.Down)
        @self.kb.add("c-n")
        def _(event):
            self._handle_down()

        @self.kb.add(Keys.Up)
        @self.kb.add("c-p")
        def _(event):
            self._handle_up()

        self.application = Application(
            layout=self.layout,
            style=self.question_style,
            key_bindings=self.kb,
            editing_mode=self.editing_mode,
        )

    def _generate_after_input(self) -> List[Tuple[str, str]]:
        """Virtual text displayed after the user input."""
        display_message = []
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

    def _on_text_changed(self, buffer) -> None:
        """Handle buffer text change event.

        1. Run a new filter on all choices.
        2. Re-calculate current selected_choice_index
            if it exceeds the total filtered_choice.
        3. Avoid selected_choice_index less than zero,
            this fix the issue of cursor lose when:
            choice -> empty choice -> choice
        """
        self.content_control.filter_choices()
        if (
            self.content_control.selected_choice_index
            > self.content_control.choice_count - 1
        ):
            self.content_control.selected_choice_index = (
                self.content_control.choice_count - 1
            )
        if self.content_control.selected_choice_index == -1:
            self.content_control.selected_choice_index = 0

    def _handle_down(self) -> None:
        self.content_control.selected_choice_index = (
            self.content_control.selected_choice_index + 1
        ) % self.content_control.choice_count

    def _handle_up(self) -> None:
        self.content_control.selected_choice_index = (
            self.content_control.selected_choice_index - 1
        ) % self.content_control.choice_count

    def _handle_tab(self) -> None:
        """Handle tab event, alter the `selected` state of the choice."""
        current_selected_index = self.content_control.selection["index"]
        self.content_control.choices[current_selected_index][
            "selected"
        ] = not self.content_control.choices[current_selected_index]["selected"]

    def _handle_enter(self, event) -> None:
        """Handle enter event.

        In multiselect scenario, if no TAB is entered, then capture the current
        highlighted choice and return the value in a list.
        Otherwise, return all TAB choices as a list.

        In normal scenario, reutrn the current highlighted choice.

        If current UI contains no choice due to filter, return None.
        """
        try:
            if self._multiselect:
                self.status["answered"] = True
                if not self.selected_choices:
                    self.status["result"] = [self.content_control.selection["name"]]
                    event.app.exit(result=[self.content_control.selection["value"]])
                else:
                    self.status["result"] = [
                        choice["name"] for choice in self.selected_choices
                    ]
                    event.app.exit(
                        result=[choice["value"] for choice in self.selected_choices]
                    )
            else:
                self.status["answered"] = True
                self.status["result"] = self.content_control.selection["name"]
                event.app.exit(result=self.content_control.selection["value"])
        except IndexError:
            self.status["answered"] = True
            self.status["result"] = None if not self._multiselect else []
            event.app.exit(result=None if not self._multiselect else [])

    @property
    def selected_choices(self) -> List[Dict[str, Any]]:
        """Get all user selected choices."""
        return list(
            filter(lambda choice: choice["selected"], self.content_control.choices)
        )

    def _get_current_text(self) -> str:
        """Get current input buffer text."""
        return self.buffer.text

    def _get_prompt_message(self) -> List[Tuple[str, str]]:
        """Get the prompt message for FormattedTextControl.

        To be used by the first window in layout.

        :return: list of formatted text
        :rtype: List[Tuple[str, str]]
        """
        pre_answer = ("class:instruction", " %s" % self._instruction)
        post_answer = ("class:answer", " %s" % self.status["result"])
        return super()._get_prompt_message(pre_answer, post_answer)

    def execute(self) -> Any:
        """Execute the application and get the result."""
        return self.application.run()
