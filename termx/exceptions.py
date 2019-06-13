class TermxException(Exception):

    def __init__(self, *args):
        if len(args) == 1:
            self.__message__ = args[0]

    def __str__(self):
        return self.__message__
