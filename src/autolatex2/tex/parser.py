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

import abc

from autolatex2.tex.mathmode import MathMode

class Parser(abc.ABC):
	"""
	Public interface of a parser.
	"""
	__metaclass__ = abc.ABCMeta

	@property
	def math_mode(self) -> MathMode:
		"""
		Replies if the math mode is active.
		:return: The math mode.
		:rtype: MathMode
		"""
		raise NotImplementedError

	@abc.abstractmethod
	def put_back(self, text : str):
		"""
		Reinject a piece of text inside the parsed text in a way that it will
		be the next text to be parsed by this object.
		:param text: The text to reinject.
		:type text: str
		"""
		raise NotImplementedError

	@abc.abstractmethod
	def stop(self):
		"""
		Stop the parsing. The function parse() will stop its current loop.
		"""
		raise NotImplementedError
