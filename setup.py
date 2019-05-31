#!/usr/bin/env python
"""
pip setup file
"""
from qoo.globals import __version__
from setuptools import setup


with open("README.rst") as readme:
    LONG_DESCRIPTION = readme.read()


setup(
    name="qoo",
    version=__version__,
    description=("A powerful but simple job queue wrapper around SQS."),
    long_description=LONG_DESCRIPTION,
    author="Jacobi Petrucciani",
    author_email="jacobi@mimirhq.com",
    url="https://github.com/jpetrucciani/qoo.git",
    download_url="https://github.com/jpetrucciani/qoo.git",
    license="LICENSE",
    packages=["qoo"],
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    zip_safe=False,
)
