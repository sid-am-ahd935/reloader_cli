import os, pathlib, pytest
from reloader_cli.reloader_cli import (
    reload_on_change,
    PathNotFoundError,
    get_module,
    get_func,
)


BASE_DIR = pathlib.Path(__file__).parent


working_module_path = str(BASE_DIR / 'dummy_app')
error_module_path = str(BASE_DIR / "my_dummy_app_for_testing")
func_name = 'run'
non_func_name = 'var_a'


class Test_get_module:

    def test_raises_custom_exception_when_module_not_present(self):
        with pytest.raises(PathNotFoundError) as e_info:
            get_module(error_module_path)


    def test_returns_module_object_when_module_present(self):
        assert isinstance(get_module(working_module_path), type(pytest))


    def test_returns_same_module_object_when_argument_is_a_module(self):
        assert pytest is get_module(pytest)


    def test_raises_typeError_when_argument_is_not_string(self):
        with pytest.raises(TypeError) as e_info:
            get_module(None)


class Test_get_func:
    module = working_module_path

    def test_raises_attributeError_when_function_not_present_in_module(self):
        with pytest.raises(AttributeError) as e_info:
            get_func(self.module, 'random_function_name')


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

    def test_raises_valueError_when_change_in_value_different_from_expected(self):
        with pytest.raises(ValueError) as e_info:
            reload_on_change(self.module, self.func, change_in= 'random_word', path= None, interval= 0.25)
    

    def test_system_exits_when_path_is_given(self):
        with pytest.raises(SystemExit) as e_info:
            reload_on_change(self.module, self.func, change_in= None, path= 'random/path', interval= 0.25)
        
        assert e_info.type == SystemExit
        assert e_info.value.code == 1

    
    def test_raises_custom_exception_when_module_not_present(self):
        with pytest.raises(PathNotFoundError) as e_info:
            reload_on_change(error_module_path, self.func, change_in= None, path= None, interval= 0.25)
    

    def test_raises_valueError_when_interval_not_float(self):
        with pytest.raises(ValueError) as e_info:
            reload_on_change(self.module, self.func, change_in= None, path= None, interval= 'Not an inch of float here')


    # def test_everything_works_fine(self):
    #     reload_on_change(self.module, self.func, change_in= None, path= None, interval= 0.25)
