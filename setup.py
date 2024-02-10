from setuptools import setup

setup(
    name="dev-dir-utils",
    version="0.1.0",
    py_modules=["main"],
    install_requires=[
        "requests",
        "Click",
    ],
    entry_points={
        "console_scripts": [
            "dev-dir-utils = main:cli",
        ],
    },
)
