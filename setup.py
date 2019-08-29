#!/usr/bin/env python
"""
pip setup file
"""
from setuptools import setup


with open("README.rst") as readme:
    LONG_DESCRIPTION = readme.read()


REQUIRED = ["boto3"]

setup(
    name="qoo",
    version="0.0.3",
    description=("A simple library for interacting with Amazon SQS."),
    long_description=LONG_DESCRIPTION,
    author="Jacobi Petrucciani",
    author_email="jacobi@mimirhq.com",
    url="https://github.com/jpetrucciani/qoo.git",
    download_url="https://github.com/jpetrucciani/qoo.git",
    license="MIT",
    packages=["qoo"],
    install_requires=REQUIRED,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
    zip_safe=False,
)
