#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 1998-2026 Stephane Galland <galland@arakhne.org>
#
# This program is free library; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation; either version 3 of the
# License, or any later version.
#
# This library is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; see the file COPYING.  If not,
# write to the Free Software Foundation, Inc., 59 Temple Place - Suite
# 330, Boston, MA 02111-1307, USA.

"""
Provides tools for debugging autolatex.
"""

import os
import pprint
from typing import Any

from autolatex2.utils.extprint import eprint

def dbg(*variables1 : Any, **variables2 : Any):
	"""
	Raw display the values of the given variables on the console.
	This function never returns.
	:param variables1: The list of variables to display.
	:type variables1: Any
	:param variables2: The dictionary of variables to display.
	:type variables2: Any
	"""
	dbg_print(*variables1, **variables2)
	exit(255)

def dbg_print(*variables1 : Any, **variables2 : Any):
	"""
	Raw display the values of the given variables on the console.
	:param variables1: The list of variables to display.
	:type variables1: Any
	:param variables2: The dictionary of variables to display.
	:type variables2: Any
	"""
	pp = pprint.PrettyPrinter(indent=2)
	if variables1: pp.pprint(variables1)
	if variables2: pp.pprint(variables2)

def dbg_struct(var : Any):
	"""
	Raw display the value structure of the given variable on the console.
	This function never returns.
	:param var: The variable to display.
	:type var: Any
	"""
	eprint ([var.__class__])
	eprint (dir(var))
	exit(255)

def dbg_showfolder(folder : str, recursive : bool = False):
	"""
	Print the content of a folder.
	The output is similar to the 'ls -lR' command line on Unix systems.
	:param folder: The name of the folder to display.
	:type folder: str
	:param recursive: Indicates if the subfolders are also displayed (default: False).
	:type recursive: bool
	"""
	eprint()
	for dirname, dir_names, filenames in os.walk(folder):
		eprint(["%s:" % dirname])

		# print path to all subdirectories first.
		for subdirname in dir_names:
			eprint(["%s/" % subdirname])

		# print path to all filenames.
		for filename in filenames:
			eprint([filename])

		if recursive:
			for subdirname in dir_names:
				full_path = os.path.join(dirname, subdirname)
				eprint()
				dbg_showfolder(full_path, recursive)

