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
from typing import override, Any

from autolatex2.tex.texobservers import Observer
from autolatex2.tex.texparsers import TeXParser, Parser


class AuxiliaryCitationAnalyzer(Observer):
	"""
	Observer on TeX parsing extracting the bibliography citations from AUX file.
	"""

	__MACROS : dict[str,str] = {
		'citation'	: '[]!{}',
		'bibcite'	: '[]!{}',
		'bibdata'	: '[]!{}',
		'bibstyle'	: '[]!{}',
	}

	def __init__(self, filename : str):
		"""
		Constructor.
		:param filename: The name of the file to parse.
		:type filename: str
		"""
		self.__filename = filename
		self.__basename = os.path.basename(os.path.splitext(filename)[0])
		self.__databases = set()
		self.__styles = set()
		self.__citations = None
		self.__md5 = None

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
		:return: the set of styls.
		:rtype: set[str]
		"""
		return self.__styles

	@property
	def citations(self) -> set[str]:
		"""
		Replies the bibliography citations that were specified in the AUX file.
		:return: the set of citations.
		:rtype: set[str]
		"""
		if self.__citations is None:
			return set()
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
			if self.__citations is None:
				self.run()
			self.__md5 = md5(bytes('\\'.join(self.citations), 'UTF-8')).hexdigest()
		return self.__md5

	@override
	def expand(self, parser : Parser, raw_text : str, name : str, *parameter : dict[str,Any]) -> str:
		"""
		Expand the given macro on the given parameters.
		:param parser: reference to the parser.
		:type parser: Parser
		:param raw_text: The raw text that is the source of the expansion.
		:type raw_text: str
		:param name: Name of the macro.
		:type name: str
		:param parameter: Descriptions of the values passed to the TeX macro.
		:type parameter: dict[str,str]
		:return: the result of expansion of the macro, or None to not replace the macro by something (the macro is used as-is)
		:rtype: str
		"""
		if name == '\\bibdata':
			if parameter and len(parameter) > 1 and 'text' in parameter[1] and parameter[1]['text']:
				for bibdb in re.split(r'\s*,\s*', parameter[1]['text']):
					if bibdb:
						self.__databases.add(bibdb)
		elif name == '\\bibstyle':
			if parameter and len(parameter) > 1 and 'text' in parameter[1] and parameter[1]['text']:
				for bibdb in re.split(r'\s*,\s*', parameter[1]['text']):
					if bibdb:
						self.__styles.add(bibdb)
		elif parameter and len(parameter) > 1 and 'text' in parameter[1] and parameter[1]['text']:
			for bibdb in re.split(r'\s*,\s*', parameter[1]['text']):
				if bibdb:
					self.__citations.add(bibdb)
		return ''

	# noinspection DuplicatedCode
	def run(self):
		"""
		Run the process for extracting the data from the AUX file.
		"""
		with open(self.filename) as f:
			content = f.read()

		self.__citations = set()

		parser = TeXParser()
		parser.observer = self
		parser.filename = self.filename

		for k, v in self.__MACROS.items():
			parser.add_text_mode_macro(k, v)
			parser.add_math_mode_macro(k, v)

		parser.parse(content)

		self.__citations = sorted(self.__citations)

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
		self.__filename = filename
		self.__basename = os.path.basename(os.path.splitext(filename)[0])
		self.__citations = None
		self.__md5 = None

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
	def citations(self) -> set:
		"""
		Replies the bibliography citations that were specified in the BCF file.
		:return: the set of citations.
		:rtype: set
		"""
		if self.__citations is None:
			return set()
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
		return self.__md5

	def run(self):
		"""
		Extract the data from the BCF file.
		"""
		with open(self.filename) as f:
			content = f.read()

		citations = set()

		for citation in re.findall(re.escape('<bcf:citekey>') + '(.+?)' + re.escape('</bcf:citekey>'), content, re.DOTALL):
			citations.add(citation)

		self.__citations = sorted(citations)

	def text(self, parser: Parser, text: str):
		pass

	def comment(self, parser: Parser, raw: str, comment: str) -> str | None:
		return None

	def open_block(self, parser: Parser, text: str) -> str | None:
		return None

	def close_block(self, parser: Parser, text: str) -> str | None:
		return None

	def open_math(self, parser: Parser, inline: bool) -> str | None:
		return None

	def close_math(self, parser: Parser, inline: bool) -> str | None:
		return None

	def find_macro(self, parser: Parser, name: str, special: bool, math: bool) -> str | None:
		return None

	def expand(self, parser: Parser, raw_text: str, name: str, *parameter: dict[str, Any]) -> str | None:
		return None

