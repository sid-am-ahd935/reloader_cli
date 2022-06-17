class PathNotFoundError(Exception):
    __module__ = Exception.__module__

    def __init__(self, path):
        super().__init__(
            "\nThe path to the python file [%s] is not available. \nPlease enter an absolute path or run the reloader-cli tool in the same directory as of that script"
            % (path)
        )
