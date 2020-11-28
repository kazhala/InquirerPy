"""Module contains list prompt."""

from typing import Any, Dict, List, Literal, Tuple, Union

from prompt_toolkit.application import Application
from prompt_toolkit.filters import IsDone
from prompt_toolkit.layout import Layout
from prompt_toolkit.layout.containers import Window
from prompt_toolkit.layout.containers import ConditionalContainer, HSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.dimension import LayoutDimension

from InquirerPy.base import (
    BaseSimplePrompt,
    INQUIRERPY_KEYBOARD_INTERRUPT,
    INQUIRERPY_POINTER_SEQUENCE,
    InquirerPyUIControl,
)


class InquirerPyListControl(InquirerPyUIControl):
    """A UIControl class intended to be consumed by prompt_toolkit window.

    Used to dynamically render the list and update the content based on input

    :param options: a list of options to display
    :type options: List[Union[str, Dict[str, Any]]]
    :param default: default selection
    :type default: Any
    :param pointer: the pointer char to display, default is unicode ">"
    :type pointer: str
    """

    def __init__(
        self,
        options: List[Union[str, Dict[str, Any]]],
        default: Any,
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
    ) -> None:
        """Construct and init a custom FormattedTextControl object."""
        self.pointer: str = pointer
        super().__init__(options=options, default=default)

    def _get_hover_text(self, option) -> List[Tuple[str, str]]:
        display_options = []
        display_options.append(("class:pointer", " %s " % self.pointer))
        display_options.append(("[SetCursorPosition]", ""))
        display_options.append(("class:pointer", str(option["name"])))
        return display_options

    def _get_normal_text(self, option) -> List[Tuple[str, str]]:
        display_options = []
        display_options.append(("", "   "))
        display_options.append(("", str(option["name"])))
        return display_options


# class InquirerListControl(FormattedTextControl):
#     def __init__(
#         self,
#         choices: List[Union[str, Dict[str, Any]]],
#         default: Any,
#         pointer=INQUIRERPY_POINTER_SEQUENCE,
#     ):
#         self.selected_option_index: int = 0
#         self.pointer: str = pointer
#         self.choices: List[Dict[str, Any]] = self._get_choices(choices, default)
#         if not choices:
#             raise InvalidArgument("choices cannot be empty.")
#         super().__init__(self._get_formatted_choices)

#     def _get_choices(self, choices, default) -> List[Dict[str, Any]]:
#         processed_choices: List[Dict[str, Any]] = []
#         try:
#             for index, choice in enumerate(choices, start=0):
#                 if isinstance(choice, str):
#                     if choice == default:
#                         self.selected_option_index = index
#                     processed_choices.append({"name": choice, "value": choice})
#                 elif isinstance(choice, dict):
#                     if choice["value"] == default:
#                         self.selected_option_index = index
#                     processed_choices.append(
#                         {"name": choice["name"], "value": choice["value"]}
#                     )
#                 else:
#                     raise InvalidArgument(
#                         "choice has to be either a string or dictionary."
#                     )
#         except KeyError:
#             raise RequiredKeyNotFound(
#                 "dictionary choice require a name key and a value key."
#             )
#         except InvalidArgument:
#             raise
#         return processed_choices

#     def _get_formatted_choices(self):
#         display_choices = []

#         for index, choice in enumerate(self.choices):
#             if index == self.selected_option_index:
#                 display_choices.append(("class:pointer", " %s " % self.pointer))
#                 display_choices.append(("[SetCursorPosition]", ""))
#                 display_choices.append(("class:pointer", str(choice["name"])))
#             else:
#                 display_choices.append(("", "   "))
#                 display_choices.append(("", str(choice["name"])))
#             display_choices.append(("", "\n"))
#         display_choices.pop()
#         return display_choices

#     @property
#     def choice_count(self) -> int:
#         return len(self.choices)

#     @property
#     def selection(self) -> Any:
#         return self.choices[self.selected_option_index]["value"]


class ListPrompt(BaseSimplePrompt):
    """A wrapper class around prompt_toolkit Application to create a list prompt.

    :param message: message to display
    :type message: str
    :param options: list of options to display
    :type options: List[Union[str, Dict[str, Any]]]
    :param default: default value
    :type default: Any
    :param style: a dictionary of style
    :type style: Dict[str, str]
    :param editing_mode: editing_mode of the prompt
    :type editing_mode: Literal["emacs", "default", "vim"]
    :param symbol: question symbol to display
    :type symbol: str
    :param pointer: the pointer symbol of hovered option
    :type pointer: str
    """

    def __init__(
        self,
        message: str,
        options: List[Union[str, Dict[str, Any]]],
        default: Any,
        style: Dict[str, str],
        editing_mode: Literal["emacs", "default", "vim"] = "default",
        symbol: str = "?",
        pointer: str = INQUIRERPY_POINTER_SEQUENCE,
    ) -> None:
        """Initialise the Application."""
        super().__init__(message, style, editing_mode, symbol)
        self.pointer = pointer
        self.content_control = InquirerPyListControl(options, default, pointer)

        self.layout = HSplit(
            [
                Window(
                    height=LayoutDimension.exact(1),
                    content=FormattedTextControl(
                        self._get_prompt_message, show_cursor=False
                    ),
                ),
                ConditionalContainer(
                    Window(content=self.content_control),
                    filter=~IsDone(),
                ),
            ]
        )

        @self.kb.add("j")
        def _(event):
            self.content_control.selected_option_index = (
                self.content_control.selected_option_index + 1
            ) % self.content_control.option_count

        @self.kb.add("k")
        def _(event):
            self.content_control.selected_option_index = (
                self.content_control.selected_option_index - 1
            ) % self.content_control.option_count

        @self.kb.add("enter")
        def _(event):
            self.status["answered"] = True
            self.status["result"] = self.content_control.selection
            event.app.exit(result=self.status["result"])

        @self.kb.add("c-c")
        def _(event) -> None:
            self.status["answered"] = True
            self.status["result"] = ""
            event.app.exit(result=INQUIRERPY_KEYBOARD_INTERRUPT)

        self.application = Application(
            layout=Layout(self.layout), style=self.question_style, key_bindings=self.kb
        )

    def _get_prompt_message(self):
        pre_answer = ("class:instruction", " %s" % self.message)
        post_answer = ("class:answer", " %s" % self.status["result"])
        return super()._get_prompt_message(pre_answer, post_answer)

    def execute(self) -> Any:
        """Run the application and get the result."""
        return self.application.run()
