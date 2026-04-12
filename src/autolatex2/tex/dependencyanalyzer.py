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
import json
from typing import override, Any, Callable, Sized

from autolatex2.tex.texobservers import Observer
from autolatex2.tex.texparsers import Parser
from autolatex2.tex.texparsers import TeXParser
from autolatex2.tex.utils import FileType, TeXMacroParameter
import autolatex2.utils.utilfunctions as genutils
import autolatex2.tex.extra_macros as extramacros

FULL_EXPAND_REGISTRY : dict[str, Callable[[Any, str, list[TeXMacroParameter]], None]] = dict()

EXTRA_FULL_EXPAND_REGISTRY : dict[str, Callable[[Any, str, list[TeXMacroParameter]], None]] = dict()

PREFIX_EXPAND_REGISTRY : dict[str, Callable[[Any, str, list[TeXMacroParameter]], None]] = dict()

EXTRA_PREFIX_EXPAND_REGISTRY : dict[str, Callable[[Any, str, list[TeXMacroParameter]], None]] = dict()

# noinspection DuplicatedCode
def expand_function(start_symbol : bool, extra_macro : bool = False):
	"""
	Decorator to register functions with __expand__ prefix.
	:param start_symbol: Marks the function as associated to the prefix of a LaTeX macro name.
	:type start_symbol: bool
	:param extra_macro: Marks the function as part of th supporting features for the extra macros. Default is False.
	:type extra_macro: bool
	:return: the decorator.
	"""
	def decorator(func: Callable) -> Callable:
		# Store the function and its metadata
		# Remove "_expand__" prefix
		if not func.__name__.startswith('_expand__'):
			raise NameError('Function name must start with \'_expand__\'')
		func_name = str(func.__name__)[9:]
		if start_symbol:
			if extra_macro:
				EXTRA_PREFIX_EXPAND_REGISTRY[func_name] = func
			else:
				PREFIX_EXPAND_REGISTRY[func_name] = func
		else:
			if extra_macro:
				EXTRA_FULL_EXPAND_REGISTRY[func_name] = func
			else:
				FULL_EXPAND_REGISTRY[func_name] = func
		return func
	return decorator


class DependencyDescription:
	"""
	Description of a dependency with all the interesting information.
	:param filename: The filename.
	:type filename: str
	:param file_type: The type of the dependency.
	:type file_type: FileType
	:param scope: The name of the scope that may be associated to the filename dependency.
	:type scope: str|None
	:param output_file: The name of the file that may be considered as an output. The type of file depends on file_type.
	For example, for a bib file, the output file may be a specific bbl file.
	:type output_file: str|None
	"""
	def __init__(self, filename : str, file_type : FileType, scope : str|None, output_file : str|None):
		self.__filename : str = filename
		self.__type : FileType = file_type
		self.__has_change : bool = False
		self.__change : float | None = None
		self.__scopes : set[str] = set()
		self.__output_files : list[str] = list()
		self.add_scope(scope)
		self.add_output_file(output_file)

	def __str__(self):
		return '->' + self.file_name

	def __repr__(self):
		json_content = {
			'file_name': self.file_name,
			'file_type': self.file_type,
			'scopes': self.scopes,
			'change': self.change,
			'output_files': self.output_files
		}
		return json.dumps(json_content,  indent = 4)

	@property
	def file_name(self) -> str:
		"""
		Replies the filename.
		:rtype: str
		"""
		return self.__filename

	@property
	def file_type(self) -> FileType:
		"""
		Replies the type of file.
		:rtype: FileType
		"""
		return self.__type

	@property
	def scopes(self) -> set[str]:
		"""
		Replies the scopes in which this file was defined as a dependency.
		:rtype: set[str]
		"""
		return self.__scopes

	def add_scope(self, scope : str|None):
		"""
		Add the given scope.
		:param scope: The name of the scope.
		:type scope: str|None
		"""
		if scope:
			self.__scopes.add(scope)

	def add_output_file(self, output_file : str|None):
		"""
		Add the given output file.
		:param output_file: The name of the output file if relevant.
		:type output_file: str|None
		"""
		if output_file:
			self.__output_files.append(output_file)

	@property
	def change(self) -> float | None:
		"""
		Replies the time of the last change for the file.
		:rtype: float
		"""
		if not self.__has_change:
			self.__has_change = True
			self.__change = genutils.get_file_last_change(self.file_name)
		return self.__change

	@property
	def output_files(self) -> list[str]:
		"""
		Replies the linked output file. For example, for a Bibtex file, it may be a specific BBL file.
		:rtype: list[str]
		"""
		return self.__output_files



