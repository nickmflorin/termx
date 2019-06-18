import contextlib
import sys

import logging


class Cursor:

    output = sys.stdout.write

    @classmethod
    @contextlib.contextmanager
    def stdout_replacement(cls, func):
        original_stdout = sys.stdout.write
        try:
            sys.stdout.write = func
            yield sys.stdout.write
        finally:
            sys.stdout.write = original_stdout

    @classmethod
    @contextlib.contextmanager
    def silence_stdout(cls):

        silenced_messages = []
        original_stdout = sys.stdout.write

        def controlled_std(text):
            with cls.stdout_replacement(original_stdout) as write:
                write(text)

        try:
            sys.stdout.write = lambda x: silenced_messages.append(x)
            cls.output = controlled_std
            yield cls
        finally:
            sys.stdout.write = original_stdout
            cls.output = sys.stdout.write

            if len(silenced_messages) != 0:
                logging.warning('Trying to use `sys.stdout.write` when it is disabled.')
                for message in silenced_messages:
                    cls.write_line(message)

    @classmethod
    def write(cls, text):
        cls.output(text)

    @classmethod
    def write_line(cls, text, newline=True):
        message = "%s" % text
        if newline:
            message = "%s\n" % text
        cls.write(message)

    @classmethod
    def overwrite(cls, text, newline=True):
        cls.clear_line()
        cls.write_line(text, newline=newline)

    @classmethod
    def clear_line(cls):
        cls.write("\033[K")

    @classmethod
    def carriage_return(cls):
        cls.write("\r")

    @classmethod
    def newline(cls):
        cls.write("\n")

    @classmethod
    def move_right(cls, n=1):
        chars = "\u001b[%sC" % n
        cls.write(chars)

    @classmethod
    def move_left(cls, n=1):
        chars = "\u001b[%sD" % n
        cls.write(chars)

    @classmethod
    def move_up(cls, n=1):
        chars = "\u001b[%sA" % n
        cls.write(chars)

    @classmethod
    def move_down(cls, n=1):
        chars = "\u001b[%sB" % n
        cls.write(chars)

    @classmethod
    def show(cls):
        cls.write("\033[?25h")

    @classmethod
    def hide(cls):
        cls.write("\033[?25l")
