#!/usr/bin/env python
# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010-2011>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import os
from lettuce import version
from setuptools import setup

def get_packages():
    # setuptools can't do the job :(
    packages = []
    for root, dirnames, filenames in os.walk('lettuce'):
        if '__init__.py' in filenames:
            packages.append(".".join(os.path.split(root)).strip("."))

    return packages

setup(name='lettuce',
    version=version,
    description='Behaviour Driven Development for python',
    author=u'Gabriel Falcao',
    author_email='gabriel@nacaolivre.org',
    url='http://github.com/gabrielfalcao/lettuce',
    packages=get_packages(),
    entry_points = {
    	'console_scripts' : [
	    'lettuce = lettuce.lettuce_cli:main',
	]}
)
