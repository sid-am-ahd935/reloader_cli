import os  # Also used as module type instance
import sys
import time
from pathlib import PurePath, Path
from argparse import ArgumentParser
from multiprocessing import Process
from .exceptions import PathNotFoundError


def get_module(module_name: [str("path") or type("module")]) -> "<class 'module'>":
    """
    Returns the module object of the script specified through an absolute path.
    Similar to:
        import <module_name> as module
        return module

    :param module_name: A string containing the path to the python script to run as a module.
    :return: Module type object.
    """

    # If a module type object is passed as an argument, just return it.
    if isinstance(module_name, type(os)):
        return module_name

    # The Path to the python script is only accepted in string and nothing else.
    if not isinstance(module_name, str):
        raise TypeError(
            "get_module(module_name) only takes string for path of python script or module object, and not [%s] type"
            % (type(module_name))
        )

    if not module_name.endswith(".py"):
        module_name = module_name + ".py"

    # When module name is a relative/(incomplete absolute) path
    module_name = os.path.abspath(module_name)

    # If the path is not available, raise the error
    if not os.path.exists(module_name):
        raise PathNotFoundError(module_name)

    # When the python script is at another directory than this tool, import does not support importing modules from directories which are not packages
    if os.getcwd() != os.path.dirname(module_name):
        # Increasing the reach of importing modules for that scripts folder
        sys.path.append(os.path.dirname(module_name))
        ## Name of a module cannot be a file name, it must be if this format: [name].py ==> import [name]
        module_import_name = Path(module_name).stem

    try:
        module = __import__(module_import_name)
        return module

    except ModuleNotFoundError:
        raise PathNotFoundError(module_name) from None


def time_now() -> str:
    return time.strftime("%H:%M:%S")


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
    def run123():
        print(a(), b(), c())

    >> reloader-cli app run123

    :param module: Path of the python script or module object that contains the func_name as callable function.
    :param func_name: The name of the function to be called to execute the whole script. Eg. run().
    """
    module = get_module(module)

    # Mentioned script does not contain the function
    if not hasattr(module, func_name):
        raise AttributeError(
            "No %s() function was found to run the script" % (func_name)
        )

    # The name of the function can only be a string
    if not isinstance(func_name, str):
        raise TypeError(
            "get_module(module, func_name) only takes string for :func_name: parameter, and not [%s] type"
            % (type(module_name))
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

    if not os.path.exists(path):
        if os.path.exists(path+'.py'):
            path = path + '.py'
        else:
            raise PathNotFoundError(path) from None

    if not isinstance(interval, float):
        try:
            interval = float(interval)
        except ValueError:
            raise ValueError(
                "Interval not set properly, please ensure interval is in Integer or Float format."
            ) from None

    prev = None
    process = Process()
    try:
        while True:
            try:
                curr = os.path.getsize(path)

                if curr != prev:
                    if prev == None:
                        print('\n[%s] starting reloader for "%s" watching changes in %s...\n' % (time_now(), module, path))
                        prev = curr
                        continue
                    print(
                        '\n[%s] changes detected in %s reloading "%s" to reflect changes...\n'
                        % (time_now(), path, module)
                    )
                    if process.is_alive():
                        process.kill()
                    process = Process(target=get_func(module, func))
                    process.start()

                prev = curr
                if not process.is_alive():
                    # The script exited by itself, close the reloader-cli
                    print('[%s] process already dead, shutting down reloader...')
                    break
                time.sleep(interval)

            except KeyboardInterrupt:
                print("\n[%s] ^C detected, shutting down all processes..." % (time_now()))
                break
    finally:
        if process.is_alive():
            process.kill()


def main():
    parser = ArgumentParser(
        description="Debugger Reload The Script Everytime A Change Is Detected In The Script"
    )
    parser.add_argument(
        "module",
        default="app",
        nargs="?",
        help="The script thats runs by using reloader",
    )
    parser.add_argument(
        "function",
        default="run",
        nargs="?",
        help="The function that runs all functionality of the script. Eg: main() of a function.",
    )
    parser.add_argument("--interval", "-i", default=0.25, type=float, nargs=1)

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--script",
        "--module",
        "-m",
        "-s",
        action="store_true",
        dest="s",
        help="The default option for this tool, to watch for change in that individual script.",
    )
    group.add_argument(
        "--dir",
        "--path",
        "-p",
        "-d",
        nargs="?",
        const=True,
        dest="p",
        help="Currently under development.",
    )
    args = parser.parse_args()

    module = args.module
    func = args.function
    change_in = None
    path = None
    interval = args.interval

    if args.p:
        print("This part of the tool is under development.")
        exit(1)
        # change_in = 'path'
        # if args.p is True:
        #     path = None
        # elif type(args.p) is str:
        #     path = args.p

    elif args.s:
        change_in = "script"

    reload_on_change(module, func, change_in, path, interval)


if __name__ == "__main__":
    main()
    # TODO: Create a decorator which wraps the run function and runs the reloader automatically.
