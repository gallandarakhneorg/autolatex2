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
TeX parser.
"""

class Parameter:
	"""
	Definition of a parameter for a macro.
	"""

	def __init__(self):
		"""
		Construct an expandable parameter.
		"""
		self.__expandable = True
		self.__value = None

	@property
	def expandable(self) -> bool:
		"""
		Indicates if the value of the parameter must be expanded.
		:return: True if the parameter must be expanded; False otherwise.
		:rtype: bool
		"""
		return self.__expandable

	@expandable.setter
	def expandable(self, e : bool):
		"""
		Change the flag indicating if the value of the parameter must be expanded.
		:param e: True if the parameter must be expanded; False otherwise.
		:type e: bool
		"""
		self.__expandable = e

	@property
	def value(self) -> str:
		"""
		The value of the argument.
		:return: The value of the argument.
		:rtype: str
		"""
		return self.__value

	@value.setter
	def value(self, v : str):
		"""
		Set the value of the argument.
		:param v: The value.
		:type v: str
		"""
		self.__value = v