class _TypeDependencyRepositoryDescriptionIterator:
	def __init__(self, parent_iterator):
		self.__parent_iterator = parent_iterator

	def __next__(self) -> DependencyDescription:
		name, description = self.__parent_iterator.__next__()
		return description




class TypeDependencyRepository(Sized):
	"""
	Repository of dependency descriptions of a specific type.
	"""
	def __init__(self, database : dict[str,DependencyDescription] = None):
		if database is None:
			self.__database : dict[str,DependencyDescription] = dict()
		else:
			self.__database: dict[str, DependencyDescription] = database
		self.__buffer_scopes : set[str] | None = None
		self.__buffer_new_database : dict[str,dict[str, DependencyDescription]] | None = None

	def __str__(self):
		return str(self.__database.keys())

	def __repr__(self):
		json_content = list()
		for dep in self:
			json_content.append(repr(dep))
		return json.dumps(json_content,  indent = 4)

	def __len__(self) -> int:
		return len(self.__database)

	def __contains__(self, item : str) -> bool:
		return item in self.__database

	def __iter__(self):
		return _TypeDependencyRepositoryDescriptionIterator(self.__database.items().__iter__())

	def __reset_buffers(self):
		self.__buffer_scopes = None
		self.__buffer_new_database = None

	def update(self, file_type : FileType, filename : str, scope : str|None = None, output_file : str|None = None) -> DependencyDescription:
		"""
		Add a dependency for the given file.
		:param file_type: The type of the dependency.
		:type file_type: FileType
		:param filename: The filename.
		:type filename: str
		:param scope: The name of the scope that may be associated to the filename dependency.
		:type scope: str|None
		:param output_file: The name of the file that may be considered as an output. The type of file depends on file_type.
		For example, for a bib file, the output file may be a specific bbl file.
		:type output_file: str|None
		:return: The dependency description.
		:rtype: DependencyDescription
		"""
		self.__reset_buffers()
		if filename not in self.__database:
			desc = DependencyDescription(filename, file_type, scope=scope, output_file=output_file)
			self.__database[filename] = desc
		else:
			desc = self.__database[filename]
			desc.add_scope(scope)
			desc.add_output_file(output_file)
		return desc

	def scope_to(self, scope : str) -> 'TypeDependencyRepository':
		"""
		Create a scopy of this repository with only the dependencies of the given scope.
		:param scope: The name of the scope.
		:return: the scoped repository.
		"""
		if self.__buffer_new_database is None:
			self.__buffer_new_database = dict()
		assert self.__buffer_new_database is not None, "self.__buffer_new_database is None"
		if scope not in self.__buffer_new_database:
			self.__buffer_new_database[scope] = dict()
			for name, dep in self.__database.items():
				if scope in dep.scopes:
					self.__buffer_new_database[scope][name] = dep
		return TypeDependencyRepository(database=self.__buffer_new_database[scope])

	def get_scopes(self) -> set[str]:
		"""
		Replies the scopes that are defined in the repository.
		:return: the scopes.
		:rtype: set[str]
		"""
		if self.__buffer_scopes is None:
			self.__buffer_scopes = set()
			assert self.__buffer_scopes is not None, "self.__buffer_scopes is None"
			for name, dep in self.__database.items():
				if dep.scopes:
					self.__buffer_scopes.update(dep.scopes)
		return self.__buffer_scopes



