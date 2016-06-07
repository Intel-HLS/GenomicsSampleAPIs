
from setuptools import setup, find_packages

from codecs import open
from os import path

setup(
    name='variantstore',

    version='0.0.1',

    description='SQLAlchemy models for the Variant Database',
    long_description='SQLAlchemy models for the Variant Database',

    url='https://github.com/Intel-HSS/store',

    author='Intel variant store',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='variant database',

    packages=['utils', 'metadb.models', 'metadb.api', 'python_api'],

    install_requires=['sqlalchemy'],

    extras_require={
        'dev': [],
        'test': [],
    },
)
