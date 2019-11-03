#!/usr/bin/env python
"""This module implements build settings."""

from setuptools import setup
from setuptools import find_packages


def main():
    """This function implements build settings."""
    with open('README.md', 'r', encoding='utf8') as file:
        readme = file.read()

    setup(
        name='mediaarchiver',
        version='0.0.0',
        description='This project helps you to archive media file.',
        long_description=readme,
        long_description_content_type='text/markdown',
        author='Road Master',
        author_email='roadmasternavi@gmail.com',
        packages=find_packages(exclude=("tests*",)),
        package_data={"mediaarchiver": ["py.typed"]},
        install_requires=[
            'parallelmediadownloader',
            'parallelhtmlscraper',
            'Pillow',
            'pyyaml',
            'yamldataclassconfig',
        ],
        url="https://github.com/road-master/media-archiver",
        keywords="media archive",
    )


if __name__ == '__main__':
    main()
