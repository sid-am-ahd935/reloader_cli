import os
import pathlib
import signal
import time
from multiprocessing import Process

import pytest
from reloader_cli.__main__ import (
    PathNotFoundError,
    ScriptNotRunnableError,
    get_func,
    get_module_with_path,
    reload_on_change,
    time_now,
)

BASE_DIR = pathlib.Path(__file__).parent


working_module_path = str(BASE_DIR / "dummy_app")
working_path_not_module = str(BASE_DIR / "dummy.txt")
working_path_no_extension = str(BASE_DIR / "dummy")
func_name = "run"
non_func_name = "var_a"


class Test_dummy_app_created_for_testing:
    dummy_app = __import__("tests.dummy_app", fromlist=["dummy_app"])

    def test_dummy_app_is_present(self):
        assert os.path.exists(working_module_path + ".py")

    def test_dummy_app_has_callable_func_name(self):
        assert hasattr(self.dummy_app, func_name)
        assert callable(getattr(self.dummy_app, func_name))

    def test_dummy_app_func_name_runs_and_prints(self, capfd):
        getattr(self.dummy_app, func_name)()
        captured = capfd.readouterr()
        assert captured.out == "Dummy Runs!!\n"

    def test_dummy_app_has_non_callable_non_func_name(self):
        assert hasattr(self.dummy_app, non_func_name)
        assert not callable(getattr(self.dummy_app, non_func_name))

    def test_dummy_app_has_callable_long_runner_function(self, capfd):
        getattr(self.dummy_app, "wait")(1)


def test_time_now():
    assert type(time_now()) is str


class Test_get_module:
    def test_raises_custom_exception_when_module_not_present(self):
        assert not os.path.exists("random_module_name")
        with pytest.raises(PathNotFoundError) as e_info:
            get_module_with_path("random_module_name")

    def test_returns_module_object_and_path_when_module_present(self):
        path, module = get_module_with_path(working_module_path)
        assert isinstance(module, type(pytest))
        assert isinstance(path, str)

    def test_returns_same_module_object_when_argument_is_a_module(self):
        path, module = get_module_with_path(pytest)
        assert module is pytest
        assert type(path) is str

    def test_raises_typeError_when_argument_is_not_string(self):
        with pytest.raises(TypeError) as e_info:
            get_module_with_path(None)

    def test_raises_custom_exception_when_script_not_a_module(self):
        with pytest.raises(ScriptNotRunnableError) as e_info:
            get_module_with_path(working_path_not_module)


class Test_get_func:
    module = working_module_path

    def test_raises_attributeError_when_function_not_present_in_module(self):
        with pytest.raises(AttributeError) as e_info:
            get_func(self.module, "random_function_name")

    def test_raises_typeError_when_argument_is_not_string(self):
        with pytest.raises(TypeError) as e_info:
            get_func(self.module, None)

    def test_raises_typeError_when_function_not_callable(self):
        with pytest.raises(TypeError) as e_info:
            get_func(self.module, non_func_name)

    def test_returns_callable_when_module_and_function_available(self):
        assert callable(get_func(self.module, func_name))


class Test_reload_on_change:
    module = working_module_path
    func = func_name
    test_func = "test"
    testing_interval = 0.0001  # Keep this very short for high speed testing, but not too short which causes clustered working

    def test_raises_valueError_when_change_in_value_different_from_expected(self):
        with pytest.raises(ValueError) as e_info:
            reload_on_change(
                self.module,
                self.func,
                change_in="random_word",
                path=None,
                interval=0.25,
            )

    def test_system_exits_when_path_is_given(self):
        with pytest.raises(SystemExit) as e_info:
            reload_on_change(
                self.module,
                self.func,
                change_in=None,
                path="random/path",
                interval=0.25,
            )

        assert e_info.type == SystemExit
        assert e_info.value.code == 1

    def test_raises_custom_exception_when_module_not_present(self):
        with pytest.raises(PathNotFoundError) as e_info:
            reload_on_change(
                "random_module_name",
                self.func,
                change_in=None,
                path=None,
                interval=0.25,
            )

    def test_raises_valueError_when_interval_not_float(self):
        with pytest.raises(ValueError) as e_info:
            reload_on_change(
                self.module,
                self.func,
                change_in=None,
                path=None,
                interval="Not an inch of float here",
            )

    def write_to_detect_changes(self, times=10, file_path=None):
        if file_path is None:
            file_path = self.module + ".py"

        og_file = open(file_path).read()

        for _ in range(times):
            time.sleep(self.testing_interval)
            with open(file_path, "a") as f:
                f.write("\n1")

        with open(file_path, "w") as f:
            f.write(og_file)

    def test_write_to_detect_function_works_and_does_not_change_file_permanently(self):
        file_path = self.module + ".py"
        actual_file = open(file_path).read()

        self.write_to_detect_changes(times=2)

        modified_file = open(file_path).read()

        assert modified_file == actual_file

    def test_works_perfectly(self, capfd):
        # process = Process(target= reload_on_change, args= (self.module, self.test_func), kwargs= dict(change_in= None, path= None, interval= 0.01))
        # # Does not print anything in this capfd

        process = Process(target=self.write_to_detect_changes)
        process.start()

        reload_on_change(
            self.module,
            self.test_func,
            change_in=None,
            path=None,
            interval=self.testing_interval,
        )
        # This side only runs after above function is completed

        process.join()

        captured = capfd.readouterr()
        assert " starting reloader" in captured.out
        assert " changes detected" in captured.out
        assert " script stopped running" in captured.out

    def test_keep_alive_runs(self, capfd):

        process = Process(
            target=reload_on_change,
            args=(
                self.module,
                self.func,
            ),
            kwargs=dict(
                change_in=None,
                path=None,
                interval=self.testing_interval,
                keep_alive=True,
            ),
        )
        process.start()
        process.join(0.1)
        self.write_to_detect_changes(times=20, file_path=self.module + ".py")

        process.join(0.5)
        self.write_to_detect_changes(times=20, file_path=self.module + ".py")
        process.terminate()

        captured = capfd.readouterr()

        assert " changes detected" in captured.out
        assert (
            "script stopped running, keeping alive reloader for next reload"
            in captured.out
        )
