'''Setup Script for Garbage Arcade'''

import os
from setuptools import setup

project_dir = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(project_dir, 'requirements.txt'), 'r') as f:
    REQS = f.readlines()

with open(os.path.join(project_dir, 'README.md'), 'r') as f:
    README = f.read()

setup(
    name="Garbage Arcade",
    version="1.0.0",
    description="Garbage Card Game",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/mistergates/GarbageCardGame",
    author="Mitch Gates",
    author_email="gates55434@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
    packages=["garbage_arcade"],
    include_package_data=True,
    install_requires=REQS
)
