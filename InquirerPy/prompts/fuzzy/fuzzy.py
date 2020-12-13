"""Module contains the class to construct fuzzyfinder prompt."""
from typing import Any, Callable, Dict, List, Literal, Tuple

from prompt_toolkit.application.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.enums import EditingMode
from prompt_toolkit.filters.base import Condition
from prompt_toolkit.filters.cli import IsDone
from prompt_toolkit.keys import Keys
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit, Window
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.dimension import LayoutDimension
from prompt_toolkit.layout.layout import Layout

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
    :param selected_pointer: selected_pointer symbol
    :type selected_pointer: str
    :param current_text: current buffer text
    :type current_text: Callable[[], str]
    """

    def __init__(
        self,
        choices: List[Any],
        default: Any,
        pointer: str,
        selected_pointer: str,
        current_text: Callable[[], str],
    ) -> None:
        """Construct UIControl and initialise choices."""
        self.pointer = "%s " % pointer
        self.selected_pointer = "%s " % selected_pointer
        super().__init__(choices, default)
        self.current_text = current_text

        for index, choice in enumerate(self.choices):
            if isinstance(choice["value"], Separator):
                raise InvalidArgument("fuzzy type prompt does not accept Separator.")
            choice["selected"] = False
            choice["index"] = index

        self.filtered_choice = self.choices

    def _get_hover_text(self, choice) -> List[Tuple[str, str]]:
        display_choices = []
        display_choices.append(("class:pointer", self.pointer))
        display_choices.append(("class:pointer", choice["name"]))
        return display_choices

    def _get_normal_text(self, choice) -> List[Tuple[str, str]]:
        display_choices = []
        display_choices.append(("", len(self.pointer) * " "))
        display_choices.append(("", choice["name"]))
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

        for index, choice in enumerate(self.filtered_choice):
            if index == self.selected_choice_index:
                display_choices += self._get_hover_text(choice)
            else:
                display_choices += self._get_normal_text(choice)
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
        if not self.current_text():
            self.filtered_choice = self.choices
        else:
            indices, choices = fuzzy_match_py(self.current_text(), self.choices)
            self.filtered_choice = choices

    @property
    def selection(self) -> Dict[str, Any]:
        """Override this value since `self.choice` does not indicate the choice displayed.

        `self.filtered_choice` is the up to date choice displayed.

        :return: a dictionary of name and value for the current pointed choice
        :rtype: Dict[str, Any]
        """
        return self.filtered_choice[self.selected_choice_index]

    @property
    def choice_count(self) -> int:
        """Get the filtered choice count.

        :return: total count of choices
        :rtype: int
        """
        return len(self.filtered_choice)


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
    :param selected_pointer: in multi select case, indicates selected choice
    :type selected_pointer: str
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
    """

    def __init__(
        self,
        message: str,
        choices: List[Any],
        default: Any = None,
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
        selected_pointer: str = 2 * INQUIRERPY_POINTER_SEQUENCE,
        style: Dict[str, str] = {},
        editing_mode: Literal["default", "vim", "emacs"] = "default",
        qmark: str = "?",
        transformer: Callable = None,
        instruction: str = "",
    ) -> None:
        """Initialise the layout and create Application."""
        self._instruction = instruction
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
            selected_pointer=selected_pointer,
            current_text=self._get_current_text,
        )
        self.buffer = Buffer(on_text_changed=self._on_text_changed)
        message_window = Window(
            height=LayoutDimension.exact(1),
            content=FormattedTextControl(self._get_prompt_message, show_cursor=False),
        )
        input_window = Window(
            height=LayoutDimension.exact(1), content=BufferControl(self.buffer)
        )
        choice_window = Window(content=self.content_control)
        self.layout = Layout(
            HSplit(
                [
                    message_window,
                    ConditionalContainer(input_window, filter=~IsDone()),
                    ConditionalContainer(choice_window, filter=~IsDone()),
                ]
            )
        )
        self.layout.focus(input_window)

        @self.kb.add(Keys.Enter)
        def _(event):
            self._handle_enter(event)

        @self.kb.add(Keys.Tab)
        def _(event):
            self._handle_tab()
            self._handle_down()

        @self.kb.add(Keys.BackTab)
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

    def _on_text_changed(self, buffer) -> None:
        """Handle buffer text change event."""
        self.content_control.filter_choices()
        if (
            self.content_control.selected_choice_index
            > self.content_control.choice_count - 1
        ):
            self.content_control.selected_choice_index = (
                self.content_control.choice_count - 1
            )

    def _handle_down(self) -> None:
        self.content_control.selected_choice_index = (
            self.content_control.selected_choice_index + 1
        ) % self.content_control.choice_count

    def _handle_up(self) -> None:
        self.content_control.selected_choice_index = (
            self.content_control.selected_choice_index - 1
        ) % self.content_control.choice_count

    def _handle_tab(self) -> None:
        current_selected_index = self.content_control.selection["index"]
        self.content_control.choices[current_selected_index][
            "selected"
        ] = not self.content_control.choices[current_selected_index]["selected"]

    def _handle_enter(self, event) -> None:
        selected_choices = list(
            filter(lambda choice: choice["selected"], self.content_control.choices)
        )
        self.status["answered"] = True
        self.status["result"] = [choice["name"] for choice in selected_choices]
        event.app.exit(result=[choice["value"] for choice in selected_choices])

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
