import os  # Also used as module type instance
import sys
import time
from pathlib import Path
from argparse import ArgumentParser
from functools import partial
from multiprocessing import Process
from reloader_cli import __version__
from reloader_cli.formatter import CustomFormatter
from reloader_cli.exceptions import (
    PathNotFoundError,
    ScriptNotRunnableError,
    custom_exception_handler,
)

sys.excepthook = custom_exception_handler  # Disable this when debugging
print = partial(
    print, flush=True
)  # Prints the contents no matter the buffer size is filled or not, apparently helps when multiprocessing


def time_now() -> str:
    """
    A function to get the current time in a particular format
    """
    return time.strftime("%H:%M:%S")


def get_module_with_path(
    module_name: [str("path") or type("module")],
) -> ("path", "<class 'module'>"):
    """
    Returns the module object of the script specified through an absolute path.
    Similar to:
        import <module_name> as module
        return module

    :param module_name: A string containing the path to the python script to run as a module.
    :return: Module type object and its path.
    """

    # If a module type object is passed as an argument, just return it.
    if isinstance(module_name, type(os)):
        return os.path.dirname(module_name.__file__), module_name

    # The Path to the python script is only accepted in string and nothing else.
    if not isinstance(module_name, str):
        raise TypeError(
            "get_module(module_name) only takes string for path of python script or module object, and not [%s] type"
            % (type(module_name))
        )

    module_name = os.path.abspath(module_name)
    module_path = Path(module_name)

    if not module_path.suffix:
        module_name += ".py"
        module_path = module_path.with_suffix(".py")

    if not (os.path.exists(module_name) or module_path.exists()):
        raise PathNotFoundError(module_name)

    sys.path.append(os.path.dirname(module_name))
    module_import_name = Path(module_name).stem

    try:
        module = __import__(module_import_name)
        return module_name, module

    except ModuleNotFoundError:
        raise ScriptNotRunnableError(module_name) from None


def get_func(module: [str("path") or type("module")], func_name: str) -> callable:
    """
    Returns a callable function object which is extracted from the python script module.
    Similar to:
        import <module> as module
        return module.func_name

    Eg.
    # app.py
    def a(): ...
    def b(): ...
    def c(): ...
    def main():
        print("Value of a is", a())
        print("Value of b & c is", b(), "&", c())

    >> reloader-cli app main

    :param module: Path of the python script or module object that contains the func_name as callable function.
    :param func_name: The name of the function to be called to execute the whole script. Eg. run().
    """
    *_, module = get_module_with_path(module)

    if not isinstance(func_name, str):
        raise TypeError(
            "get_module(module, func_name) only takes string for :func_name: parameter, and not [%s] type"
            % (type(func_name))
        )
    if not hasattr(module, func_name):
        raise AttributeError(
            "No %s() function was found to run the script" % (func_name)
        )

    func = getattr(module, func_name)

    # If the function id not callable then raise error
    if callable(func):
        return func
    else:
        raise TypeError(
            "%s is of %s type and is not callable. \nPlease mention a callable function that runs the whole script."
            % (func_name, type(func))
        )


