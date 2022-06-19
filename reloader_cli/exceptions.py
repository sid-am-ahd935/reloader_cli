class PathNotFoundError(Exception):
    __module__ = Exception.__module__

    def __init__(self, path):
        super().__init__(
            "User error. \nThe path to the python file [%s] is not available. \nPlease enter an absolute path or run the reloader-cli tool in the same directory as of that script"
            % (path)
        )


class ScriptNotRunnableError(Exception):
    __module__ = Exception.__module__

    def __init__(self, path):
        super().__init__(
            "User error. \nThe path to the file [%s] is not a python script. \nThis reloader-cli tool is made for python scripts."
            % (path)
        )


def custom_exception_handler(exception_type, exception, traceback):
    print("\n%s: %s\n" % (exception_type.__name__, exception))
