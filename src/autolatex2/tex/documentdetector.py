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
Tools that is parsing a TeX file and detect if \\documentclass is inside.
"""
from typing import override

from autolatex2.tex.texobservers import Observer
from autolatex2.tex.texparsers import Parser
from autolatex2.tex.texparsers import TeXParser
from autolatex2.tex.utils import TeXMacroParameter


class DocumentDetector(Observer):
	"""
	Observer on TeX parsing for detecting the documentclass macro inside a file.
	"""

	def __init__(self, filename : str | None = None, text : str | None = None, lineno : int = 1):
		"""
		Constructor.
		:param filename: The name of the file.
		:type filename: str
		:param text: The text to parse. If None, the text is extracted from the file with the given name.
		:type text: str
		:param lineno: The number of the first line.
		:type lineno: int
		"""
		self.__filename : str | None = filename
		if text is None and self.__filename:
			with open(self.__filename, 'rb') as f:
				self.__content : str = f.read().decode('UTF-8')
		else:
			self.__content : str = text or ''
		self.__lineno : int = lineno
		self.__latex_document : bool = False

	@property
	def latex(self) -> bool:
		"""
		Replies if the parsed document is a LaTeX document.
		:return: True if the document contains the documentclass macro; False otherwise.
		:rtype: bool
		"""
		return self.__latex_document

	@latex.setter
	def latex(self, l : bool):
		"""
		Set if the parsed document is a LaTeX document.
		:param l: True if the document contains the documentclass macro; False otherwise.
		:type: bool
		"""
		self.__latex_document = l

	@property
	def filename(self) -> str:
		"""
		Replies if filename that is parsed.
		:return: The filename.
		:rtype: str
		"""
		return self.__filename or ''

	@filename.setter
	def filename(self, n : str):
		"""
		Replies if filename that is parsed.
		:param n: The filename.
		:type n: str
		"""
		self.__filename = n

	@override
	def expand(self, parser : Parser, raw_text : str, name : str, *parameters : TeXMacroParameter) -> str | None:
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
		if name == '\\documentclass':
			self.latex = True
			parser.stop()
		return None

	def run(self):
		"""
		Determine if the given string is a LaTeX document, i.e., it contains the \\documentclass macro.
		"""
		self.latex = False
		if self.__content:
			parser = TeXParser()
			parser.observer = self
			parser.filename = self.filename
			parser.add_text_mode_macro('documentclass', '![]!{}')
			parser.add_math_mode_macro('documentclass', '![]!{}')
			parser.parse(self.__content, self.__lineno)

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

