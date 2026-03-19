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
Extension of the printing API.
"""

import sys
import pprint
from typing import Any

"""
Global variable that enables to switch from the standard output to the standard error output. 
"""
IS_STANDARD_OUTPUT : bool = True

"""
Global variable that enables or disables the output functions from this module. 
"""
IS_ACTIVATED : bool = True


def eprint(*args : Any, **kwargs : Any):
	"""
	Print the arguments on the selected output (standard output, standard error output).
	"""
	global IS_ACTIVATED
	if IS_ACTIVATED:
		global IS_STANDARD_OUTPUT
		if IS_STANDARD_OUTPUT:
			print(*args,  file=sys.stdout, **kwargs)
		else:
			print(*args,  file=sys.stderr, **kwargs)

def epprint(value : Any):
	"""
	Pretty print the arguments on the selected output (standard output, standard error output).
	"""
	pp = pprint.PrettyPrinter(indent=2)
	fmt = pp.pformat(value)
	eprint(fmt)

