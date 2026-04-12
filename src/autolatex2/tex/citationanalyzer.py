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
Tools for extracting the bibliography citations from AUX file or BSF file.
"""

import os
import re
from hashlib import md5
from typing import override, Any, Callable

from sortedcontainers import SortedSet

from autolatex2.tex.texobservers import Observer
from autolatex2.tex.texparsers import TeXParser, Parser
from autolatex2.tex.utils import TeXMacroParameter

# noinspection DuplicatedCode
EXPAND_REGISTRY : dict[str, Callable[[Any, list[TeXMacroParameter]], None]] = dict()

def expand_function(func : Callable) -> Callable:
	"""
	Decorator to register functions with __expand__ prefix.
	:param func: The function to be marked
	:type func: Callable
	:return: the function.
	:rtype: Callable
	"""
	# Store the function and its metadata
	# Remove "_expand__" prefix
	if not func.__name__.startswith('_expand__'):
		raise NameError('Function name must start with \'_expand__\'')
	func_name = str(func.__name__)[9:]
	EXPAND_REGISTRY[func_name] = func
	return func

class AuxiliaryCitationAnalyzer(Observer):
	"""
	Observer on TeX parsing extracting the bibliography citations from AUX file.
	"""

	__MACROS : dict[str,str] = {
		'citation'	: '![]!{}',
		'bibcite'	: '![]!{}!{}',
		'bibdata'	: '![]!{}',
		'bibstyle'	: '![]!{}',
	}

	def __init__(self, filename : str):
		"""
		Constructor.
		:param filename: The name of the file to parse.
		:type filename: str
		"""
		self.__expand_registry = EXPAND_REGISTRY
		self.__filename : str = filename
		self.__basename : str = os.path.basename(os.path.splitext(filename)[0])
		self.__databases : set[str] = set()
		self.__styles : set[str] = set()
		self.__citations_computed : bool = False
		self.__citations : SortedSet = SortedSet()
		self.__md5 : str | None = None

	@property
	def databases(self) -> set[str]:
		"""
		Replies the databases that were specified in the AUX file.
		:return: the set of databases.
		:rtype: set[str]
		"""
		return self.__databases

	@property
	def styles(self) -> set[str]:
		"""
		Replies the bibliography styles that were specified in the AUX file.
		:return: the set of styles.
		:rtype: set[str]
		"""
		return self.__styles

	@property
	def citations(self) -> SortedSet:
		"""
		Replies the bibliography citations that were specified in the AUX file.
		:return: the set of citations.
		:rtype: SortedSet
		"""
		return self.__citations

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

	@property
	def md5(self) -> str:
		"""
		Parse the aux file, extract the bibliography citations, and build a MD5.
		:return: the MD5 of the citations.
		"""
		if self.__md5 is None:
			if not self.__citations_computed:
				self.__citations_computed = True
				self.run()
			self.__md5 = md5(bytes('\\'.join(self.citations), 'UTF-8')).hexdigest()
		assert self.__md5 is not None, "MD5 is none"
		return self.__md5

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
		:type parameters: dict[str,str]
		:return: the result of expansion of the macro, or None to not replace the macro by something (the macro is used as-is)
		:rtype: str
		"""
		if name.startswith('\\'):
			callback_name = name[1:]
			if callback_name in self.__expand_registry:
				func = self.__expand_registry[callback_name]
				func(self, list(parameters))
		return ''

	@expand_function
	def _expand__citation(self, parameters : list[TeXMacroParameter]):
		assert len(parameters) > 1, "Invalid parameters for \\citation: %s" % str(parameters)
		if parameters[1].text:
			for bibkey in re.split(r'\s*,\s*', parameters[1].text):
				if bibkey:
					self.__citations.add(bibkey)

	@expand_function
	def _expand__bibcite(self, parameters : list[TeXMacroParameter]):
		assert len(parameters) > 1, "Invalid parameters for \\bibcite: %s" % str(parameters)
		if parameters[1].text:
			for bibkey in re.split(r'\s*,\s*', parameters[1].text):
				if bibkey:
					self.__citations.add(bibkey)

	@expand_function
	def _expand__bibdata(self, parameters : list[TeXMacroParameter]):
		assert len(parameters) > 1, "Invalid parameters for \\bibdata: %s" % str(parameters)
		if parameters[1].text:
			for bibdb in re.split(r'\s*,\s*', parameters[1].text):
				if bibdb:
					self.__databases.add(bibdb)

	@expand_function
	def _expand__bibstyle(self, parameters : list[TeXMacroParameter]):
		assert len(parameters) > 1, "Invalid parameters for \\bibstyle: %s" % str(parameters)
		if parameters[1].text:
			for bibst in re.split(r'\s*,\s*', parameters[1].text):
				if bibst:
					self.__styles.add(bibst)

	# noinspection DuplicatedCode
	def run(self):
		"""
		Run the process for extracting the data from the AUX file.
		"""
		self.__citations = SortedSet()
		if os.path.isfile(self.filename):
			with open(self.filename) as f:
				content = f.read()

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






class BiblatexCitationAnalyzer(Observer):
	"""
	Observer on TeX parsing extracting the bibliography citations from a BCF (biblatex) file.
	"""

	def __init__(self, filename : str):
		"""
		Constructor.
		:param filename: The name of the file to parse.
		:type filename: str
		"""
		self.__filename : str = filename
		self.__basename : str = os.path.basename(os.path.splitext(filename)[0])
		self.__citations : SortedSet | None = None
		self.__md5 : str | None = None

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

	@property
	def citations(self) -> SortedSet:
		"""
		Replies the bibliography citations that were specified in the BCF file.
		:return: the set of citations.
		:rtype: set
		"""
		if self.__citations is None:
			self.__citations = SortedSet()
		assert self.__citations is not None, "Citations is none"
		return self.__citations

	@property
	def md5(self) -> str:
		"""
		Parse the bcf file, extract the bibliography citations, and build a MD5.
		:return: the MD5 of the citations.
		"""
		if self.__md5 is None:
			if self.__citations is None:
				self.run()
			self.__md5 = md5(bytes('\\'.join(self.citations), 'UTF-8')).hexdigest()
		assert self.__md5 is not None, "MD5 is none"
		return self.__md5

	# noinspection DuplicatedCode
	def run(self):
		"""
		Extract the data from the BCF file.
		"""
		if os.path.isfile(self.filename):
			with open(self.filename) as f:
				content = f.read()
			citations = SortedSet()
			for citation in re.findall(re.escape('<bcf:citekey>') + '(.+?)' + re.escape('</bcf:citekey>'), content,
									   re.DOTALL):
				citations.add(citation)
			self.__citations = citations
		else:
			self.__citations = SortedSet()


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

	@override
	def expand(self, parser: Parser, raw_text: str, name: str, *parameter: TeXMacroParameter) -> str | None:
		return None

