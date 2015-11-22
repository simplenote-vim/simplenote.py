#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
  setup.py - distutils script
'''
import os
import sys
import simplenote

from distutils.core import setup

requires = []

if sys.version_info[:2] < (2,6):
    requires.append('simplejson')

def publish():
    """ Publish to PyPi"""
    os.system("python setup.py sdist upload")

if sys.argv[-1] == "publish":
    publish()
    sys.exit()

setup(name = "simplenote",
      version = simplenote.__version__,
      description = "Python library for the simplenote.com API",
      long_description = (open("README.rst").read() + "\n\n" + open("HISTORY.rst").read()),
      author = "Daniel Schauenberg",
      author_email = "d@unwiredcouch.com",
      url = "https://github.com/mrtazz/simplenote.py",
      packages = ["simplenote"],
      install_requires=requires,
      license = "MIT",
      classifiers = (
          "Development Status :: 5 - Production/Stable",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2",
          "Programming Language :: Python :: 3"
      )
     )
