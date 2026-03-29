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
from typing import override, Any, Callable

from autolatex2.tex.texobservers import Observer
from autolatex2.tex.texparsers import Parser
from autolatex2.tex.texparsers import TeXParser
from autolatex2.tex import utils

FULL_EXPAND_REGISTRY : dict[str, Callable[[Any, str, tuple[dict[str, Any], ...]], None]] = dict()

PREFIX_EXPAND_REGISTRY : dict[str, Callable[[Any, str, tuple[dict[str, Any], ...]], None]] = dict()


# noinspection DuplicatedCode
def expand_function(start_symbol : bool):
	"""
	Decorator to register functions with __expand__ prefix.
	:param start_symbol: Marks the function as associated to the prefix of a LaTeX macro name.
	:type start_symbol: bool
	:return: the decorator.
	"""
	def decorator(func: Callable) -> Callable:
		# Store the function and its metadata
		# Remove "_expand__" prefix
		if not func.__name__.startswith('_expand__'):
			raise NameError('Function name must start with \'_expand__\'')
		func_name = str(func.__name__)[9:]
		if start_symbol:
			PREFIX_EXPAND_REGISTRY[func_name] = func
		else:
			FULL_EXPAND_REGISTRY[func_name] = func
		return func
	return decorator



class DependencyAnalyzer(Observer):
	"""
	Observer on TeX parsing for extracting the dependencies of the TeX file.
	"""

	__MACROS : dict[str,str] = {
		# TeX
		'input'						: '!{}',
		'include'					: '!{}',
		'usepackage'				: '![]!{}',
		'RequirePackage'			: '![]!{}',
		'documentclass'				: '![]!{}',
		# Index
		'makeindex'					: '',
		'printindex'				: '',
		# Glossaries
		'makeglossaries'			: '',
		'printglossaries'			: '',
		'newglossaryentry'			: '![]!{}',
		# BibTeX
		'addbibresource'			: '![]!{}',
		'begin'						: '[]!{}',
		'putbib'					: '![]',
		'bibliographyslide'			: '',
		'defaultbibliography'		: '!{}',
		'defaultbibliographystyle'	: '!{}',
	}

	def __init__(self, filename : str, root_directory : str):
		"""
		Constructor.
		:param filename: The name of the file to parse.
		:type filename: str
		:param root_directory: The name of the root directory.
		:type root_directory: str
		"""
		self.__full_expand_registry = FULL_EXPAND_REGISTRY
		self.__prefix_expand_registry = PREFIX_EXPAND_REGISTRY
		self.__is_multibib = False
		self.__is_bibunits = False
		self.__is_biblatex = False
		self.__is_biber = False
		self.__is_index = False
		self.__is_xindy = False
		self.__is_glossary = False
		self.__dependencies = {}
		self.__filename = filename
		self.__basename = os.path.basename(os.path.splitext(filename)[0])
		self.__root_directory = root_directory
		self.__explicit_bibliography = False
		self.__explicit_bibliography_style = False
		self.__default_bibliography = dict()
		self.__default_bibliography_style = dict()

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
	def is_bibunits(self) -> bool:
		"""
		Replies the Bibunits support is enable
		:return: True if the Bibunits support is enabled.
		:rtype: bool
		"""
		return self.__is_bibunits

	@is_bibunits.setter
	def is_bibunits(self, enable : bool):
		"""
		Set if the Bibunits support is enable
		:param enable: True if the Bibunits support is enabled.
		:type enable: bool
		"""
		self.__is_bibunits = enable

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
		This flag is considered only if is_makeindex is enabled.
		:return: True if the xindy support is enabled.
		:rtype: bool
		"""
		return self.__is_xindy

	@is_xindy_index.setter
	def is_xindy_index(self, enable : bool):
		"""
		Set if the support for xindy support is enable.
		This flag is considered only if is_makeindex is enabled.
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

	def __parse_bib_references(self, bib_db : str, *files : dict[str,Any]):
		"""
		Add a dependency to a BibTeX database.
		:param bib_db: the BibTeX database.
		:type bib_db: str
		:param files: the BibTeX files.
		:type files: dict[str,Any]
		:type files: str
		"""
		for param in files:
			value = param['text']
			if value:
				for svalue in re.split(r'\s*,\s*', value):
					if svalue:
						self.__explicit_bibliography = True
						if svalue.endswith('.bib'):
							bib_file = svalue
						else:
							bib_file = svalue + '.bib'
						if not os.path.isabs(bib_file):
							bib_file = os.path.normpath(os.path.join(self.root_directory, bib_file))
						if os.path.isfile(bib_file):
							self.__add_bib_dependency('bib', bib_file, bib_db)

	# noinspection PyCallingNonCallable
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
		:return: the result of expansion of the macro, or None to not replace the macro by something (the macro is used as-is)
		:rtype: str
		"""
		if name.startswith('\\'):
			callback_name = name[1:]
			if callback_name in self.__full_expand_registry:
				func = self.__full_expand_registry[callback_name]
				func(self, name, list(parameter))
			else:
				largest_size = 0
				largest_func = None
				for prefix, func in self.__prefix_expand_registry.items():
					if callback_name.startswith(prefix):
						l = len(prefix)
						if l > largest_size:
							largest_size = l
							largest_func = func
				if largest_func is not None:
					largest_func(self, name, list(parameter))
		return ''

	@expand_function(start_symbol=False)
	def _expand__input(self, name : str, parameters : list[dict[str, Any],...]):
		self._expand__include(name, parameters)

	@expand_function(start_symbol=False)
	def _expand__newglossaryentry(self, name : str, parameters : list[dict[str, Any],...]):
		self._expand__makeglossaries(name, parameters)

	@expand_function(start_symbol=False)
	def _expand__printglossaries(self, name : str, parameters : list[dict[str, Any],...]):
		self._expand__makeglossaries(name, parameters)

	@expand_function(start_symbol=False)
	def _expand__printindex(self, name : str, parameters : list[dict[str, Any],...]):
		self._expand__makeindex(name, parameters)

	# noinspection PyPep8Naming
	@expand_function(start_symbol=False)
	def _expand__RequirePackage(self, name : str, parameters : list[dict[str, Any],...]):
		self._expand__usepackage(name, parameters)

	# noinspection PyUnusedLocal
	@expand_function(start_symbol = False)
	def _expand__addbibresource(self, name : str, parameters : list[dict[str, Any],...]):
		bibdb = self.basename
		self.__parse_bib_references(bibdb, *parameters)

	@expand_function(start_symbol = True)
	def _expand__bibliography(self, name : str, parameters : list[dict[str, Any],...]):
		if self.is_multibib:
			bibdb = name[13:] if len(name) > 13 else self.basename
		else:
			bibdb = self.basename
		self.__parse_bib_references(bibdb, *parameters)

	# noinspection PyUnusedLocal
	@expand_function(start_symbol = False)
	def _expand__putbib(self, name : str, parameters : list[dict[str, Any],...]):
		bibdb = self.basename
		if len(parameters) > 0 and parameters[0] and 'text' in parameters[0] and parameters[0]['text']:
			self.__parse_bib_references(bibdb, *parameters)
		elif '\\defaultbibliography' not in self.__default_bibliography:
			self.__default_bibliography['\\defaultbibliography'] = [ {'text': self.basename} ]

	# noinspection PyUnusedLocal
	@expand_function(start_symbol = False)
	def _expand__bibliographyslide(self, name : str, parameters : list[dict[str, Any],...]):
		bibdb = self.basename
		self.__parse_bib_references(bibdb, {'text': 'biblio'})

	# noinspection PyUnusedLocal
	@expand_function(start_symbol = False)
	def _expand__begin(self, name : str, parameters : list[dict[str, Any],...]):
		tex_name = parameters[1]['text']
		if tex_name == 'bibliographysection':
			bibdb = self.basename
			self.__parse_bib_references(bibdb, {'text': 'biblio'})

	@expand_function(start_symbol = True)
	def _expand__bibliographystyle(self, name : str, parameters : list[dict[str, Any],...]):
		if self.is_multibib:
			bibdb = name[18:] if len(name) > 18 else self.basename
		else:
			bibdb = self.basename
		for param in parameters:
			value = param['text']
			if value:
				for svalue in re.split('\\s*,\\s*', value.strip()):
					if svalue:
						self.__explicit_bibliography_style = True
						if svalue.endswith('.bst'):
							bst_file = svalue
						else:
							bst_file = svalue + '.bst'
						if not os.path.isabs(bst_file):
							bst_file = os.path.normpath(os.path.join(self.root_directory, bst_file))
						if os.path.isfile(bst_file):
							self.__add_bib_dependency('bst', bst_file, bibdb)

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__documentclass(self, name : str, parameters : list[dict[str, Any],...]):
		cls = parameters[1]['text']
		if cls.endswith('.cls'):
			cls_file = cls
		else:
			cls_file = cls + '.cls'
		if not os.path.isabs(cls_file):
			cls_file = os.path.normpath(os.path.join(self.root_directory, cls_file))
		if os.path.isfile(cls_file):
			self.__add_dependency('cls', cls_file)

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__include(self, name : str, parameters : list[dict[str, Any],...]):
		for param in parameters:
			value = param['text']
			if value:
				if utils.is_tex_document(value):
					tex_file = value
				else:
					tex_file = value + utils.get_tex_file_extensions()[0]
				if not os.path.isabs(tex_file):
					tex_file = os.path.normpath(os.path.join(self.root_directory, tex_file))
				if os.path.isfile(tex_file):
					self.__add_dependency('tex', tex_file)

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__makeglossaries(self, name : str, parameters : list[dict[str, Any],...]):
		self.is_glossary = True

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__makeindex(self, name : str, parameters : list[dict[str, Any],...]):
		self.is_makeindex = True

	# noinspection DuplicatedCode,PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__usepackage(self, name : str, parameters : list[dict[str, Any],...]):
		sty = parameters[1]['text']
		if sty.endswith('.sty'):
			sty_file = sty
		else:
			sty_file = sty + ".sty"
		if sty_file == 'multibib.sty':
			self.is_multibib = True
		elif sty_file == 'bibunits.sty':
			self.is_bibunits = True
		elif sty_file == 'biblatex.sty':
			self.is_biblatex = True
			# Parse the biblatex parameters
			if parameters[0] and parameters[0]['text']:
				params = re.split(r'\s*,\s*', (parameters[0]['text'] or '').strip())
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
							bbx_file = os.path.normpath(os.path.join(self.root_directory, bbx_file))
						if os.path.isfile(bbx_file):
							self.__add_bib_dependency('bbx', bbx_file)
						if v.endswith('.cbx'):
							cbx_file = v
						else:
							cbx_file = v + ".cbx"
						if not os.path.isabs(cbx_file):
							cbx_file = os.path.normpath(os.path.join(self.root_directory, cbx_file))
						if os.path.isfile(cbx_file):
							self.__add_bib_dependency('cbx', cbx_file)
					elif k == 'bibstyle':
						if v.endswith('.bbx'):
							bbx_file = v
						else:
							bbx_file = v + ".bbx"
						if not os.path.isabs(bbx_file):
							bbx_file = os.path.normpath(os.path.join(self.root_directory, bbx_file))
						if os.path.isfile(bbx_file):
							self.__add_bib_dependency('bbx', bbx_file)
					elif k == 'citestyle':
						if v.endswith('.cbx'):
							cbx_file = v
						else:
							cbx_file = v + '.cbx'
						if not os.path.isabs(cbx_file):
							cbx_file = os.path.normpath(os.path.join(self.root_directory, cbx_file))
						if os.path.isfile(cbx_file):
							self.__add_bib_dependency('cbx', cbx_file)
		elif sty_file == 'indextools.sty':
			if parameters[0] and parameters[0]['text'] and 'xindy' in parameters[0]['text']:
				self.is_xindy_index = True
		elif sty_file == 'glossaries.sty':
			self.is_glossary = True
		else:
			if not os.path.isabs(sty_file):
				sty_file = os.path.normpath(os.path.join(self.root_directory, sty_file))
			if os.path.isfile(sty_file):
				self.__add_dependency('sty', sty_file)

	# noinspection DuplicatedCode,PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__defaultbibliography(self, name : str, parameters : list[dict[str, Any],...]):
		self.__default_bibliography[name] = parameters

	# noinspection DuplicatedCode,PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__defaultbibliographystyle(self, name : str, parameters : list[dict[str, Any],...]):
		self.__default_bibliography_style[name] = parameters


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
		:return: the definition of the macro, i.e., the macro prototype. See the class documentation for an explanation about the format of the macro prototype.
		:rtype: str
		"""
		if not special:
			if name.startswith('bibliographystyle'):
				return '!{}'
			elif name.startswith('bibliography'):
				return '!{}'
		return None

	# noinspection DuplicatedCode
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

		if not self.__explicit_bibliography and self.__default_bibliography:
			for name, parameters in self.__default_bibliography.items():
				self._expand__bibliography(name, parameters)

		if not self.__explicit_bibliography_style and self.__default_bibliography_style:
			for name, parameters in self.__default_bibliography_style.items():
				self._expand__bibliographystyle(name, parameters)


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
