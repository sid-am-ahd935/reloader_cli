
# reloader-cli

Help in fine tuning your changes with this minimalist CLI tool that reloads your python script after every save.



#
[![MIT License](https://img.shields.io/apm/l/atomic-design-ui.svg?)](https://github.com/sid-am-ahd935/reloader_cli/blob/main/LICENSE)
[![Tests Passing](https://img.shields.io/badge/tests-passing-green)](https://github.com/sid-am-ahd935/reloader_cli/tree/main/tests)
[![Coverage 100%](https://img.shields.io/badge/coverage-98%25-green)](https://github.com/sid-am-ahd935/reloader_cli/blob/main/coverage.json)
#
## Installation

Install reloader-cli with pip

```bash
  pip install reloader-cli
```
    
## Usage/Examples

To use this tool, simply install it via pip and run
```bash
  reloader [my_app.py] [main]
```
By default this tool targets the run() function inside your app.py script.

![Usage Starting Tips](https://github.com/sid-am-ahd935/reloader_cli/blob/main/images/usage-reloader-cli.gif)

## Running Tests

To run tests and see code coverage, run the following command:

```bash
  coverage run -m pytest && coverage report -m
```
Or if only to run tests, run:
```bash
  pytest
```

Keep in mind the following modules are required for running these commands:
```
  coverage
  pytest
```

## License

To view the license for using this tool, visit this link here: [MIT](https://github.com/sid-am-ahd935/reloader_cli/blob/main/LICENSE)


## Authors

- [@Aman Ahmed Siddiqui](https://www.github.com/sid-am-ahd935)


## Support and Suggestions

For any type of related support or you have some suggestions in mind, email me at aasiddiqui40@gmail.com.

## Debugging

For debugging this tool, search for 'debugging' inside the file, and follow the instructions in the comments.
