#!/usr/bin/env python3
import os
import sys
import shutil
import setuptools

# Workaround issue in pip with "pip install -e --user ."
import site
site.ENABLE_USER_SITE = True

with open("README.rst", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="thorlabs_elliptec",
    version="1.1.0",
    author="Patrick Tapping",
    author_email="mail@patricktapping.com",
    description="Interface to ThorLabs Elliptec piezo-driven motion stages and mounts.",
    long_description=long_description,
    url="https://gitlab.com/ptapping/thorlabs-elliptec",
    project_urls={
        "Documentation": "https://thorlabs-elliptec.readthedocs.io/",
        "Source": "https://gitlab.com/ptapping/thorlabs-elliptec",
        "Tracker": "https://gitlab.com/ptapping/thorlabs-elliptec/-/issues",
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "pyserial",
    ],
)
