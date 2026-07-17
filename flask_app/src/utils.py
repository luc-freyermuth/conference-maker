import re
from threading import Timer
from inspect import signature
import time
from typing import Any
import math
from urllib.parse import urlparse

def get_valid_filename(name):
    s = str(name).strip().replace(" ", "_")
    s = re.sub(r"(?u)[^-\w.]", "", s)
    if s in {"", ".", ".."}:
        raise ValueError("Could not derive file name from '%s'" % name)
    return s

def debounce(wait):
    def decorator(fn):
        sig = signature(fn)
        caller = {}

        def debounced(*args, **kwargs):
            nonlocal caller

            try:
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
                called_args = fn.__name__ + str(dict(bound_args.arguments))
            except:
                called_args = ''

            t_ = time.time()

            def call_it(key):
                try:
                    # always remove on call
                    caller.pop(key)
                except:
                    pass

                fn(*args, **kwargs)

            try:
                # Always try to cancel timer
                caller[called_args].cancel()
            except:
                pass

            caller[called_args] = Timer(wait, call_it, [called_args])
            caller[called_args].start()

        return debounced

    return decorator


def check_not_blank(value: Any, name: str) -> str:
    if value is None or value == '' or (type(value) is float and math.isnan(value)):
        raise ValueError(f'Le champ `{name}` est vide')
    return str(value)

def check_int(value: Any, name: str) -> int:
    if value is None or (type(value) is not int):
        raise ValueError(f'Le champ `{name}` n\'est pas un entier valide')
    return value

def get_urls_in_str(text: str) -> list[str]:
    words= text.split()

    urls = []
    for word in words:
        parsed = urlparse(word)
        if parsed.scheme and parsed.netloc:
            urls.append(word)

    return urls