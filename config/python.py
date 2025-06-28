""" python deps for this project """

config_requires: list[str] = [
    "pyclassifiers",
]
install_requires: list[str] = [
    "termcolor",
    "yattag",
]
build_requires: list[str] = [
    "pydmt",
    "pymakehelper",
]
test_requires: list[str] = [
    "pylint",
    "pytest",
    "pytest-cov",
    "mypy",
    "pyrefly",
    # types
    "types-termcolor",
    "types-PyYAML",
]
requires = config_requires + install_requires + build_requires + test_requires
