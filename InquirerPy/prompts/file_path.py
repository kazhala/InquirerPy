import os
from pathlib import Path

from prompt_toolkit import prompt
from prompt_toolkit.completion import Completer, Completion
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.validation import ValidationError, Validator


class FilePath:
    def __init__(self, message, style, default, symbol, key_binding_mode, **kwargs):
        pass


class MyCustomCompleter(Completer):
    def get_completions(self, document, complete_event):
        if document.cursor_position == 0 or document.text == "~":
            return

        validation = lambda file, doc_text: str(file).startswith(doc_text)

        if document.text.startswith("~"):
            dirname = os.path.dirname("%s%s" % (Path.home(), document.text[1:]))
            validation = lambda file, doc_text: str(file).startswith(
                "%s%s" % (Path.home(), doc_text[1:])
            )
        elif document.text.startswith("./"):
            dirname = os.path.curdir
            validation = lambda file, doc_text: str(file).startswith(doc_text[2:])
        else:
            dirname = os.path.dirname(document.text)
        path = Path(dirname)

        for item in self._get_completion(document, path, validation):
            yield item

    def _get_completion(self, document, path, validation):
        for file in path.iterdir():
            if validation(file, document.text):
                yield Completion(
                    "%s" % os.path.basename(str(file)),
                    start_position=-1 * len(os.path.basename(document.text)),
                )


class PathValidator(Validator):
    def validate(self, document):
        if not Path(document.text).expanduser().exists():
            raise ValidationError(
                message="The input is not valid path",
                cursor_position=document.cursor_position,
            )


bindings = KeyBindings()


@bindings.add("c-space")
def _(event):
    buff = event.app.current_buffer
    if buff.complete_state:
        buff.complete_next()
    else:
        buff.start_completion(select_first=False)


text = prompt(
    "> ",
    completer=MyCustomCompleter(),
    validator=PathValidator(),
    validate_while_typing=False,
    key_bindings=bindings,
)
