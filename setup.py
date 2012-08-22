#!/usr/bin/env python
# -*- coding: utf-8 -*-
#from distutils.core import setup
from setuptools import setup


from . import irequests as target
setup(
    name=target.__name__,
    version=target.__version__,
    description=target.__doc__.splitlines()[0],
    long_description=target.__doc__,
    author=target.__author__,
    author_email=target.__author_email__,
    url=target.__url__,
    classifiers=target.__classifiers__,
    license=target.__license__,
    py_packages=[target.__name__, ],
    install_requires=getattr(target, '__install_requires__', []),
    )