class _DependencyRepository(Sized):
	"""
	Repository of dependency descriptions.
	"""
	def __init__(self):
		self.__database : dict[FileType,TypeDependencyRepository] = dict()
		self.__buffer_bibliography_databases : set[str] | None = None

	def __str__(self):
		return str(self.__database.keys())

	def __repr__(self):
		return json.dumps(self.__database,  indent = 4)

	def __len__(self) -> int:
		return len(self.__database)

	def __reset_buffers(self):
		self.__buffer_bibliography_databases = None

	def update(self, file_type : FileType, filename : str, scope : str|None = None, output_file : str|None = None) -> DependencyDescription:
		"""
		Add a dependency for the given file, associated to the given type.
		:param file_type: The type of the dependency.
		:type file_type: FileType
		:param filename: The filename.
		:type filename: str
		:param scope: The name of the scope that may be associated to the filename dependency.
		:type scope: str|None
		:param output_file: The name of the file that may be considered as an output. The type of file depends on file_type.
		For example, for a bib file, the output file may be a specific bbl file.
		:type output_file: str|None
		:return: The dependency description.
		:rtype: DependencyDescription
		"""
		self.__reset_buffers()
		if file_type not in self.__database:
			self.__database[file_type] = TypeDependencyRepository()
		return self.__database[file_type].update(file_type, filename, scope=scope, output_file=output_file)

	@property
	def types(self) -> set[FileType]:
		"""
		Replies the types of files that have been stored in this repository.
		:return: the set of file types.
		:rtype: set[FileType]
		"""
		return set(self.__database.keys())

	def get_bibliography_scopes(self) -> set[str]:
		"""
		Replies the names of the bibliography scopes that have been detected.
		The scopes of the bibliographies are usually defined by the LaTeX multibib package.
		:return: the names of the bibliography database.
		:rtype: set[str]
		"""
		if self.__buffer_bibliography_databases is None:
			self.__buffer_bibliography_databases = set()
			assert self.__buffer_bibliography_databases is not None, "self.__buffer_bibliography_databases is None"
			for btype in FileType.bibliography_types():
				if btype in self.__database:
					content = self.__database[btype]
					if content:
						self.__buffer_bibliography_databases.update(content.get_scopes())
		return self.__buffer_bibliography_databases

	def get_dependencies_for_type(self, dependency_type : FileType, scope : str|None = None) -> TypeDependencyRepository:
		"""
		Replies the dependencies of the given type.
		:param dependency_type: The type of the dependency (tex, bib, ...)
		:type dependency_type: FileType
		:param scope: The scope of the dependency to restrict to.
		:type scope: str|None
		:return: the set of dependencies. The replied dictionary maps the dependency filenames to their detailed descriptions
		:rtype: TypeDependencyRepository
		"""
		if dependency_type not in self.__database:
			self.__database[dependency_type] = TypeDependencyRepository()
		if scope:
			return self.__database[dependency_type].scope_to(scope)
		return self.__database[dependency_type]



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
		'begin'						: '![]!{}![]',
		'end'						: '!{}',
		'putbib'					: '![]',
		'defaultbibliography'		: '!{}',
		'defaultbibliographystyle'	: '!{}',
	}

	def __init__(self, filename : str, root_directory : str, main_filename : str, include_extra_macros : bool):
		"""
		Constructor.
		:param filename: The name of the file to parse.
		:type filename: str
		:param root_directory: The name of the root directory.
		:type root_directory: str
		:param main_filename: The name of the main TeX file that is used as the TeX entry point. This filename
		 may differ from those provided as the filename argument for this function.
		:type main_filename: str
		:param include_extra_macros: Indicates if the extra macros must be included in the dependency analysis.
		:type include_extra_macros: bool
		"""
		self.__include_extra_macros = include_extra_macros
		if self.__include_extra_macros:
			self.__full_expand_registry = FULL_EXPAND_REGISTRY | EXTRA_FULL_EXPAND_REGISTRY
			self.__prefix_expand_registry = PREFIX_EXPAND_REGISTRY | EXTRA_FULL_EXPAND_REGISTRY
		else:
			self.__full_expand_registry = FULL_EXPAND_REGISTRY
			self.__prefix_expand_registry = PREFIX_EXPAND_REGISTRY
		self.__is_multibib : bool = False
		self.__bibunit_index : int = 0
		self.__in_bibunit : bool = False
		self.__is_bibunits : bool = False
		self.__is_biblatex : bool = False
		self.__is_biber : bool = False
		self.__is_index : bool = False
		self.__is_xindy : bool = False
		self.__is_glossary : bool = False
		self.__dependency_repository : _DependencyRepository = _DependencyRepository()
		self.__filename : str = filename
		self.__basename : str = os.path.basename(os.path.splitext(filename)[0])
		self.__root_directory : str = root_directory
		self.__main_filename : str = main_filename
		self.__explicit_bibliography : bool = False
		self.__explicit_bibliography_style : bool = False
		self.__default_bibliography : dict[str,list[TeXMacroParameter]] = dict()
		self.__default_bibliography_style : dict[str,list[TeXMacroParameter]] = dict()

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
	def main_filename(self) -> str:
		"""
		Replies the filename of the main TeX document that serves as the entry point for the TeX tools.
		:return: The name of the main TeX document file.
		:rtype: str
		"""
		return self.__main_filename

	@main_filename.setter
	def main_filename(self, f : str):
		"""
		Set the filename of the main TeX document that serves as the entry point for the TeX tools.
		:param f: The name of the main TeX document file.
		:type f: str
		"""
		self.__main_filename = f

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

	def get_dependency_types(self) -> set[FileType]:
		"""
		Replies the dependency types.
		:return: the set of dependency types.
		:rtype: set[FileType]
		"""
		return self.__dependency_repository.types

	def get_dependencies_for_type(self, dependency_type : FileType, scope : str|None = None) -> TypeDependencyRepository:
		"""
		Replies the dependencies of the given type.
		:param dependency_type: The type of the dependency (tex, bib, ...)
		:type dependency_type: FileType
		:param scope: The scope of the dependency to restrict to.
		:type scope: str|None
		:return: the set of dependencies. The set of dependency names is the more used form. The dictionary of dictionary is usually used for bibliography dependencies.
		:rtype: TypeDependencyRepository
		"""
		return self.__dependency_repository.get_dependencies_for_type(dependency_type, scope)

	def get_bibliography_scopes(self) -> set[str]:
		"""
		Replies the names of the bibliography scopes that have been detected.
		:return: the names of the bibliography database.
		:rtype: set[str]
		"""
		return self.__dependency_repository.get_bibliography_scopes()

	def __extract_bibdb(self, macro_name_prefix : str, name : str) -> str:
		l = len(macro_name_prefix)
		if self.is_multibib:
			return name[l:] if len(name) > l else self.basename
		else:
			return self.basename

	def __parse_bib_references(self, bib_db : str, bbl_file : str, *files : TeXMacroParameter):
		"""
		Add a dependency to a bibliography database.
		:param bib_db: the name of the database.
		:type bib_db: str
		:param bbl_file: the name of the BBL file.
		:type bbl_file: str
		:param files: the bibliography files.
		:type files: TeXMacroParameter
		:type files: str
		"""
		# Special case: the bibunit
		if self.__in_bibunit:
			bbl_file = genutils.basename_with_path(bbl_file, *FileType.bibliography_extensions()) + str(self.__bibunit_index)
			bbl_file = FileType.bbl.add_extension(bbl_file)
		if not os.path.isabs(bbl_file):
			bbl_file = FileType.bbl.ensure_extension(bbl_file)
			bbl_file = os.path.normpath(os.path.join(self.root_directory, bbl_file))
		for param in files:
			value = param.text
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
							self.__dependency_repository.update(FileType.bib, bib_file, scope=bib_db, output_file=bbl_file)

	# noinspection PyCallingNonCallable
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
		:type parameters: TeXMacroParameter
		:return: the result of expansion of the macro, or None to not replace the macro by something (the macro is used as-is)
		:rtype: str
		"""
		if name.startswith('\\'):
			callback_name = name[1:]
			if callback_name in self.__full_expand_registry:
				func = self.__full_expand_registry[callback_name]
				func(self, name, list(parameters))
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
					largest_func(self, name, list(parameters))
		return ''

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__documentclass(self, name : str, parameters : list[TeXMacroParameter]):
		assert len(parameters) > 1, "Invalid parameters for \\documentclass: %s" % str(parameters)
		cls = parameters[1].text
		if cls.endswith('.cls'):
			cls_file = cls
		else:
			cls_file = cls + '.cls'
		if not os.path.isabs(cls_file):
			cls_file = os.path.normpath(os.path.join(self.root_directory, cls_file))
		if os.path.isfile(cls_file):
			self.__dependency_repository.update(FileType.cls, cls_file)

	@expand_function(start_symbol=False)
	def _expand__input(self, name : str, parameters : list[TeXMacroParameter]):
		self._expand__include(name, parameters)

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__include(self, name : str, parameters : list[TeXMacroParameter]):
		for param in parameters:
			value = param.text
			if value:
				if FileType.is_tex_document(value):
					tex_file = value
				else:
					tex_file = value + FileType.tex_extensions()[0]
				if not os.path.isabs(tex_file):
					tex_file = os.path.normpath(os.path.join(self.root_directory, tex_file))
				if os.path.isfile(tex_file):
					self.__dependency_repository.update(FileType.tex, tex_file)

	@expand_function(start_symbol=False)
	def _expand__newglossaryentry(self, name : str, parameters : list[TeXMacroParameter]):
		self._expand__makeglossaries(name, parameters)

	@expand_function(start_symbol=False)
	def _expand__printglossaries(self, name : str, parameters : list[TeXMacroParameter]):
		self._expand__makeglossaries(name, parameters)

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__makeglossaries(self, name : str, parameters : list[TeXMacroParameter]):
		self.is_glossary = True

	@expand_function(start_symbol=False)
	def _expand__printindex(self, name : str, parameters : list[TeXMacroParameter]):
		self._expand__makeindex(name, parameters)

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__makeindex(self, name : str, parameters : list[TeXMacroParameter]):
		self.is_makeindex = True

	# noinspection PyPep8Naming
	@expand_function(start_symbol=False)
	def _expand__RequirePackage(self, name : str, parameters : list[TeXMacroParameter]):
		self._expand__usepackage(name, parameters)

	@expand_function(start_symbol = True)
	def _expand__bibliography(self, name : str, parameters : list[TeXMacroParameter]):
		assert len(parameters) > 0, "Invalid parameters for \\bibliography: %s" % str(parameters)
		bibdb = self.__extract_bibdb('\\bibliography', name)
		self.__parse_bib_references(bibdb, bibdb, *parameters)

	@expand_function(start_symbol = True)
	def _expand__bibliographystyle(self, name : str, parameters : list[TeXMacroParameter]):
		assert len(parameters) > 0, "Invalid parameters for \\bibliographystyle: %s" % str(parameters)
		bibdb = self.__extract_bibdb('\\bibliographystyle', name)
		self.__analyse_bst_specification(bibdb, parameters)

	# noinspection PyUnusedLocal
	@expand_function(start_symbol = False)
	def _expand__addbibresource(self, name : str, parameters : list[TeXMacroParameter]):
		assert len(parameters) > 0, "Invalid parameters for \\addbibresource: %s" % str(parameters)
		bibdb = self.basename
		self.__parse_bib_references(bibdb, *parameters)

	# noinspection PyUnusedLocal
	@expand_function(start_symbol = False)
	def _expand__putbib(self, name : str, parameters : list[TeXMacroParameter]):
		bibdb = self.basename
		# By default, Bibunits uses the 'bu' prefix for its auxiliary files
		bbl_file = 'bu'
		if len(parameters) > 0 and parameters[0].text:
			self.__parse_bib_references(bibdb, bbl_file, *parameters)
		elif '\\defaultbibliography' in self.__default_bibliography:
			self.__parse_bib_references(bibdb, bbl_file,*self.__default_bibliography['\\defaultbibliography'])
		else:
			self.__parse_bib_references(bibdb, bbl_file, TeXMacroParameter(text=self.basename))

	# noinspection PyUnusedLocal
	@expand_function(start_symbol = False, extra_macro=True)
	def _expand__bibliographyslide(self, name : str, parameters : list[TeXMacroParameter]):
		# The name of the auxiliary file that contains the bibliography entry is based on: \jobname.\index.aux
		self.__parse_bib_references(self.basename, self.__build_bibunit_auxiliary_basename_prefix(), TeXMacroParameter(text='biblio'))

	# noinspection PyUnusedLocal
	@expand_function(start_symbol = False)
	def _expand__begin(self, name : str, parameters : list[TeXMacroParameter]):
		assert len(parameters) > 1, "Invalid parameters for \\begin: %s" % str(parameters)
		tex_name = parameters[1].text
		if tex_name == 'bibunit':
			self.__is_bibunits = True
			self.__in_bibunit = True
			self.__bibunit_index = self.__bibunit_index + 1
			assert len(parameters) > 2, "Invalid parameters for \\begin{bibunits}: %s" % str(parameters)
			if parameters[2].text:
				self.__analyse_bst_specification(self.basename, [ parameters[2] ])
		elif self.__include_extra_macros and tex_name == 'bibliographysection':
			self.__is_bibunits = True
			self.__in_bibunit = True
			self.__bibunit_index = self.__bibunit_index + 1
			self.__parse_bib_references(self.basename, self.__build_bibunit_auxiliary_basename_prefix(), TeXMacroParameter(text='biblio'))

	# noinspection PyUnusedLocal
	@expand_function(start_symbol = False)
	def _expand__end(self, name : str, parameters : list[TeXMacroParameter]):
		assert len(parameters) > 0, "Invalid parameters for \\end: %s" % str(parameters)
		tex_name = parameters[0].text
		if tex_name == 'bibunit' or (self.__include_extra_macros and tex_name == 'bibliographysection'):
			self.__is_bibunits = True
			self.__in_bibunit = False

	# noinspection DuplicatedCode,PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__usepackage(self, name : str, parameters : list[TeXMacroParameter]):
		assert len(parameters) > 1, "Invalid parameters for \\usepackage: %s" % str(parameters)
		sty = parameters[1].text
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
			if parameters[0].text:
				params = re.split(r'\s*,\s*', (parameters[0].text or '').strip())
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
							self.__dependency_repository.update(FileType.bbx, bbx_file)
						if v.endswith('.cbx'):
							cbx_file = v
						else:
							cbx_file = v + ".cbx"
						if not os.path.isabs(cbx_file):
							cbx_file = os.path.normpath(os.path.join(self.root_directory, cbx_file))
						if os.path.isfile(cbx_file):
							self.__dependency_repository.update(FileType.cbx, cbx_file)
					elif k == 'bibstyle':
						if v.endswith('.bbx'):
							bbx_file = v
						else:
							bbx_file = v + ".bbx"
						if not os.path.isabs(bbx_file):
							bbx_file = os.path.normpath(os.path.join(self.root_directory, bbx_file))
						if os.path.isfile(bbx_file):
							self.__dependency_repository.update(FileType.bbx, bbx_file)
					elif k == 'citestyle':
						if v.endswith('.cbx'):
							cbx_file = v
						else:
							cbx_file = v + '.cbx'
						if not os.path.isabs(cbx_file):
							cbx_file = os.path.normpath(os.path.join(self.root_directory, cbx_file))
						if os.path.isfile(cbx_file):
							self.__dependency_repository.update(FileType.cbx, cbx_file)
		elif sty_file == 'indextools.sty':
			if parameters[0] and parameters[0].text and 'xindy' in parameters[0].text:
				self.is_xindy_index = True
		elif sty_file == 'glossaries.sty':
			self.is_glossary = True
		else:
			if not os.path.isabs(sty_file):
				sty_file = os.path.normpath(os.path.join(self.root_directory, sty_file))
			if os.path.isfile(sty_file):
				self.__dependency_repository.update(FileType.sty, sty_file)

	# noinspection DuplicatedCode,PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__defaultbibliography(self, name : str, parameters : list[TeXMacroParameter]):
		self.__default_bibliography[name] = parameters

	# noinspection DuplicatedCode,PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__defaultbibliographystyle(self, name : str, parameters : list[TeXMacroParameter]):
		self.__default_bibliography_style[name] = parameters

	def __analyse_bst_specification(self, bib_db : str, parameters: list[TeXMacroParameter]):
		for param in parameters:
			value = param.text
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
							self.__dependency_repository.update(FileType.bst, bst_file, scope=bib_db)

	def __build_bibunit_auxiliary_basename_prefix(self) -> str:
		"""
		Compute the prefix text that will serve as the starting value for the filename of Bibunits auxiliary files
		according to the API and extra macros provided by S. Galland.
		:return: The prefix.
		:rtype: str
		"""
		if self.__include_extra_macros:
			return genutils.simple_basename(self.main_filename, *FileType.tex_extensions()) + '.'
		return 'bu'

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

		if self.__include_extra_macros:
			for k, v in extramacros.ALL_EXTRA_MACROS.items():
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
