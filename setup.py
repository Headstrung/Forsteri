"""
"""

# Import modules.
from setuptools import setup, find_pachages
from codecs import open
from os import path

# Find the path to this file.
here = path.abspath(path.dirname(__file__))

# Get the long description from the relevant file.
with open(path.join(here, "DESCRIPTION.rst"), encoding="utf-8" as f):
    long_description = f.read()

# 
setup(
    name="Forsteri",
    version="0.0.1",
    description="Data management and forecasting software.",
    url="https://github.com/Headstrung/Forsteri",
    author="Andrew Hawkins",
    author_email="andrewh@pqmfg.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Intended Audience :: Manufacturing",
        "Intended Audience :: Science/Research",
        "Topic :: Office/Business :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
        "Programming Language :: Python :: 2.7"
    ],
    keywords="forecasting manufacturing supply chain data management",
    packages=find_packages(exclude=["data", "doc"]),
    install_requires=[
        "wx",
        "webbrowser",
        "threading",
        "subprocess",
        "sqlite3",
        "copy",
        "pickle",
        "datetime",
        "sys",
        "re",
        "csv",
        "operator",
        "numpy"
    ],
    package_data{
        
    }
)
