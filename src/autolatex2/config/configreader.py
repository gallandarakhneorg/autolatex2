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
Reader of the program configuration.
"""

import logging
import configparser
import os
import re
from typing import Any

import autolatex2.utils.utilfunctions as genutils
from autolatex2.config.configobj import Config
from autolatex2.config.translator import TranslatorLevel
from autolatex2.utils.extlogging import ensure_autolatex_logging_levels
from autolatex2.utils.i18n import T


class OldStyleConfigReader:
	"""
	Reader of the program configuration that is written with the old-style format (ini file).
	"""
	
	def __init__(self):
		self._base_dir : str = os.getcwd()
		ensure_autolatex_logging_levels()

	def _read_viewer(self, content : Any, config : Config):
		"""
		Read the configuration section [viewer].
		:param content: the configuration file content.
		:type content: dict
		:param config: the configuration object to fill up.
		:type config: Config
		"""
		config.view.view = OldStyleConfigReader.to_bool(self._ensure_ascendent_compatibility(content.get('view')), config.view.view)
		config.view.viewer_cli = self._ensure_ascendent_compatibility(content.get('viewer')) or config.view.viewer_cli

	def _read_scm(self, content : Any, config : Config):
		"""
		Read the configuration section [scm].
		:param content: the configuration file content.
		:type content: dict
		:param config: the configuration object to fill up.
		:type config: Config
		"""
		config.scm.commit_cli = self._ensure_ascendent_compatibility(content.get('scm commit')) or config.scm.commit_cli
		config.scm.update_cli = self._ensure_ascendent_compatibility(content.get('scm update')) or config.scm.commit_cli

	def _read_clean(self, content : Any, config : Config):
		"""
		Read the configuration section [clean].
		:param content: the configuration file content.
		:type content: dict
		:param config: the configuration object to fill up.
		:type config: Config
		"""
		for p in OldStyleConfigReader.to_path_list(self._ensure_ascendent_compatibility(content.get('files to clean'))):
			config.clean.add_clean_file(p)
		for p in OldStyleConfigReader.to_path_list(self._ensure_ascendent_compatibility(content.get('files to desintegrate'))):
			config.clean.add_cleanall_file(p)

	def _read_generation_prefix(self, content : Any, config : Config):
		"""
		Read the path definition in the configuration section [generation].
		:param content: the configuration file content.
		:type content: dict
		:param config: the configuration object to fill up.
		:type config: Config
		"""
		main_name = self._ensure_ascendent_compatibility(content.get('main file'))
		if main_name:
			main_name = genutils.abs_path(main_name, self._base_dir)
			config.document_directory = os.path.dirname(main_name)
			config.document_filename = os.path.basename(main_name)

	def _read_generation(self, content : Any, config : Config):
		"""
		Read the configuration section [generation], except the ones "_read_generation_prefix".
		:param content: the configuration file content.
		:type content: dict
		:param config: the configuration object to fill up.
		:type config: Config
		"""
		config.include_extra_macros = OldStyleConfigReader.to_bool(self._ensure_ascendent_compatibility(content.get('include extra macros')), config.generation.include_extra_macros)

		for p in OldStyleConfigReader.to_path_list(self._ensure_ascendent_compatibility(content.get('image directory'))):
			config.translators.add_image_path(self.to_path(p))

		config.translators.is_translator_enable = OldStyleConfigReader.to_bool(self._ensure_ascendent_compatibility(content.get('generate images')), config.translators.is_translator_enable)
		
		config.include_extra_macros = OldStyleConfigReader.to_bool(self._ensure_ascendent_compatibility(content.get('include extra macros')), config.generation.include_extra_macros)
		generation_type = OldStyleConfigReader.to_kw(self._ensure_ascendent_compatibility(content.get('generation type')), 'pdf' if config.generation.pdf_mode else 'ps')
		if generation_type == 'dvi' or generation_type == 'ps':
			config.generation.pdf_mode = False
		else:
			config.generation.pdf_mode = True

		tex_compiler = OldStyleConfigReader.to_kw(self._ensure_ascendent_compatibility(content.get('tex compiler')), config.generation.latex_compiler)
		if tex_compiler != 'latex' and tex_compiler != 'xelatex' and tex_compiler != 'lualatex':
			tex_compiler = 'pdflatex'
		config.generation.latex_compiler = tex_compiler

		config.generation.synctex = OldStyleConfigReader.to_bool(self._ensure_ascendent_compatibility(content.get('synctex')), config.generation.synctex)

		for p in OldStyleConfigReader.to_path_list(self._ensure_ascendent_compatibility(content.get('translator include path'))):
			config.translators.add_include_path(self.to_path(p))
	
		cmd = self._ensure_ascendent_compatibility(content.get('latex_cmd'))
		if cmd:
			config.generation.latex_cli = cmd

		cmd = self._ensure_ascendent_compatibility(content.get('bibtex_cmd'))
		if cmd:
			config.generation.bibtex_cli = cmd
	
		cmd = self._ensure_ascendent_compatibility(content.get('biber_cmd'))
		if cmd:
			config.generation.biber_cli = cmd
	
		cmd = self._ensure_ascendent_compatibility(content.get('makeglossaries_cmd'))
		if cmd:
			config.generation.makeglossary_cli = cmd

		cmd = self._ensure_ascendent_compatibility(content.get('makeindex_cmd'))
		if cmd:
			config.generation.makeindex_cli = cmd

		cmd = self._ensure_ascendent_compatibility(content.get('dvi2ps_cmd'))
		if cmd:
			config.generation.dvips_cli = cmd

		flags = self._ensure_ascendent_compatibility(content.get('latex_flags'))
		if flags:
			config.generation.latex_flags = flags

		flags = self._ensure_ascendent_compatibility(content.get('bibtex_flags'))
		if flags:
			config.generation.bibtex_flags = flags

		flags = self._ensure_ascendent_compatibility(content.get('biber_flags'))
		if flags:
			config.generation.biber_flags = flags

		flags = self._ensure_ascendent_compatibility(content.get('makeglossaries_flags'))
		if flags:
			config.generation.makeglossary_flags = flags

		flags = self._ensure_ascendent_compatibility(content.get('makeindex_flags'))
		if flags:
			config.generation.makeindex_flags = flags

		flags = self._ensure_ascendent_compatibility(content.get('dvi2ps_flags'))
		if flags:
			config.generation.dvips_flags = flags

		make_index_style = self.to_list(self._ensure_ascendent_compatibility(content.get('makeindex style')))
		config.generation.makeindex_style_filename = None
		if not make_index_style:
			make_index_style = ['@detect@system']
		for key in make_index_style:
			kw = OldStyleConfigReader.to_kw(key, '@detect@system')
			result = None
			if kw == '@detect':
				result = self.to_path(self.__detect_ist_file(config))
			elif kw == '@system':
				result = self.to_path(config.get_system_ist_file())
			elif kw == '@none':
				config.generation.makeindex_style_filename = None
				break
			elif kw == '@detect@system':
				ist_file = self.__detect_ist_file(config)
				if ist_file:
					result = self.to_path(ist_file)
				else:
					result = self.to_path(config.get_system_ist_file())
			if result:
				config.generation.makeindex_style_filename = result
				break

	def _read_translator(self, translator_name : str, translator_level : TranslatorLevel, content : Any, config : Config):
		"""
		Read the configuration section [<translator>].
		:param translator_name: The name of the translator.
		:type translator_name: str
		:param translator_level: The level for the translator.
		:type translator_level: int
		:param content: the configuration file content.
		:type content: dict
		:param config: the configuration object to fill up.
		:type config: Config
		"""
		raw_value = self._ensure_ascendent_compatibility(content.get('include module'))
		default_value = config.translators.included(translator_name, translator_level)
		new_value = OldStyleConfigReader.to_bool(raw_value, default_value)
		config.translators.set_included(translator_name, translator_level, new_value)
		raw_files = self._ensure_ascendent_compatibility(content.get('files to convert'))
		path_list = OldStyleConfigReader.to_path_list(raw_files)
		for path_element in path_list:
			formatted_path = self.to_path(path_element)
			config.translators.add_image_to_convert(formatted_path)

	# noinspection PyMethodMayBeStatic
	def _is_translator_section(self, section_name : str) -> bool:
		"""
		Replies if the given section name is for a translator or not.
		:param section_name: Name of the section to test.
		:type section_name: str
		:return: True if the given section name is for a translator.
		:rtype: bool
		"""
		if re.match(r'^[a-zA-Z+-]+2[a-zA-Z0-9+-]+(?:_[a-zA-Z0-9_+-]+)?$', section_name, re.S):
			return True
		return False

	def read(self, filename : str, translator_level : TranslatorLevel, config : Config = None) -> Config:
		"""
		Read the configuration file.
		:param filename: the name of the file to read.
		:type filename: str
		:param translator_level: the level at which the configuration is located. See TranslatorLevel enumeration.
		:type translator_level: TranslatorLevel
		:param config: the configuration object to fill up. Default is None.
		:type config: Config
		:return: the configuration object
		:rtype: Config
		"""
		if config is None:
			config = Config()

		filename = os.path.abspath(filename)
		self._base_dir = os.path.dirname(filename)

		try:
			config_file = configparser.ConfigParser()
			config_file.read(filename)
			
			for section in config_file.sections():
				nsection = section.lower()
				if nsection == 'generation':
					content = dict(config_file.items(section))
					self._read_generation_prefix(content, config)

			for section in config_file.sections():
				nsection = section.lower()
				content = dict(config_file.items(section))
				if nsection == 'generation':
					self._read_generation(content, config)
				elif nsection == 'viewer':
					self._read_viewer(content, config)
				elif nsection == 'clean':
					self._read_clean(content, config)
				elif nsection == 'scm':
					self._read_scm(content, config)
				elif self._is_translator_section(nsection):
					self._read_translator(section, translator_level, content, config)
				else:
					logging.debug(T("Ignore section '%s' in the configuration file: %s") % (section, filename))
		finally:
			self._base_dir = os.getcwd()
		return config

	# noinspection PyMethodMayBeStatic
	def __detect_ist_file(self, config : Config) -> str | None:
		"""
		Detect an IST file into the current document.
		:param config: the configuration.
		:type config: Config
		:return: the IST filename or None
		:rtype: str
		"""
		ddir = config.document_directory
		if not ddir:
			ddir = os.getcwd()
		if os.path.isdir(ddir):
			only_files = [f for f in os.listdir(ddir) if os.path.isfile(os.path.join(ddir, f))]
			ist_files = list()
			for file in only_files:
				if re.match(r'.ist$', file, re.I):
					ist_files.append(file)
			if len(ist_files) > 0:
				filename = ist_files[0]
				if len(ist_files) > 1:
					logging.warning(T('Multiple IST files were found into the document directory. Use: %s') % filename)
				return filename
		return None

	# noinspection PyMethodMayBeStatic
	def _ensure_ascendent_compatibility(self, value : str | None) -> str:
		if value:
			m = re.match(r'^(.*?)\s*#.*$', value)
			if m:
				return m.group(1)
		return value or ''

	def to_path(self, value : str | None) -> str:
		if value:
			return genutils.abs_path(value, self._base_dir)
		return value or ''

	@staticmethod
	def to_bool(value : str, default : bool | None) -> bool:
		"""
		Convert a string to a bool. This function takes care of strings as "True", "False", "Yes", "No", "t", "f", "y", "n", "1", "0".
		:param value: the value to convert.
		:type value: str
		:param default: the default value.
		:type: bool
		:return: the boolean value.
		:rtype: bool
		"""
		if value:
			v = value.lower()
			return v == 'true' or v == 'yes' or v == 't' or v =='y' or v =='1'
		return default or False

	@staticmethod
	def to_path_list(value : str) -> list:
		"""
		Convert a string to list of paths. According to the operating system, the path separator may be ':' or ';'
		:param value: the value to convert.
		:type value: str
		:return: the list value.
		:rtype: list
		"""
		if value:
			sep = os.pathsep
			paths = value.split(sep)
			return paths
		return list()

	@staticmethod
	def to_list(value : str) -> list[str] | None:
		"""
		Convert a string to list of strings. The considered separators are: ',' and ';'
		:param value: the value to convert.
		:type value: str
		:return: the list value.
		:rtype: list
		"""
		if value:
			return re.split(r'\s*[,;]\s*', value)
		return None

	@staticmethod
	def to_kw(value : str, default : str | None) -> str:
		"""
		Convert a string to string-based keyword.
		:param value: the value to convert.
		:type value: str | None
		:param default: the default value.
		:type: str
		:return: the keyword.
		:rtype: str
		"""
		if value:
			return value.lower()
		return default or ''

	# noinspection PyBroadException,DuplicatedCode
	def read_system_config_safely(self, config : Config = None) -> Config:
		"""
		Read the configuration file at the system level without failing if the file does not exist.
		:param config: the configuration object to fill up. Default is None.
		:type config: Config
		:return: the configuration object
		:rtype: Config
		"""
		if config is None:
			config = Config()
		filename = config.system_config_file
		if filename and os.path.isfile(filename) and os.access(filename, os.R_OK):
			try:
				self.read(filename, TranslatorLevel.SYSTEM, config)
			except:
				pass
		return config

	# noinspection PyBroadException,DuplicatedCode
	def read_user_config_safely(self, config : Config = None) -> Config:
		"""
		Read the configuration file at the user level without failing if the file does not exist.
		:param config: the configuration object to fill up. Default is None.
		:type config: Config
		:return: the configuration object
		:rtype: Config
		"""
		if config is None:
			config = Config()
		filename = config.user_config_file
		if filename and os.path.isfile(filename) and os.access(filename, os.R_OK):
			try:
				self.read(filename, TranslatorLevel.USER, config)
			except:
				pass
		return config

	# noinspection PyBroadException
	def read_document_config_safely(self, filename : str, config : Config = None) -> Config:
		"""
		Read the configuration file at the document level without failing if the file does not exist.
		:param filename: the name of the file to read.
		:type filename: str
		:param config: the configuration object to fill up. Default is None.
		:type config: Config
		:return: the configuration object
		:rtype: Config
		"""
		if config is None:
			config = Config()
		if filename and os.path.isfile(filename) and os.access(filename, os.R_OK):
			try:
				self.read(filename, TranslatorLevel.DOCUMENT, config)
			except:
				pass
		return config
		
