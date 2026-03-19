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
Tools that is extracting the dependencies of the TeX file.
"""

import os
import re
from typing import override, Any

from autolatex2.tex.texobservers import Observer
from autolatex2.tex.texparam import Parameter
from autolatex2.tex.texparsers import Parser
from autolatex2.tex.texparsers import TeXParser
from autolatex2.tex import utils

class DependencyAnalyzer(Observer):
	"""
	Observer on TeX parsing for extracting the dependencies of the TeX file.
	"""

	__MACROS : dict[str,str] = {
		'input'						: '!{}',
		'include'					: '!{}',
		'makeindex'					: '',
		'printindex'				: '',
		'usepackage'				: '![]!{}',
		'RequirePackage'			: '![]!{}',
		'documentclass'				: '![]!{}',
		'addbibresource'			: '![]!{}',
		'makeglossaries'			: '',
		'printglossaries'			:'',
		'newglossaryentry'			:'![]!{}',
	}

	def __init__(self, filename : str, root_directory : str):
		"""
		Constructor.
		:param filename: The name of the file to parse.
		:type filename: str
		:param root_directory: The name of the root directory.
		:type root_directory: str
		"""
		self.__is_multibib = False
		self.__is_biblatex = False
		self.__is_biber = False
		self.__is_index = False
		self.__is_xindy = False
		self.__is_glossary = False
		self.__dependencies = {}
		self.__filename = filename
		self.__basename = os.path.basename(os.path.splitext(filename)[0])
		self.__root_directory = root_directory

	@property
	def root_directory(self) -> str:
		"""
		Replies the root directory of the document.
		:return: The root directory of the document.
		:rtype: str
		"""
		return self.__root_directory

	@root_directory.setter
	def root_directory(self, d : str):
		"""
		Set the root directory of the document.
		:param d: The root directory of the document.
		:type d: str
		"""
		self.__root_directory = d

	@property
	def basename(self) -> str:
		"""
		Replies the basename of the document.
		:return: The basename  of the document.
		:rtype: str
		"""
		return self.__basename

	@basename.setter
	def basename(self, n : str):
		"""
		Set the basename of the document.
		:param n: The basename of the document.
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
		Set the filename of the parsed document.
		:param n: The filename of the parsed document.
		:type n: str
		"""
		self.__filename = n

	@property
	def is_multibib(self) -> bool:
		"""
		Replies the multibib support is enable
		:return: True if the multibib support is enabled.
		:rtype: bool
		"""
		return self.__is_multibib

	@is_multibib.setter
	def is_multibib(self, enable : bool):
		"""
		Set if the multibib support is enable
		:param enable: True if the multibib support is enabled.
		:type enable: bool
		"""
		self.__is_multibib = enable

	@property
	def is_biblatex(self) -> bool:
		"""
		Replies the biblatex support is enable
		:return: True if the biblatex support is enabled.
		:rtype: bool
		"""
		return self.__is_biblatex

	@is_biblatex.setter
	def is_biblatex(self, enable : bool):
		"""
		Set if the biblatex support is enable
		:param enable: True if the biblatex support is enabled.
		:type enable: bool
		"""
		self.__is_biblatex = enable

	@property
	def is_biber(self) -> bool:
		"""
		Replies the biber support is enable
		:return: True if the biber support is enabled.
		:rtype: bool
		"""
		return self.__is_biber

	@is_biber.setter
	def is_biber(self, enable : bool):
		"""
		Set if the biber support is enable
		:param enable: True if the biber support is enabled.
		:type enable: bool
		"""
		self.__is_biber = enable

	@property
	def is_makeindex(self) -> bool:
		"""
		Replies the makeindex support is enable
		:return: True if the makeindex support is enabled.
		:rtype: bool
		"""
		return self.__is_index

	@is_makeindex.setter
	def is_makeindex(self, enable : bool):
		"""
		Set if the makeindex support is enable
		:param enable: True if the makeindex support is enabled.
		:type enable: bool
		"""
		self.__is_index = enable

	@property
	def is_xindy_index(self) -> bool:
		"""
		Replies if the support for xindy support is enable.
		This flag is considered only if is_makeindex is enable.
		:return: True if the xindy support is enabled.
		:rtype: bool
		"""
		return self.__is_xindy

	@is_xindy_index.setter
	def is_xindy_index(self, enable : bool):
		"""
		Set if the support for xindy support is enable.
		This flag is considered only if is_makeindex is enable.
		:param enable: True if the xindy support is enabled.
		:type enable: bool
		"""
		self.__is_xindy = enable

	@property
	def is_glossary(self) -> bool:
		"""
		Replies the glossary support is enable
		:return: True if the glossary support is enabled.
		:rtype: bool
		"""
		return self.__is_glossary

	@is_glossary.setter
	def is_glossary(self, enable : bool):
		"""
		Set if the glossary support is enable
		:param enable: True if the glossary support is enabled.
		:type enable: bool
		"""
		self.__is_glossary = enable

	def __add_dependency(self, dependency_type : str, dependency_file : str):
		"""
		Add a dependency.
		:param dependency_type: The type of the dependency (tex, bib, ...)
		:type dependency_type: str
		:param dependency_file: The filename.
		:type dependency_file: str
		"""
		if dependency_type not in self.__dependencies:
			s = set()
			s.add(dependency_file)
			self.__dependencies[dependency_type] = s
		else:
			self.__dependencies[dependency_type].add(dependency_file)

	def get_dependency_types(self) -> set[str]:
		"""
		Replies the dependency types.
		:return: the set of dependency types.
		:rtype: set[str]
		"""
		the_set = set(self.__dependencies.keys())
		if 'biblio' in the_set:
			the_set.remove('biblio')
		return the_set

	def get_dependencies(self, dependency_type : str) -> set[str] | dict[str,dict[str,set[str]]]:
		"""
		Replies the dependencies of the given type.
		:param dependency_type: The type of the dependency (tex, bib, ...)
		:type dependency_type: str
		:return: the set of dependencies. The set of dependency names is the more used form. The dictionary of dictionary is usually used for bibliography dependencies.
		:rtype: set[str] | dict[str,dict[str,set[str]]]
		"""
		if dependency_type in self.__dependencies:
			return self.__dependencies[dependency_type]
		return set()

	def get_bib_dependencies(self, bib_type : str, bib_database : str = '') -> set[str]:
		"""
		Replies the bibliography dependencies of the given type.
		:param bib_type: The type of the dependency (bbx, ...)
		:type bib_type: str
		:param bib_database: The name of the bibliography database.
		:type bib_database: str
		:return: the set of dependencies.
		:rtype: set[str]
		"""
		if 'biblio' in self.__dependencies:
			hash1 = self.__dependencies['biblio']
			if bib_database in hash1:
				hash2 = hash1[bib_database]
				if bib_type in hash2:
					return hash2[bib_type]
		return set()

	def get_bib_databases(self) -> set[str]:
		"""
		Replies the set of bibliography databases
		:return: the set of bibliography database.
		:rtype: set[str]
		"""
		if 'biblio' in self.__dependencies:
			hash1 = self.__dependencies['biblio']
			return hash1.keys()
		return set()

	def __add_bib_dependency(self, bib_type : str, dependency_file : str, db_name : str = ''):
		"""
		Add a dependency.
		:param bib_type: The type of the dependency (bbx, ...)
		:type bib_type: str
		:param dependency_file: The filename.
		:type dependency_file: str
		:param db_name: The name of the bibliography database (default: )
		:type db_name: str
		"""
		if 'biblio' not in self.__dependencies:
			hash1 = {}
			self.__dependencies['biblio'] = hash1
		else:
			hash1 = self.__dependencies['biblio']
		if db_name not in hash1:
			hash2 = {}
			hash1[db_name] = hash2
		else:
			hash2 = hash1[db_name]
		if bib_type not in hash2:
			the_set = set()
			hash2[bib_type] = the_set
		else:
			the_set = hash2[bib_type]
		the_set.add(dependency_file)

	def __parse_bib_reference(self, bib_db : str, *files : Parameter):
		"""
		Add a dependency to a BibTeX database.
		:param bib_db: the BibTeX database.
		:type bib_db: str
		:param files: the BibTeX files.
		:type files: str
		"""
		for param in files:
			value = param['text']
			if value:
				for svalue in re.split(r'\s*,\s*', value):
					if svalue:
						if svalue.endswith('.bib'):
							bib_file = svalue
						else:
							bib_file = svalue + '.bib'
						if not os.path.isabs(bib_file):
							bib_file = os.path.join(self.root_directory, bib_file)
						if os.path.isfile(bib_file):
							self.__add_bib_dependency('bib', bib_file, bib_db)

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
		:type parameter: dict[str,Any]
		:return: the result of the expand of the macro, or None to not replace the macro by something (the macro is used as-is)
		:rtype: str
		"""
		if name == '\\include' or name == '\\input':
			for param in parameter:
				value = param['text']
				if value:
					if utils.is_tex_document(value):
						tex_file = value
					else:
						tex_file = value + utils.get_tex_file_extensions()[0]
					if not os.path.isabs(tex_file):
						tex_file = os.path.join(self.root_directory, tex_file)
					if os.path.isfile(tex_file):
						self.__add_dependency('tex', tex_file)
		elif name == '\\makeindex' or name == '\\printindex':
			self.is_makeindex = True
		elif name == '\\makeglossaries' or name == '\\printglossaries' or name == '\\newglossaryentry':
			self.is_glossary = True
		elif name == '\\usepackage' or name == '\\RequirePackage':
			sty = parameter[1]['text']
			if sty.endswith('.sty'):
				sty_file = sty
			else:
				sty_file = sty + ".sty"
			if sty_file == 'multibib.sty':
				self.is_multibib = True
			elif sty_file == 'biblatex.sty':
				self.is_biblatex = True
				# Parse the biblatex parameters
				if parameter[0] and parameter[0]['text']:
					params = re.split(r'\s*,\s*', (parameter[0]['text'] or '').strip())
					for p in params:
						r = re.match(r'^([^=]+)\s*=\s*(.*?)\s*$', p, re.DOTALL)
						if r:
							k = r.group(1)
							v = r.group(2) or ''
						else:
							k = p
							v = ''
						if k == 'backend':
							self.is_biber = (v == 'biber')
						elif k == 'style':
							if v.endswith('.bbx'):
								bbx_file = v
							else:
								bbx_file = v + ".bbx"
							if not os.path.isabs(bbx_file):
								bbx_file = os.path.join(self.root_directory, bbx_file)
							if os.path.isfile(bbx_file):
								self.__add_bib_dependency('bbx', bbx_file)
							if v.endswith('.cbx'):
								cbx_file = v
							else:
								cbx_file = v + ".cbx"
							if not os.path.isabs(cbx_file):
								cbx_file = os.path.join(self.root_directory, cbx_file)
							if os.path.isfile(cbx_file):
								self.__add_bib_dependency('cbx', cbx_file)
						elif k == 'bibstyle':
							if v.endswith('.bbx'):
								bbx_file = v
							else:
								bbx_file = v + ".bbx"
							if not os.path.isabs(bbx_file):
								bbx_file = os.path.join(self.root_directory, bbx_file)
							if os.path.isfile(bbx_file):
								self.__add_bib_dependency('bbx', bbx_file)
						elif k == 'citestyle':
							if v.endswith('.cbx'):
								cbx_file = v
							else:
								cbx_file = v + '.cbx'
							if not os.path.isabs(cbx_file):
								cbx_file = os.path.join(self.root_directory, cbx_file)
							if os.path.isfile(cbx_file):
								self.__add_bib_dependency('cbx', cbx_file)
			elif sty_file == 'indextools.sty':
				if parameter[0] and parameter[0]['text'] and 'xindy' in parameter[0]['text']:
					self.is_xindy_index = True
			elif sty_file == 'glossaries.sty':
				self.is_glossary = True
			else:
				if not os.path.isabs(sty_file):
					sty_file = os.path.join(self.root_directory, sty_file)
				if os.path.isfile(sty_file):
					self.__add_dependency('sty', sty_file)
		elif name == '\\documentclass':
			cls = parameter[1]['text']
			if cls.endswith('.cls'):
				cls_file = cls
			else:
				cls_file = cls + '.cls'
			if not os.path.isabs(cls_file):
				cls_file = os.path.join(self.root_directory, cls_file)
			if os.path.isfile(cls_file):
				self.__add_dependency('cls', cls_file)
		else:
			if name.startswith('\\bibliographystyle'):
				if not self.is_multibib:
					bibdb = self.basename
				else:
					bibdb = name[18:] if len(name) > 18 else self.basename
				for param in parameter:
					value = param['text']
					if value:
						for svalue in re.split('\\s*,\\s*',value.strip()):
							if svalue:
								if svalue.endswith('.bst'):
									bst_file = svalue
								else:
									bst_file = svalue + '.bst'
								if not os.path.isabs(bst_file):
									bst_file = os.path.join(self.root_directory, bst_file)
								if os.path.isfile(bst_file):
									self.__add_bib_dependency('bst', bst_file, bibdb)
			elif name.startswith('\\bibliography'):
				if not self.is_multibib:
					bibdb = self.basename
				else:
					bibdb = name[13:] if len(name) > 13 else self.basename
				self.__parse_bib_reference(bibdb, *parameter)
			elif name == '\\addbibresource':
				bibdb = self.basename
				self.__parse_bib_reference(bibdb, *parameter)
		return ''

	@override
	def find_macro(self, parser : Parser, name : str, special : bool, math : bool) -> str | None:
		"""
		Invoked each time a macro definition is not found in the parser data.
		:param parser: reference to the parser.
		:type parser: Parser
		:param name: Name of the macro.
		:type name: str
		:param special: Indicates if the macro is a special macro or not.
		:type special: bool
		:param math: Indicates if the math mode is active.
		:type math: bool
		:return: the definition of the macro, ie. the macro prototype. See the class documentation for an explanation about the format of the macro prototype.
		:rtype: str
		"""
		if not special:
			if name.startswith('bibliographystyle'):
				return '!{}'
			elif name.startswith('bibliography'):
				return '!{}'
		return None

	def run(self):
		"""
		Detect the dependencies.
		"""
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
