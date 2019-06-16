import sys


class Cursor:

    @classmethod
    def write(cls, text, newline=True):
        if newline:
            sys.stdout.write("%s\n" % text)
        else:
            sys.stdout.write("%s" % text)

    @classmethod
    def overwrite(cls, text, newline=True):
        cls.clear_line()
        cls.write(text, newline=newline)

    @classmethod
    def clear_line(cls):
        sys.stdout.write("\033[K")

    @classmethod
    def carriage_return(cls):
        sys.stdout.write("\r")

    @classmethod
    def newline(cls):
        sys.stdout.write("\n")

    @classmethod
    def move_right(cls, n=1):
        chars = "\u001b[%sC" % n
        sys.stdout.write(chars)

    @classmethod
    def move_left(cls, n=1):
        chars = "\u001b[%sD" % n
        sys.stdout.write(chars)

    @classmethod
    def move_up(cls, n=1):
        chars = "\u001b[%sA" % n
        sys.stdout.write(chars)

    @classmethod
    def move_down(cls, n=1):
        chars = "\u001b[%sB" % n
        sys.stdout.write(chars)

    @classmethod
    def show(cls):
        sys.stdout.write("\033[?25h")
        # sys.stdout.flush()

    @classmethod
    def hide(cls):
        sys.stdout.write("\033[?25l")
        # sys.stdout.flush()
