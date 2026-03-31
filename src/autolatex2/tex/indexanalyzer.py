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
Tools for that is extracting the definitions of indexes from an IDX file.
"""

import os
from hashlib import md5
from typing import override

from sortedcontainers import SortedSet

from autolatex2.tex.texobservers import Observer
from autolatex2.tex.texparsers import Parser
from autolatex2.tex.texparsers import TeXParser
from autolatex2.tex.utils import TeXMacroParameter


class IndexAnalyzer(Observer):
	"""
	Observer on TeX parsing that is extracting the definitions of indexes from an IDX file.
	"""

	__MACROS : dict[str,str] = {
		'indexentry' : '[]!{}!{}',
	}

	def __init__(self, filename : str):
		"""
		Constructor.
		:param filename: The name of the file to parse.
		:type filename: str
		"""
		self.__filename : str = filename
		self.__basename : str = os.path.basename(os.path.splitext(filename)[0])
		self.__databases = set()
		self.__indexes_computed : bool = False
		self.__indexes : SortedSet = SortedSet()
		self.__md5 : str|None = None

	@property
	def indexes(self) -> SortedSet:
		"""
		Replies the indexes that were specified in the IDX file.
		:return: the set of indexes.
		:rtype: SortedSet
		"""
		return self.__indexes

	@property
	def basename(self) -> str:
		"""
		Replies the basename of the parsed file.
		:return: The basename  of the parsed file.
		:rtype: str
		"""
		return self.__basename

	@basename.setter
	def basename(self, n : str):
		"""
		Set the basename of the parsed file.
		:param n: The basename of the parsed file.
		:type n: str
		"""
		self.__basename = n

	@property
	def filename(self) -> str:
		"""
		Replies the filename of the parsed file.
		:return: The filename of the parsed file.
		:rtype: str
		"""
		return self.__filename

	@filename.setter
	def filename(self, n : str):
		"""
		Set the filename of the parsed file.
		:param n: The filename of the parsed file.
		:type n: str
		"""
		self.__filename = n

	# noinspection DuplicatedCode
	@property
	def md5(self) -> str:
		"""
		Parse the idx file, extract the indexes, and build a MD5.
		:return: the MD5 of the indexes.
		"""
		if self.__md5 is None:
			if not self.__indexes_computed:
				self.__indexes_computed = True
				self.run()
			self.__md5 = md5(bytes('\\'.join(self.indexes), 'UTF-8')).hexdigest()
		assert self.__md5 is not None
		return self.__md5

	# noinspection DuplicatedCode
	@override
	def expand(self, parser : Parser, raw_text : str, name : str, *parameters : TeXMacroParameter) -> str:
		"""
        Expand the given macro on the given parameters.
        :param parser: reference to the parser.
        :type parser: Parser
        :param raw_text: The raw text that is the source of the expansion.
        :type raw_text: str
        :param name: Name of the macro.
        :type name: str
        :param parameters: Descriptions of the values passed to the TeX macro.
        :type parameters: dict[str,Any]
        :return: the result of expansion of the macro, or None to not replace the macro by something (the macro is used as-is)
        :rtype: str
        """
		value = []
		if len(parameters) > 2 and parameters[2].text:
			value.append(parameters[2].text)
		if len(parameters) > 1 and parameters[1].text:
			value.append(parameters[1].text)
		if len(value) > 0:
			self.__indexes.add('|'.join(value))
		return ''

	# noinspection DuplicatedCode
	def run(self):
		"""
		Extract the data from the IDX file.
		"""
		with open(self.filename) as f:
			content = f.read()

		self.__indexes = SortedSet()

		parser = TeXParser()
		parser.observer = self
		parser.filename = self.filename

		for k, v in self.__MACROS.items():
			parser.add_text_mode_macro(k, v)
			parser.add_math_mode_macro(k, v)

		parser.parse(content)

	@override
	def text(self, parser: Parser, text: str):
		pass

	@override
	def comment(self, parser: Parser, raw: str, comment: str) -> str | None:
		return None

	@override
	def open_block(self, parser: Parser, text: str) -> str | None:
		return None

	@override
	def close_block(self, parser: Parser, text: str) -> str | None:
		return None

	@override
	def open_math(self, parser: Parser, inline: bool) -> str | None:
		return None

	@override
	def close_math(self, parser: Parser, inline: bool) -> str | None:
		return None

	@override
	def find_macro(self, parser: Parser, name: str, special: bool, math: bool) -> str | None:
		return None


