""" python depedencies for this project """


from typing import List

dev_requires: List[str] = [
    "pypitools",
    "black",
]
config_requires: List[str] = [
    "pyclassifiers",
]
install_requires: List[str] = [
    "termcolor",
    "yattag",
]
build_requires: List[str] = [
    "pymakehelper",
    "pydmt",
]
test_requires: List[str] = [
    "pylint",
    "pytest",
    "pytest-cov",
    "flake8",
    "pyflakes",
    "pycodestyle",
    "mypy",
    "pyrefly",
    # types
    "types-termcolor",
    "types-PyYAML",
]
requires = config_requires + install_requires + build_requires + test_requires
