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
Translation engine.
"""

import re
import os
from typing import Any

from autolatex2.config .configobj import Config
from autolatex2.config .translator import TranslatorLevel
from autolatex2.translator.readers.abstractreader import AbstractTransdefReader
from autolatex2.translator.readers.perlreader import PerlTransdefReader
from autolatex2.translator.readers.transdefline import TransdefLine
from autolatex2.translator.readers.yamlreader import YamlTransdefReader
from autolatex2.utils.i18n import T


class Translator:
	"""
	Description of a translator.
	"""

	def __init__(self, name : str, configuration : Config):
		"""
		Parse a complete translator name to extract the components.
		:param name: The name must have the syntax:<ul>
				<li><code>source2target</code></li>
				<li><code>source2target+target2</code></li>
				<li><code>source2target_variant</code></li>
				<li><code>source2target+target2_variant</code></li>
				</li>
		:type: str
		:param configuration: The current AutoLaTeX configuration.
		:type configuration: Config
		"""
		self.configuration = configuration
		self.__name = None
		self.__basename = None
		self.__source = None
		self.__full_source = None
		self.__target = None
		self.__variant = None
		self.__filename = None
		self.__level = None
		self.__file_content = None
		self.__temporary_file_patterns = None
		self.__target_file_patterns = None
		self.decode(name)

	@classmethod
	def _label(cls, full_source : str, target : str, variant : str = None) -> str:
		"""
		Replies a human-readable string that corresponds to the specified translator data.
		:param full_source: The filename extension for the source file.
		:type full_source: str
		:param target: The filename extension for the target file.
		:type target: str
		:param variant: The name of the transformation variant version. Default is None.
		:type variant: str
		:return: the string representation that is readable by a human
		:rtype: str
		"""
		if variant:
			return T("Translate %s to %s with %s alternative") % (full_source, target, variant)
		else:
			return T("Translate %s to %s") % (full_source, target)

	def __str__(self):
		return Translator._label(self.full_source, self.target, self.variant)

	def __repr__(self):
		return str(self)

	def decode(self, name: str):
		"""
		Decode the given translator name and change the properties
		of this object accordingly.
		:param name: The name must have the syntax:<ul>
				<li><code>source2target</code></li>
				<li><code>source2target+target2</code></li>
				<li><code>source2target_variant</code></li>
				<li><code>source2target+target2_variant</code></li>
				</li>
		:type: str
		"""
		m = re.match(r'^([a-zA-Z+-]+)2([a-zA-Z0-9-]+)(?:\+([a-zA-Z0-9+-]+))?(?:_(.*))?$', name)
		if m:
			source = m.group(1)
			target = m.group(2)
			target2 = m.group(3) or ''
			variant = m.group(4) or ''
			osource = source
			basename = "%s2%s%s" % (source, target, target2)
			if target2:
				if target2 == 'tex':
					source = "ltx.%s" % source
				elif target2 == 'layers':
					source = "layers.%s" % source
				elif target2 == 'layers+tex' or target2 == 'tex+layers':
					source = "layers.ltx.%s" % source
				else:
					target += "+%s" % target2
			self.__name = name
			self.__full_source = source
			self.__source = osource
			self.__target = target
			self.__variant = variant
			self.__basename = basename
		else:
			raise RuntimeError(T("Invalid translator name: %s") % name)


	@property
	def name(self) -> str:
		"""
		Name of the translator.
		:rtype: str
		"""
		return self.__name

	@property
	def source(self) -> str:
		"""
		Source type given to the constructor.
		:rtype: str
		"""
		return self.__source

	@property
	def full_source(self) -> str:
		"""
		Source type.
		:rtype: str
		"""
		return self.__full_source

	@property
	def target(self) -> str:
		"""
		Target type.
		:rtype: str
		"""
		return self.__target

	@property
	def variant(self) -> str:
		"""
		Variant version of the translator.
		:rtype: str
		"""
		return self.__variant

	@property
	def basename(self) -> str:
		"""
		Basename of the translator.
		:rtype: str
		"""
		return self.__basename

	@property
	def filename(self) -> str:
		"""
		Replies the filename of the translator.
		:return: The filename or None.
		:rtype: str
		"""
		return self.__filename

	@filename.setter
	def filename(self, name : str):
		"""
		Set the filename of the translator.
		:param name: The filename of the translator.
		:type name: str
		"""
		self.__filename = name

	@property
	def level(self) -> TranslatorLevel:
		"""
		Replies the execution level at which this translator was defined.
		:return: The execution level of the translator.
		:rtype: TranslatorLevel
		"""
		return self.__level 

	@level.setter
	def level(self, l : TranslatorLevel):
		"""
		Set the execution level at which this translator was defined.
		:param l: The execution level of the translator.
		:type l: TranslatorLevel
		"""
		self.__level  = l

	def __read_translator_file(self, filename : str) -> dict[str,TransdefLine]:
		"""
		Replies the content of a translator definition file.
		:param filename: The filename to read.
		:type filename: str
		:return: The dictionary of the content.
		:rtype: dict[str,str]
		"""
		exts = os.path.splitext(filename)
		ext = exts[-1]
		reader = self._create_transdef_reader(ext)
		content = reader.read_translator_file(filename)
		return content

	def _create_transdef_reader(self,  extension : str) -> AbstractTransdefReader:
		"""
		Create the instance of the transdef reader based on the filename extension.
		"""
		if extension == '.transdef':
			return PerlTransdefReader(self.configuration)
		else:
			return YamlTransdefReader(self.configuration)

	def get_input_extensions(self) -> list[str]:
		"""
		Replies the list of the filename extensions that are the sources for this translator.
		:rtype: list[str]
		"""
		if self.__file_content is None:
			self.__file_content = self.__read_translator_file(self.filename)
		if 'INPUT_EXTENSIONS' in self.__file_content and self.__file_content['INPUT_EXTENSIONS'] and self.__file_content['INPUT_EXTENSIONS'].value_list:
			return list(self.__file_content['INPUT_EXTENSIONS'].value_list)
		return list()

	def get_output_extensions(self) -> list[str]:
		"""
		Replies the list of the filename extensions that are the targets for this translator.
		:rtype: list[str]
		"""
		if self.__file_content is None:
			self.__file_content = self.__read_translator_file(self.filename)
		if 'OUTPUT_EXTENSIONS' in self.__file_content and self.__file_content['OUTPUT_EXTENSIONS'] and self.__file_content['OUTPUT_EXTENSIONS'].value:
			return list(self.__file_content['OUTPUT_EXTENSIONS'].value_list)
		return list()

	def get_command_line(self) -> list[str] | None:
		"""
		Replies the command line to run if specified in the translator definition file.
		:rtype: list[str] | None
		"""
		if self.__file_content is None:
			self.__file_content = self.__read_translator_file(self.filename)
		if 'COMMAND_LINE' in self.__file_content and self.__file_content['COMMAND_LINE'] and self.__file_content['COMMAND_LINE'].value_list:
			return self.__file_content['COMMAND_LINE'].value_list
		return None

	def get_embedded_function(self) -> str | None:
		"""
		Replies the embedded function to run if specified in the translator definition file.
		:rtype: str | None
		"""
		if self.__file_content is None:
			self.__file_content = self.__read_translator_file(self.filename)
		if 'TRANSLATOR_FUNCTION' in self.__file_content and self.__file_content['TRANSLATOR_FUNCTION'] and self.__file_content['TRANSLATOR_FUNCTION'].value:
			return self.__file_content['TRANSLATOR_FUNCTION'].value
		return None

	def get_embedded_function_interpreter(self) -> str | None:
		"""
		Replies the interpreter for the embedded function to run if specified in the translator definition file.
		:rtype: str | None
		"""
		if self.__file_content is None:
			self.__file_content = self.__read_translator_file(self.filename)
		if 'TRANSLATOR_FUNCTION' in self.__file_content and self.__file_content['TRANSLATOR_FUNCTION'] and self.__file_content['TRANSLATOR_FUNCTION'].interpreter:
			return self.__file_content['TRANSLATOR_FUNCTION'].interpreter
		return None

	def get_python_dependencies(self) -> list[str] | None:
		"""
		Replies the python dependencies that must be included in the executed script.
		:rtype: list[str] | None
		"""
		if self.__file_content is None:
			self.__file_content = self.__read_translator_file(self.filename)
		if 'TRANSLATOR_PYTHON_DEPENDENCIES' in self.__file_content and self.__file_content['TRANSLATOR_PYTHON_DEPENDENCIES'] and self.__file_content['TRANSLATOR_PYTHON_DEPENDENCIES'].value_list:
			return self.__file_content['TRANSLATOR_PYTHON_DEPENDENCIES'].value_list
		return None

	def get_constants(self, list_separator : str = ' ') -> dict[str,Any]:
		"""
		Replies the constants that must be defined for the translator.
		The replied dictionary is a copy of the internal data structure.
		:param list_separator: The separator of elements used for merging a list in order to obtain a string.
		:type list_separator: str
		:return: the dictionary of the variable names and the values. You could change the content of this dictionary safely. It will not change the internal data structure.
		:rtype: dict[str,Any]
		"""
		if self.__file_content is None:
			self.__file_content = self.__read_translator_file(self.filename)
		variables = dict()
		for k, v in self.__file_content.items():
			if k not in [ 'INPUT_EXTENSIONS', 'OUTPUT_EXTENSIONS', 'FILES_TO_CLEAN', 'TRANSLATOR_PERL_DEPENDENCIES', 
					'TRANSLATOR_PYTHON_DEPENDENCIES',  'COMMAND_LINE',  'TRANSLATOR_FUNCTION']:
				if v.value_list:
					variables[k] = ''
					for elt in v.value_list:
						if variables[k]:
								variables[k] += list_separator 
						variables[k] += str(elt)
				else:
					variables[k] = str(v.value)
		return variables

	def get_temporary_file_patterns(self) -> list[str]:
		"""
		Replies the list of the filename patterns that are used for temporary files.
		:rtype: list[str]
		"""
		if self.__temporary_file_patterns is None:
			if self.__file_content is None:
				self.__file_content = self.__read_translator_file(self.filename)
			if 'TEMPORARY_FILES' in self.__file_content and self.__file_content['TEMPORARY_FILES'] and self.__file_content['TEMPORARY_FILES'].value_list:
				self.__temporary_file_patterns = list(self.__file_content['TEMPORARY_FILES'].value_list)
			else:
				self.__temporary_file_patterns = list()
		return self.__temporary_file_patterns


	def get_target_file_patterns(self) -> list[str]:
		"""
		Replies the list of the filename patterns that are representing the target files.
		:rtype: list[str]
		"""
		if self.__target_file_patterns is None:
			if self.__file_content is None:
				self.__file_content = self.__read_translator_file(self.filename)
			if 'ALL_OUTPUT_FILES' in self.__file_content and self.__file_content['ALL_OUTPUT_FILES'] and self.__file_content['ALL_OUTPUT_FILES'].value_list:
				self.__target_file_patterns = list(self.__file_content['ALL_OUTPUT_FILES'].value_list)
			else:
				self.__target_file_patterns = list()
			if '$out' not in self.__target_file_patterns:
				self.__target_file_patterns.append('$out')
		return self.__target_file_patterns