def reload_on_change(
    module: "name of script to run",
    func: "function thats runs everything inside script",
    change_in: "module/script/path/dir" = None,
    path: "path to watch for change" = None,
    interval: float = 0.25,
    keep_alive: bool = False,
):
    """
    Reloads the module.func() function whenever a change is detected inside the module script. Similar to importlib.reload().

    :param module: Takes in the path of the python script to run as a module.
    :param func: Takes in the function name to call whenever there is a change detected.
                 Basically, this function should be responsible for excecuting the whole script as if it was called directly.
    :param change_in: States whether to watch changes inside the script only or the whole directory. Values are limited to [module/script/path/dir] or None.
    :param path: Currently under development.
    :param interval: A number in float to describe how time to wait before watching for change.
    """

    if not change_in in ["module", "script", "path", "dir", None]:
        raise ValueError(
            ":change_in: can only have value from [module/script/path/dir] or None"
        )

    if path is None:
        if not change_in or change_in.lower() in ["module", "script"]:
            path = module

        # elif change_in.lower() in ['path', 'dir']:
        #     path = os.path.dirname(module)

    elif path is not None:
        print("This functionality is currently in development...")
        exit(1)

    path, module = get_module_with_path(path)
    module_name = module.__name__

    if not isinstance(interval, float):
        try:
            interval = float(interval)
        except ValueError:
            raise ValueError(
                "Interval not set properly, please ensure interval is in Integer or Float format."
            ) from None

    print(
        '\n[%s] starting reloader for "%s" watching changes in %s...\n'
        % (time_now(), module_name, path)
    )
    prev = os.path.getsize(path)

    process = Process(target=get_func(module, func))
    process.start()
    flag_keep_alive_to_print_message = True
    try:
        while True:
            time.sleep(interval)
            curr = os.path.getsize(path)

            if curr != prev:

                print(
                    '\n[%s] changes detected in %s reloading "%s" to reflect changes...\n'
                    % (time_now(), path, module_name)
                )
                if process.is_alive():
                    process.kill()

                process = Process(target=get_func(module, func))
                process.start()
                flag_keep_alive_to_print_message = True

            if not process.is_alive() and not keep_alive:
                # The script exited by itself, close the reloader-cli.
                print(
                    "\n[%s] script stopped running, shutting down reloader...\n"
                    % (time_now())
                )
                break

            elif ( not process.is_alive() and keep_alive and flag_keep_alive_to_print_message):
                # The script finished execution but is still held by by the tool.
                print('\n[%s] "%s" script stopped running, keeping alive reloader for next reload...\n' % (time_now(), module_name))
                flag_keep_alive_to_print_message = False

            prev = curr

    except KeyboardInterrupt:
        print("\n[%s] ^C detected, shutting down all processes...\n" % (time_now()))
    finally:
        if process.is_alive():
            process.kill()


def main():
    my_formatter = lambda prog: CustomFormatter(prog)
    parser = ArgumentParser(
        description="Debugger Reload The Script Everytime A Change Is Detected In The Script",
        formatter_class=my_formatter,
        epilog="Run this tool with on [app].py for running [run]() function.\n",
        usage="reloader [app] [run] [-i seconds] [-v version]",
    )
    parser.add_argument(
        "module",
        default="app",
        nargs="?",
        help="The script thats runs by using reloader",
    )
    parser.add_argument(
        "function",
        default="main",
        nargs="?",
        help="The function that runs all functionality of the script. Eg: main() of a function.",
    )
    parser.add_argument(
        "-i",
        "--interval",
        default=0.25,
        type=float,
        nargs=1,
        metavar="[seconds]",
        help="Time for cooldown between every check.",
    )
    parser.add_argument(
        "-k",
        "--keep-alive",
        action="store_true",
        help="When the scipts runs out before any change could be reloaded. Press CTRL+C in tool's CLI to exit.",
    )
    parser.add_argument("-v", "--version", action="store_true", help="Show version.")

    group = parser.add_mutually_exclusive_group()
    # group.add_argument(
    #     "--script",
    #     "--module",
    #     "-m",
    #     "-s",
    #     action="store_true",
    #     dest="s",
    #     help="The default option for this tool, to watch for change in that individual script.",
    # )
    group.add_argument(
        "-p",
        "--path",
        nargs="?",
        const=True,
        help="Currently under development.",
        metavar="path",
    )
    args = parser.parse_args()

    module = args.module
    func = args.function
    change_in = None
    path = None
    interval = (
        args.interval
        if type(args.interval) is float
        else args.interval[0]
        if type(args.interval) is list
        else 0.25
    )
    keep_alive = args.keep_alive

    if args.version:
        print(__version__)
        exit()

    if args.path:
        print("This part of the tool is under development.")
        exit(1)
        # change_in = 'path'
        # if args.p is True:
        #     path = None
        # elif type(args.p) is str:
        #     path = args.p

    reload_on_change(module, func, change_in, path, interval, keep_alive)


if __name__ == "__main__":
    main()
    # TODO: Create a decorator which wraps the run function to determine which function to run and runs the reloader automatically. + in future, might also help to determine which file to run
    # TODO: Add path watcher.
