#!/usr/bin/env python
from setuptools import setup, find_packages
from media_albums import __version__

setup(
    name='django-media-albums',
    version=__version__,
    description='A photo/video/audio albums application for Django',
    author='Velocity Webworks',
    author_email='dev@velocitywebworks.com',
    url='https://github.com/VelocityWebworks/django-media-albums',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Django>=1.8',
        'Pillow',
    ],
)
