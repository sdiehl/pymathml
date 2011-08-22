#!/usr/bin/env python

from distutils.core import setup

setup(name="pymathml",
      version="0.3", # keep in sync with mathml/__init__.py
      description="Python MathML renderer",
      author="Gustavo J. A. M. Carneiro",
      author_email="gustavo@users.sourceforge.net",
      url="http://pymathml.sf.net",
      license="LGPL",
      packages=['mathml', 'mathml.xml', 'mathml.backend'])

