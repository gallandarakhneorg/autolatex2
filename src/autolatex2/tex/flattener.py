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
Tools for creating a flattened version of a TeX document.
A flattened document contains a single TeX file, and all the
other related files are put inside the same directory of
the TeX file.
"""

import os
import shutil
import re
import textwrap
import logging
from typing import override, Any, Callable

from autolatex2.tex.texobservers import Observer
from autolatex2.tex.texparsers import Parser
from autolatex2.tex.texparsers import TeXParser
import autolatex2.utils.utilfunctions as genutils
from autolatex2.tex.utils import TeXMacroParameter
from autolatex2.utils.i18n import T
import autolatex2.tex.extra_macros as extramacros

FULL_EXPAND_REGISTRY : dict[str, Callable[[Any, Parser, str, list[TeXMacroParameter]], str]] = dict()

EXTRA_FULL_EXPAND_REGISTRY : dict[str, Callable[[Any, Parser, str, list[TeXMacroParameter]], str]] = dict()

PREFIX_EXPAND_REGISTRY : dict[str, Callable[[Any, Parser, str, list[TeXMacroParameter]], str]] = dict()

EXTRA_PREFIX_EXPAND_REGISTRY : dict[str, Callable[[Any, Parser, str, list[TeXMacroParameter]], str]] = dict()


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


class Flattener(Observer):
	"""
	Observer on TeX parsing for creating a flattened version of a TeX document.
	"""

	__MACROS : dict[str,str] = {
		# TeX
		'input'							: '!{}',
		'include'						: '!{}',
		'usepackage'					: '![]!{}',
		'RequirePackage'				: '![]!{}',
		'documentclass'					: '![]!{}',
		# Figures
		'includegraphics'				: '![]!{}',
		'graphicspath'					: '![]!{}',
		'pgfdeclareimage'				: '![]!{}!{}',
		# Biblatex
		'addbibresource'				: '![]!{}',
		'printbibliography'				: '![]',
		# bibunits
		'putbib'						: '![]',
		# S. Galland Templates
		'bibliographyslide'				: '',
		# BibTeX and other files
		'defaultbibliography'			: '!{}',
		'defaultbibliographystyle'		: '!{}',
		'begin'							: '![]!{}',
		'end'							: '![]!{}',
	}

	def __init__(self, filename : str, output_directory : str, include_extra_macros : bool):
		"""
		Constructor.
		:param filename: The name of the file to parse.
		:type filename: str
		:param output_directory: The name of the directory in which the document must be generated.
		:type output_directory: ste
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
		self.__file_content_counter : int = 0
		self.__embedded_files_added : set[str] = set()
		self.__embedded_files : dict[str,str] = dict()
		self.__include_paths : list[str] = list()
		self.__dynamic_preamble : list[str] = list()
		self.__tex_file_content : str = ''
		self.__source2target : dict[str,str] = dict()
		self.__target2source : dict[str,str] = dict()
		self.__files_to_copy : set[str] = set()
		# Other attributes
		self.__filename : str = filename
		self.__basename : str = os.path.basename(os.path.splitext(filename)[0])
		self.__dirname : str = os.path.dirname(filename)
		self.__output : str = output_directory
		self.__use_biblio :bool = False
		self.__included_sty : dict[str,str] = dict()
		self.__bibunits_aux_index : int = 0
		self.__in_bibunit : bool = False
		self.__explicit_bibliography : bool = False
		self.__explicit_bibliography_files : list[str] = list()
		self.__default_bibliography : list[str] = list()
		self.__explicit_bibliography_style : bool = False
		self.__default_bibliography_style : str | None = None
		self.__reset()

	def __reset(self) :
		# Inclusion paths for pictures.
		self.__include_paths = list()
		if self.__dirname:
			self.__include_paths.append(self.__dirname)
		# Preamble entries added by this tool
		self.__dynamic_preamble = list()
		# Content of the TeX file to generate
		self.__tex_file_content = ''
		# Mapping between the files of the source TeX and the target TeX.
		self.__source2target = dict()
		self.__target2source = dict()
		# Files to copy
		self.__files_to_copy = set()
		# Embedded files
		self.__embedded_files_added = set()
		self.__embedded_files = dict()
		self.__file_content_counter = 0

	@property
	def include_paths(self) -> list[str]:
		"""
		Replies the paths in which included files are search for.
		:return: The list of the inclusion path.
		:rtype: list[str]
		"""
		return self.__include_paths

	@property
	def use_biblio(self) -> bool:
		"""
		Replies if the biblio database is used and kept in the flat version.
		:return: True if the biblio database may be used. False for inline biliography entries.
		:rtype: bool
		"""
		return self.__use_biblio

	@use_biblio.setter
	def use_biblio(self, b : bool):
		"""
		Set if the biblio database is used and kept in the flat version.
		:param b: True if the biblio database may be used. False for inline biliography entries.
		:type b: bool
		"""
		self.__use_biblio = b

	@property
	def output_directory(self) -> str:
		"""
		Replies the output directory.
		:return: The name  of the output directory.
		:rtype: str
		"""
		return self.__output

	@output_directory.setter
	def output_directory(self, n : str):
		"""
		Set the output directory.
		:param n: The name of output directory.
		:type n: str
		"""
		self.__output = n

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
	def dirname(self) -> str:
		"""
		Replies the dirname of the parsed file.
		:return: The dirname  of the parsed file.
		:rtype: str
		"""
		return self.__dirname

	@dirname.setter
	def dirname(self, n : str):
		"""
		Set the dirname of the parsed file.
		:param n: The dirname of the parsed file.
		:type n: str
		"""
		self.__dirname = n

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

	@override
	def open_block(self, parser : Parser, text : str) -> str | None:
		"""
		Invoked when a block is opened.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: The text used for opening the block.
		:type text: str
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		"""
		return '{'

	@override
	def close_block(self, parser : Parser, text : str) -> str | None:
		"""
		Invoked when a block is closed.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: The text used for opening the block.
		:type text: str
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		"""
		return '}'

	@override
	def open_math(self, parser : Parser, inline : bool) -> str | None:
		"""
		Invoked when a math environment is opened.
		:param parser: reference to the parser.
		:type parser: Parser
		:param inline: Indicates if the math environment is inline or not.
		:type inline: bool
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		"""
		return '$' if inline else '\\['

	@override
	def close_math(self, parser : Parser, inline : bool) -> str | None:
		"""
		Invoked when a math environment is closed.
		:param parser: reference to the parser.
		:type parser: Parser
		:param inline: Indicates if the math environment is inline or not.
		:type inline: bool
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		"""
		return '$' if inline else '\\]'

	@override
	def text(self, parser : Parser, text : str):
		"""
		Invoked when characters were found and must be output.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: the text to filter.
		:type text: str
		"""
		if text:
			self.__tex_file_content += text

	# noinspection DuplicatedCode,PyCallingNonCallable
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
		if name.startswith('\\'):
			callback_name = re.sub(r'\*', 'star', name[1:])
			if callback_name in self.__full_expand_registry:
				func = self.__full_expand_registry[callback_name]
				return func(self, parser, name, list(parameters))
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
					return largest_func(self, parser, name, list(parameters))
		return raw_text

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__begin(self, parser : Parser, name : str, parameters : list[TeXMacroParameter]) -> str:
		assert len(parameters) > 1
		tex_name = parameters[1].text
		if tex_name == 'filecontents*':
			self.__file_content_counter = self.__file_content_counter + 1
		elif tex_name == 'bibunit' or (self.__include_extra_macros and tex_name == 'bibliographysection'):
			self.__in_bibunit = True
			self.__bibunits_aux_index = self.__bibunits_aux_index + 1
			if not self.use_biblio:
				return ''
		ret = name
		if parameters[0].text:
			ret += "[%s]" % parameters[0].text
		ret += "{%s}" % tex_name
		return ret

	@expand_function(start_symbol=False)
	def _expand__end(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		assert len(parameters) > 1
		tex_name = parameters[1].text
		if tex_name == 'filecontents*':
			self.__file_content_counter = self.__file_content_counter - 1
			if self.__file_content_counter <= 0:
				for key,  value in self.__embedded_files.items():
					parser.put_back(value)
				self.__embedded_files = dict()
		elif tex_name == 'bibunit':
			self.__in_bibunit = False
			if not self.use_biblio:
				return ''
		elif self.__include_extra_macros and tex_name == 'bibliographysection':
			self._expand__putbib(parser, name, [ TeXMacroParameter(text='biblio') ])
			self.__in_bibunit = False
			if not self.use_biblio:
				return '\\bibliographyslide'
		ret = name
		if parameters[0].text:
			ret += "[%s]" % parameters[0].text
		ret += "{%s}" % tex_name
		return ret

	# noinspection PyPep8Naming
	@expand_function(start_symbol=False)
	def _expand__RequirePackage(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		return self._expand__usepackage(parser, name, parameters)

	# noinspection DuplicatedCode
	@expand_function(start_symbol=False)
	def _expand__usepackage(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		assert len(parameters) > 1
		tex_name = parameters[1].text
		if tex_name == 'bibunits' and not self.use_biblio:
			return ''
		filename = self.__make_filename(tex_name, '.sty')
		added_file = ''
		if tex_name == 'biblatex':
			if not self.use_biblio:
				filename = self.__make_filename(self.basename, '.bbl', '.tex')
				if os.path.isfile(filename) and filename not in self.__embedded_files_added:
					logging.debug(T('Embedding %s'), filename)
					if not self.__embedded_files_added:
						self.__dynamic_preamble.append("\\usepackage{filecontents}")
					self.__embedded_files_added.add(filename)
					with open(filename) as f:
						content = f.read()
					basename = os.path.basename(filename)
					added_file = textwrap.dedent("""
							%%=======================================================
							%%== BEGIN FILE: %s
							%%=======================================================
							\\begin{filecontents*}{%s}
							%s
							\\end{filecontents*}
							%%=======================================================
							""") % (basename, basename, content)
				else:
					logging.error(T('File not found: %s'), filename)
		elif self.__is_document_file(filename) and filename not in self.__embedded_files_added:
			logging.debug(T('Embedding %s'), filename)
			if not self.__embedded_files_added:
				self.__dynamic_preamble.append("\\usepackage{filecontents}")
			self.__embedded_files_added.add(filename)
			with open(filename) as f:
				content = f.read()
			basename = os.path.basename(filename)
			added_file = textwrap.dedent("""
					%%=======================================================
					%%== BEGIN FILE: %s
					%%=======================================================
					\\begin{filecontents*}{%s}
					%s
					\\end{filecontents*}
					%%=======================================================
					""") % (basename, basename, content)
		ret = name
		if parameters[0].text:
			ret += "[%s]" % parameters[0].text
		ret += "{%s}" % tex_name
		if added_file:
			if 	self.__file_content_counter <= 0:
				parser.put_back(added_file + ret)
				return ''
			else:
				self.__embedded_files[filename] = added_file
				return ret
		else:
			return ret

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__documentclass(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		assert len(parameters) > 1
		tex_name = parameters[1].text
		filename = self.__make_filename(tex_name, '.cls')
		if self.__is_document_file(filename):
			tex_name = self.__create_mapping(filename, '.cls')
			self.__files_to_copy.add(filename)
		ret = name
		if parameters[0].text:
			ret += "[%s]" % parameters[0].text
		ret += "{%s}\n\n%%========= AUTOLATEX PREAMBLE\n\n" % tex_name
		return ret

	@expand_function(start_symbol=False, extra_macro=True)
	def _expand__includeanimatedfigure(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		return self._expand__includegraphics(parser, name, parameters)

	@expand_function(start_symbol=False, extra_macro=True)
	def _expand__includeanimatedfigurewtex(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		return self._expand__includegraphics(parser, name, parameters)

	@expand_function(start_symbol=False, extra_macro=True)
	def _expand__includefigurewtex(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		return self._expand__includegraphics(parser, name, parameters)

	@expand_function(start_symbol=False, extra_macro=True)
	def _expand__includegraphicswtex(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		return self._expand__includegraphics(parser, name, parameters)

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__includegraphics(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		assert len(parameters) > 1
		tex_name, prefix = self.__find_picture(parameters[1].text)
		ret = prefix + name
		if parameters[0].text:
			ret += "[%s]" % parameters[0].text
		ret += "{%s}" % tex_name
		return ret

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__graphicspath(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		assert len(parameters) > 1
		t = parameters[1].text
		if t:
			r = re.match(r'^\s*(?:\{([^}]+)}|([^,]+))\s*[,;]?\s*(.*)$', t)
			while r:
				graphic_path = r.group(1)
				if not graphic_path:
					graphic_path = r.group(2) or ''
				if not os.path.isabs(graphic_path):
					graphic_path = os.path.join(self.__dirname, graphic_path)
				t = r.group(3)
				self.__include_paths.insert(0, graphic_path)
				r = re.match(r'^\s*(?:\{([^}]+)}|([^,]+))\s*[,;]?\s*(.*)$', t) if t else None
		return "\\graphicspath{{./}}"

	@expand_function(start_symbol=False, extra_macro=True)
	def _expand__mfigurestar(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		return self._expand__mfigure(parser, name, parameters)

	@expand_function(start_symbol=False, extra_macro=True)
	def _expand__mfigurewtex(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		return self._expand__mfigure(parser, name, parameters)

	@expand_function(start_symbol=False, extra_macro=True)
	def _expand__mfigurewtexstar(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		return self._expand__mfigure(parser, name, parameters)

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False, extra_macro=True)
	def _expand__mfigure(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		assert len(parameters) > 4
		tex_name, prefix = self.__find_picture(parameters[2].text)
		ret = prefix + name
		if parameters[0].text:
			ret += "[%s]" % parameters[0].text
		ret += "{%s}{%s}{%s}{%s}" % (parameters[1].text, tex_name, parameters[3].text, parameters[4].text)
		return ret

	@expand_function(start_symbol=False, extra_macro=True)
	def _expand__msubfigurestar(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		return self._expand__msubfigure(parser, name, parameters)

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False, extra_macro=True)
	def _expand__msubfigure(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		assert len(parameters) > 3
		tex_name, prefix = self.__find_picture(parameters[2].text)
		ret = prefix + name
		if parameters[0].text:
			ret += "[%s]" % parameters[0].text
		ret += "{%s}{%s}{%s}" % (parameters[1].text, tex_name, parameters[3].text)
		return ret

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__pgfdeclareimage(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		assert len(parameters) > 2
		tex_name, prefix = self.__find_picture(parameters[2].text)
		ret = prefix + name
		if parameters[0].text:
			ret += "[%s]" % parameters[0].text
		ret += "{%s}{%s}" % (parameters[1].text, tex_name)
		return ret

	@expand_function(start_symbol=False)
	def _expand__include(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		return self._expand__input(parser, name, parameters)

	# noinspection PyUnusedLocal,DuplicatedCode
	@expand_function(start_symbol=False)
	def _expand__input(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		assert len(parameters) > 0
		filename = self.__make_filename(parameters[0].text, '.tex')
		with open(filename) as f:
			subcontent = f.read()
		subcontent += textwrap.dedent("""
						%%=======================================================
						%%== END FILE: %s
						%%=======================================================
						""") % (os.path.basename(filename))

		parser.put_back(subcontent)
		return textwrap.dedent("""
				%%=======================================================
				%%== BEGIN FILE: %s
				%%=======================================================
				""") % (os.path.basename(filename))

	# noinspection PyUnusedLocal,DuplicatedCode
	@expand_function(start_symbol=True)
	def _expand__bibliographystyle(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		assert len(parameters) > 0
		self.__explicit_bibliography_style = True
		if self.use_biblio:
			tex_name = parameters[0].text
			filename = self.__make_filename(tex_name, '.bst')
			if self.__is_document_file(filename):
				tex_name = self.__create_mapping(filename, '.bst')
				self.__files_to_copy.add(filename)
			return "%s{%s}" % (name, tex_name)
		return ''

	# noinspection PyUnusedLocal,DuplicatedCode
	@expand_function(start_symbol=False)
	def _expand__defaultbibliographystyle(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		assert len(parameters) > 0
		self.__default_bibliography_style = parameters[0].text
		if self.use_biblio:
			tex_name = parameters[0].text
			filename = self.__make_filename(tex_name, '.bst')
			if self.__is_document_file(filename):
				tex_name = self.__create_mapping(filename, '.bst')
				self.__files_to_copy.add(filename)
			return "%s{%s}" % (name, tex_name)
		return ''

	# noinspection PyUnusedLocal,DuplicatedCode
	@expand_function(start_symbol=True)
	def _expand__bibliography(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		assert len(parameters) > 0
		if parameters[0].text:
			files = re.split(r'\s*,\s*', parameters[0].text)
			self.__explicit_bibliography = True
			self.__explicit_bibliography_files = files
			if self.use_biblio:
				return self.__flatten_biblio_file(name, files)
			else:
				ret = self.__flatten_embedded_format()
				if ret:
					return ret
				return "%s{%s}" % (name, ','.join(files))
		return '%s{}' % name

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__addbibresource(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		assert len(parameters) > 1
		if parameters[1].text:
			self.__explicit_bibliography = True
			files = re.split(r'\s*,\s*', parameters[1].text)
			self.__explicit_bibliography_files = files
			if self.use_biblio:
				return self.__flatten_biblio_file(name, files)
		return ''

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__printbibliography(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		if self.__explicit_bibliography:
			if self.__explicit_bibliography_files:
				if self.use_biblio:
					return name
				else:
					return self.__flatten_embedded_format()
		else:
			if self.__default_bibliography:
				if self.use_biblio:
					return self.__flatten_biblio_file(name, self.__default_bibliography, add_parameter=0)
				else:
					return self.__flatten_embedded_format()
		logging.error(T('No bibliography source provided'))
		return ''

	# noinspection DuplicatedCode,PyUnusedLocal
	@expand_function(start_symbol=False)
	def _expand__putbib(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		assert len(parameters) > 0
		if parameters[0].text:
			files = re.split(r'\s*,\s*', parameters[0].text)
		elif self.__explicit_bibliography:
			files = self.__explicit_bibliography_files
		else:
			files = self.__default_bibliography
		if files:
			if self.use_biblio:
				return self.__flatten_biblio_file(name, files, add_parameter=2)
		elif self.use_biblio:
			return self.__flatten_biblio_file(name, [self.basename], add_parameter=2)
		return self.__flatten_embedded_format()

	# noinspection PyUnusedLocal
	@expand_function(start_symbol=False, extra_macro=True)
	def _expand__bibliographyslide(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		self._expand__putbib(parser, name, [ TeXMacroParameter(text='biblio') ])
		return name

	# noinspection PyUnusedLocal,DuplicatedCode
	@expand_function(start_symbol=False)
	def _expand__defaultbibliography(self, parser: Parser, name: str, parameters: list[TeXMacroParameter]) -> str:
		assert len(parameters) > 0
		if parameters[0].text:
			lst = list()
			for param in re.split(r'\s*,\s*', parameters[0].text):
				bib_name = self.__make_filename(param, '.bib')
				if self.__is_document_file(bib_name):
					lst.append(bib_name)
			self.__default_bibliography = lst if lst else list()
		return ''


	# noinspection DuplicatedCode
	def __flatten_biblio_file(self, macro_name : str, files : list[str], add_parameter : int = 1) -> str:
		"""
		Do the bibliography output by considering that the biblio is stored in a local bib file.
		:param macro_name: The name of the TeX macro that should be used for including the bibliography.
		:type macro_name: str
		:param files: A list of bibliography file to use for rendering the bibliography.
		:type files: list[str]
		:param add_parameter: Indicates if the files are added as parameter of the macro. 0 means no parameter.
		1 means one regular parameter. 2 means optional parameter. Default is 1.
		:type add_parameter: int
		:return: the text to be put back in the flattened version of the document.
		:rtype: str
		"""
		assert self.use_biblio
		new_tex_names = list()
		for file in files:
			filename = self.__make_filename(file, '.bib')
			if self.__is_document_file(filename):
				tex_name = self.__create_mapping(filename, '.bib')
				self.__files_to_copy.add(filename)
				new_tex_names.append(tex_name)
			else:
				logging.warning(T('File not found in document folder: %s'), filename)
				new_tex_names.append(file)
		if add_parameter == 1:
			return "%s{%s}" % (macro_name, ','.join(new_tex_names))
		elif add_parameter == 2:
			return "%s[%s]" % (macro_name, ','.join(new_tex_names))
		else:
			return macro_name


	def __flatten_embedded_format(self) -> str:
		"""
		Do the bibliography output by output the BBL content in the TeX file.
		:return: the text to be put back in the flattened version of the document.
		:rtype: str
		"""
		assert not self.use_biblio
		if self.__in_bibunit:
			bbl_name = self.basename + '.' + str(self.__bibunits_aux_index)
		else:
			bbl_name = self.basename
		bbl_file = self.__make_filename(bbl_name, '.bbl')
		if os.path.isfile(bbl_file):
			with open(bbl_file) as f:
				content = f.read()
			return textwrap.dedent("""
					%%=======================================================
					%%== BEGIN FILE: %s
					%%=======================================================
					%s
					%%=======================================================
					""") % (os.path.basename(bbl_file), content)
		else:
			logging.error(T('File not found: %s'), bbl_file)
			return ''

	def __make_filename(self, basename : str, *ext : str) -> str:
		"""
		Create a valid filename for the flattening process.
		:param basename: The basename.
		:param basename: str
		:param ext: The filename extension (default: None).
		:param ext: list(str)
		"""
		name = basename
		for one_ext in ext:
			if one_ext and not basename.endswith(ext):
				name = basename + one_ext
				continue
		if not os.path.isabs(name):
			return os.path.join(self.dirname, name)
		return name

	def __is_document_file(self, filename : str) -> bool:
		"""
		Replies if the given file is a part of the document.
		:param filename: The filename to test.
		:type filename: str
		:return: True if the file is a part of the document; otherwise False.
		:rtype: bool
		"""
		if not os.path.isabs(filename):
			filename = os.path.join(self.dirname, filename)
		if os.path.isfile(filename):
			return filename.startswith(self.dirname)
		return False

	# noinspection DuplicatedCode
	def __create_mapping(self, filename : str, ext : str) -> str:
		"""
                Compute a unique filename, and map it to the source file.
                :param filename: The filename to translate.
                :type filename: str
                :param ext: The filename extension to remove.
                :type ext: str
                :return: The unique basename.
                :rtype: str
                """
		name = os.path.basename(filename)
		if ext and name.endswith(ext):
			name = name[0:(-len(ext))]
		bn = name
		i = 0
		while (name + ext) in self.__target2source:
			name = "%s_%d" % (bn, i)
			i += 1
		self.__target2source[name + ext] = filename
		self.__source2target[filename] = name + ext
		return name

	# noinspection DuplicatedCode
	def __find_picture(self, tex_name : str) -> tuple[str,str]:
		"""
		Find a picture.
		:param tex_name: The name of the picture in the TeX document.
		:type tex_name: str
		:return: the tuple (target filename, the prefix to add before the macro)
		:rtype: tuple[str,str]
		"""
		# Search in the registered/found bitmaps
		if self.__source2target:
			for src in self.__source2target:
				if src == tex_name:
					return os.path.basename(self.__source2target[tex_name]), ''

		prefix = ''
		filename = self.__make_filename(tex_name)
		if not os.path.isfile(filename):
			texexts = ('.pdftex_t', '.pstex_t', '.pdf_tex', '.ps_tex', '.tex')
			figexts = (	'.pdf', '.eps', '.ps', '.png', '.jpeg', '.jpg', '.gif', '.bmp')
			exts = figexts + texexts
			ofilename = filename
			obasename = genutils.simple_basename(tex_name, *exts)
			filenames = {}

			# Search in the registered paths
			template = obasename
			for path in self.include_paths:
				for ext in figexts:
					fullname = os.path.join(path, template + ext)
					fullname = self.__make_filename(fullname)
					if os.path.isfile(fullname):
						filenames[fullname] = False
				for ext in texexts:
					fullname = os.path.join(path, template + ext)
					fullname = self.__make_filename(fullname, '')
					if os.path.isfile(fullname):
						filenames[fullname] = True

			# Search in the folder, i.e. the document directory.
			if not filenames:
				template = os.path.join(os.path.dirname(ofilename), genutils.simple_basename(ofilename, *exts))
				for ext in figexts:
					fn = template + ext
					if os.path.isfile(fn):
						filenames[fn] = False
				for ext in texexts:
					fn = template + ext
					if os.path.isfile(fn):
						filenames[fn] = True

			if not filenames:
				logging.error(T('Picture not found: %s'), tex_name)
			else:
				selected_name1 = None
				selected_name2 = None
				for filename in filenames:
					bn, ext = os.path.splitext(filename)
					tex_name = self.__create_mapping(filename, ext) + ext
					if filenames[filename]:
						if not selected_name1:
							selected_name1 = (tex_name, filename)
					else:
						self.__files_to_copy.add(filename)
						selected_name2 = tex_name
				if selected_name1:
					tex_name, filename = selected_name1
					logging.debug(T('Embedding %s'), filename)
					with open(filename) as f:
						filecontent = f.read()
					# Replacing the filename in the newly embedded TeX file
					if self.__source2target:
						for source in self.__source2target:
							filecontent = filecontent.replace('{' + source + '}',
											'{' + self.__source2target[source] + '}')
					bsn = os.path.basename(tex_name)
					prefix +=	textwrap.dedent("""
								%%=======================================================
								%%== BEGIN FILE: %s
								%%=======================================================
								\\begin{filecontents*}{%s}
								%s
								\\end{filecontents*}
								%%=======================================================
								""") % (bsn, bsn, filecontent)
					self.__dynamic_preamble.append('\\usepackage{filecontents}')
				elif selected_name2:
					tex_name = selected_name2
		else:
			ext = os.path.splitext(tex_name)[1] or ''
			tex_name = self.__create_mapping(filename, ext) + ext
			self.__files_to_copy.add(filename)

		return tex_name, prefix

	# noinspection DuplicatedCode
	def _analyze_document(self) -> str:
		"""
		Analyze the tex document for extracting information.
		:return: The content of the file.
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

		# Replace PREAMBLE content
		if self.__tex_file_content:
			preamble = '\n'.join(self.__dynamic_preamble)
			if not preamble:
				preamble = ''
			content = self.__tex_file_content.replace('%========= AUTOLATEX PREAMBLE', preamble, 1)

		# Clean the content by removing empty lines
		content = content.replace('\t', ' ').strip()
		content = re.sub("\n+[ \t]*", "\n", content, re.S)

		return content

	def _generate_flat_document(self,  content : str) -> bool:
		"""
		Generate the flat document.
		:param content: The content of the file.
		:type content: str
		:return: The success status of the generation.
		:rtype: bool
		"""
		# Create the output directory
		os.makedirs(self.output_directory)

		# Create the main TeX file
		output_file = os.path.join(self.output_directory, self.basename) + '.tex'

		logging.debug(T('Writing %s') % output_file)
		with open(output_file, 'w') as f:
			f.write(content)

		# Copy the resources
		for source in self.__files_to_copy:
			target = self.__source2target[source]
			target = os.path.join(self.output_directory, target)
			logging.debug(T('Copying resource %s to %s') % (source, target))
			target_directory = os.path.dirname(target)
			if not os.path.isdir(target_directory):
				os.makedirs(target_directory)
			shutil.copy(source, target)
		return True

	def run(self) -> bool:
		"""
		Make the input file standalone.
		:return: True if the execution is a success, otherwise False.
		"""
		self.__reset()
		content = self._analyze_document()
		logging.debug(T("File content: %s") % content)
		return self._generate_flat_document(content)

	@override
	def comment(self, parser: Parser, raw: str, comment: str) -> str | None:
		return None


