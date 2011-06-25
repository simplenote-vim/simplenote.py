#!/usr/bin/env python
# encoding: utf-8
'''
  setup.py - distutils script
'''
import os
import sys
import simplenote

from distutils.core import setup

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
      license = "MIT",
      classifiers = (
          "Development Status :: 4 - Beta",
          "License :: OSI Approved :: MIT License",
          "Programming Language :: Python",
          "Programming Language :: Python :: 2.6",
          "Programming Language :: Python :: 2.7",
      )
     )
