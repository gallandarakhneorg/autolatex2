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
Writer of AutoLaTeX Configuration.
"""

import configparser
import os
from typing import Any

from autolatex2.config.configobj import Config


class OldStyleConfigWriter:
	"""
	Writer of AutoLaTeX Configuration that is written with the old-style format (ini file).
	"""

	# noinspection PyMethodMayBeStatic
	def to_bool(self,  value : bool) -> str | None:
		"""
		Convert the given boolean value to a string representation for the configuration file.
		:param value: the value to convert.
		:type value: bool
		:return: the string representation for the boolean value.
		:rtype: str
		"""
		if value is None:
			return None
		return 'true' if value else 'false'

	# noinspection PyMethodMayBeStatic
	def to_cli(self,  value : Any) -> str | None:
		"""
		Convert the given value to a string representation for the command-line operation.
		:param value: the value to convert. It could be a list or a value.
		:type value: Any
		:return: the string representation for the value.
		:rtype: str
		"""
		if value:
			if isinstance(value,  list):
				return ' '.join(value)
			else:
				return str(value)
		return None

	# noinspection PyMethodMayBeStatic
	def to_path(self,  value : Any,  cdir : str) -> str | None:
		"""
		Convert the given value to a path that is relative to the folder cdir.
		:param value: the path to convert.
		:type value: object
		:param cdir: the root path to be considered.
		:type value: str
		:return: the relative path.
		:rtype: str
		"""
		if value:
			return os.path.relpath(str(value),  cdir)
		return None

	# noinspection PyMethodMayBeStatic
	def to_paths(self,  value : Any,  cdir : str) -> str | None:
		"""
		Convert the given value to a list of path that are relative to the folder cdir.
		:param value: the paths to convert.
		:type value: Any
		:param cdir: the root path to be considered.
		:type cdir: str
		:return: the relative paths.
		:rtype: str
		"""
		if value:
			if isinstance(value,  list):
				return os.pathsep.join({os.path.relpath(str(f),  cdir) for f in value})
			else:
				return os.path.relpath(str(value),  cdir)
		return None

	# noinspection PyMethodMayBeStatic
	def set(self,  config_out : configparser.ConfigParser,  section : str,  key : str,  value : Any):
		"""
		Put the given value in the configuration inside the given section and for the given key.
		:param config_out: configuration to be filled up.
		:type config_out: ConfigParser
		:param section: name of the section of the configuration to set.
		:type section: str
		:param key: the name of the key that is supposed to be set.
		:type key: str
		:param value: the value to save in the configuration.
		:type value: Any
		"""
		if value:
			config_out.set(section,  key,  value)

	def write(self, filename : str,  config : Config):
		"""
		Write the configuration file.
		:param filename: the name of the file to read.
		:type filename: str
		:param config: the configuration object to fill up.
		:type config: Config
		"""
		dout = os.path.dirname(filename)
		
		config_out = configparser.ConfigParser()

		config_out.add_section('generation')

		self.set(config_out, 'generation', 'main file', self.to_path(os.path.normpath(os.path.join(config.document_directory, config.document_filename)), dout))

		self.set(config_out, 'generation', 'image directory', self.to_paths(config.translators.image_paths, dout))
		
		self.set(config_out, 'generation', 'generate images', self.to_bool(config.translators.is_translator_enable))
		
		self.set(config_out, 'generation', 'generation type', 'pdf' if config.generation.pdf_mode else 'ps')

		self.set(config_out, 'generation', 'include extra macros', self.to_bool(config.generation.include_extra_macros))

		self.set(config_out, 'generation', 'tex compiler', config.generation.latex_compiler)

		self.set(config_out, 'generation', 'synctex', self.to_bool(config.generation.synctex))

		self.set(config_out, 'generation', 'translator include path', self.to_paths(config.translators.include_paths, dout))

		self.set(config_out, 'generation', 'latex_cmd', self.to_cli(config.generation.latex_cli))
		self.set(config_out, 'generation', 'latex_flags', self.to_cli(config.generation.latex_flags))

		self.set(config_out, 'generation', 'bibtex_cmd', self.to_cli(config.generation.bibtex_cli))
		self.set(config_out, 'generation', 'bibtex_flags', self.to_cli(config.generation.bibtex_flags))

		self.set(config_out, 'generation', 'biber_cmd', self.to_cli(config.generation.biber_cli))
		self.set(config_out, 'generation', 'biber_flags', self.to_cli(config.generation.biber_flags))
	
		self.set(config_out, 'generation', 'makeglossaries_cmd', self.to_cli(config.generation.makeglossary_cli))
		self.set(config_out, 'generation', 'makeglossaries_flags', self.to_cli(config.generation.makeglossary_flags))
	
		self.set(config_out, 'generation', 'makeindex_cmd', self.to_cli(config.generation.makeindex_cli))
		self.set(config_out, 'generation', 'makeindex_flags', self.to_cli(config.generation.makeindex_flags))

		self.set(config_out, 'generation', 'dvi2ps_cmd', self.to_cli(config.generation.dvips_cli))
		self.set(config_out, 'generation', 'dvi2ps_flags', self.to_cli(config.generation.dvips_flags))

		if config.generation.makeindex_style_filename:
			if config.generation.makeindex_style_filename == config.get_system_ist_file():
				self.set(config_out, 'generation', 'makeindex style', '@system')
			elif os.path.dirname(config.generation.makeindex_style_filename) == config.document_directory:
				self.set(config_out, 'generation', 'makeindex style', '@detect@system')
			else:
				self.set(config_out, 'generation', 'makeindex style', config.generation.makeindex_style_filename)

		config_out.add_section('viewer')

		self.set(config_out, 'viewer', 'view', self.to_bool(config.view.view))

		self.set(config_out, 'viewer', 'viewer', self.to_cli(config.view.viewer_cli))

		clean_files = config.clean.clean_files
		cleanall_files = config.clean.cleanall_files
		if clean_files or cleanall_files:
			config_out.add_section('clean')
			self.set(config_out, 'clean', 'files to clean', self.to_paths(clean_files,  dout))
			self.set(config_out, 'clean', 'files to desintegrate', self.to_paths(cleanall_files,  dout))

		for translator,  included in config.translators.translators().items():
			config_out.add_section(translator)
			self.set(config_out, translator, 'include module', self.to_bool(included))

		with open(filename, 'w') as configfile:
			config_out.write(configfile)
			
