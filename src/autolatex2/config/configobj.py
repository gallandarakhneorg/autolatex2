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
Configuration of the program instance.
"""

import os
import re
import json
import inspect
from json import JSONEncoder
from typing import override, Any

from autolatex2.config import logging
from autolatex2.config.generation import GenerationConfig
from autolatex2.config.translator import TranslatorConfig
from autolatex2.config.view import ViewerConfig
from autolatex2.config.logging import LoggingConfig
from autolatex2.config.scm import ScmConfig
from autolatex2.config.clean import CleanConfig

import gettext

from autolatex2.tex.utils import FileType
from autolatex2.utils.i18n import T


class Config:
	"""
	Configuration of the program instance.
	"""

	DEFAULT_INFINITE_LOOP_DELAY : int = 2

	DEFAULT_CLI_ACTION : str = 'all'

	def __init__(self):
		self.__python_interpreter : str = 'python3'
		self.__os_name : str | None = None
		self.__home_directory : str | None = None
		self.__user_directory : str | None = None
		self.__user_file : str | None = None
		self.__document_directory : str | None = None
		self.__document_filename : str | None = None
		self.__installation_directory : str | None = None
		self.__autolatex_script_name : str | None = None
		self.__autolatex_launch_name : str | None = None
		self.__autolatex_version : str | None = None
		self.__infinite_loop : bool = False
		self.__infinite_loop_delay : int = Config.DEFAULT_INFINITE_LOOP_DELAY
		self.__default_cli_action : str = Config.DEFAULT_CLI_ACTION
		self.__generation : GenerationConfig | None = None
		self.__translation : TranslatorConfig | None = None
		self.__view : ViewerConfig | None = None
		self.__logging : LoggingConfig | None = None
		self.__scm : ScmConfig | None = None
		self.__clean : CleanConfig | None = None

	def reset_internal_attributes(self, os_name : str):
		"""
		Reset the internal attributes.
		:param os_name: the new OS name.
		:type os_name: str
		"""
		self.__python_interpreter = 'python3'
		self.__os_name = os_name
		self.__home_directory = None
		self.__user_directory = None
		self.__user_file = None
		self.__document_directory = None
		self.__document_filename = None
		self.__installation_directory = None
		self.__autolatex_script_name = None
		self.__autolatex_launch_name = None
		self.__autolatex_version = None
		self.__infinite_loop = False
		self.__infinite_loop_delay = Config.DEFAULT_INFINITE_LOOP_DELAY
		self.__default_cli_action = Config.DEFAULT_CLI_ACTION

		if self.__generation is not None:
			self.__generation.reset_internal_attributes()
		if self.__translation is not None:
			self.__translation.reset_internal_attributes()
		if self.__view is not None:
			self.__view.reset_internal_attributes()
		if self.__logging is not None:
			self.__logging.reset_internal_attributes()
		if self.__scm is not None:
			self.__scm.reset_internal_attributes()
		if self.__clean is not None:
			self.__clean.reset_internal_attributes()

	@override
	def __str__(self) -> str:
		"""
		Replies the string representation of the program configuration.
		:return: the string representation of the configuration.
		:rtype: str
		"""
		return self.to_json()

	@override
	def __repr__(self) -> str:
		"""
		Replies the representation of the program configuration.
		:return: the representation of the configuration.
		:rtype: str
		"""
		return self.to_json()

	def to_json(self) -> str:
		"""
		Replies the JSON representation for this configuration.
		:return: the JSON representation of the configuration.
		:rtype: str
		"""
		class JsonEncoder(JSONEncoder):
			def default(self, obj) -> dict[str,Any] | list[Any]:
				properties = inspect.getmembers(obj.__class__, lambda o: isinstance(o, property))
				return {k : v.fget(obj) for k, v in properties}
		return json.dumps(self, indent=4, cls=JsonEncoder)

	@property
	def python_interpreter(self) -> str:
		"""
		Name of the python interpreter.
		:return: the name.
		:rtype: str
		"""
		return self.__python_interpreter

	@python_interpreter.setter
	def python_interpreter(self, name : str | None):
		"""
		Change the name of the python interpreter.
		:param name: The name of the interpreter. If None is used, 'python3' is assumed.
		:type name: str
		"""
		if name:
			self.__python_interpreter = name
		else:
			self.__python_interpreter = 'python3'
	
	@property
	def os_name(self) -> str:
		"""
		Replies the name of the OS.
		This name is used by this configuration for building  the property values.
		:return: the name.
		:rtype: str
		"""
		if self.__os_name:
			return self.__os_name
		else:
			return os.name

	@os_name.setter
	def os_name(self, name : str | None):
		"""
		Set the name of the OS.
		This name is used by this configuration for building  the property values.
		:param name: The name of the OS. If None, the value of <code>os.name</code>
		             will be used.
		:type name: str | None
		"""
		self.__os_name = name
	
	@property
	def home_directory(self) -> str:
		"""
		Replies the home directory of the user.
		:return: the absolute filename or None.
		:rtype: str
		"""
		if self.__home_directory:
			return self.__home_directory
		else:
			return os.path.expanduser('~')

	@home_directory.setter
	def home_directory(self, name : str | None):
		"""
		Set the home directory.
		:param name: The home directory, or None to reset to the home directory.
		:type name: str
		"""
		self.__home_directory = name

	def __is_unix(self) -> bool:
		"""
		Replies if the current operating system is using the Unix conventions.
		:return: True if the operating is compatible with Unix; False if another operating system.
		:rtype: bool
		"""
		return self.os_name == 'posix'

	def __is_windows(self) -> bool:
		"""
		Replies if the current operating system is using the Windows conventions.
		:return: True if the operating is compatible with Windows; False if another operating system.
		:rtype: bool
		"""
		return self.os_name == 'nt'

	def make_document_config_filename(self, directory : str) -> str:
		"""
		Replies the filename of the 'project' configuration when
		it is located in the given directory.
		:param directory: The name of the directory in which the main document file is located.
		:type directory: str
		:return: The name of the file in which the document-level configuration is stored.
		:rtype: str
		"""
		if self.__is_unix():
			return os.path.join(directory, ".autolatex_project.cfg")
		else:
			return os.path.join(directory, "autolatex_project.cfg")

	@property
	def user_config_directory(self) -> str:
		"""
		Replies the name of folder where the 'user' configuration is.
		:return: The name of the user-level configuration folder.
		:rtype: str
		"""
		if self.__user_directory is None:
			if self.__is_unix():
				self.__user_directory = os.path.join(self.home_directory, ".autolatex")
			elif self.__is_windows():
				self.__user_directory = os.path.join(self.home_directory, "Local Settings", "Application Data", "autolatex")
			else:
				self.__user_directory = os.path.join(self.home_directory, "autolatex")
		return self.__user_directory or ''

	# noinspection PyMethodMayBeStatic
	def _isdir(self, directory : str) -> bool:
		"""
		Replies if the given directory exists in the operating system.
		:param directory: Name of the directory to test.
		:type directory: str
		:return: True if the directory exists; False otherwise.
		:rtype: bool
		"""
		return os.path.isdir(directory)

	@property
	def user_config_file(self) -> str:
		"""
		Replies the name of file where the 'user' configuration is.
		:return: The name of the file in which the user-level configuration is stored.
		:rtype: str
		"""
		if self.__user_file is None:
			directory = self.user_config_directory
			if self._isdir(directory):
				self.__user_file = os.path.join(directory, 'autolatex.conf')
			elif self.__is_unix():
				self.__user_file = os.path.join(self.home_directory, ".autolatex")
			elif self.__is_windows():
				self.__user_file = os.path.join(self.home_directory, "Local Settings", "Application Data", "autolatex.conf")
			else:
				self.__user_file = os.path.join(self.home_directory, "autolatex.conf")
		return self.__user_file or ''

	@property
	def system_config_file(self) -> str:
		"""
		Replies the name of file where the 'system' configuration is.
		:return: The name of the file in which the system-level configuration is stored.
		:rtype: str
		"""
		return os.path.join(self.installation_directory, 'default.cfg')

	@property
	def document_directory(self) -> str:
		"""
		Replies the directory of the document.
		:return: the name of the directory in which the current TeX document is located.
		:rtype: str
		"""
		return self.__document_directory or ''

	@document_directory.setter
	def document_directory(self, folder : str):
		"""
		Change the document directory.
		:param folder: The path to the folder in which the current LaTeX document is located.
		:type folder: str
		"""
		self.__document_directory = folder

	@property
	def document_filename(self) -> str:
		"""
		Replies the filename of the document, relatively to the document directory.
		:return: the name of the filein if the current TeX document.
		:rtype: str
		"""
		return self.__document_filename or ''

	@document_filename.setter
	def document_filename(self, filename: str):
		"""
		Change the document filename, relatively to the document directory.
		:param filename: The path to the file of the current LaTeX document.
		:type filename: str
		"""
		if filename:
			if not os.path.isabs(filename):
				self.__document_filename = filename
			else:
				ddir = self.document_directory
				if ddir:
					self.__document_filename = os.path.relpath(filename, ddir)
				else:
					self.__document_filename = os.path.relpath(filename)
		else:
			self.__document_filename = None

	def set_document_directory_and_filename(self, current_document : str) -> str | None:
		"""
		Change the document directory and filename.
		If the given path does not contain a document, try to find the directory where
		an AutoLaTeX configuration file is
		located. The search is traversing the parent directory from the current
		document.
		:param current_document: The path to the current LaTeX document.
		:type current_document: str
		:return: The path to the folder where the program configuration was found.
		         It is 'current_document' or a parent directory of 'current_document'.
		:rtype: str | None
		"""
		adir = None
		if self._isdir(current_document):
			directory = current_document
		else:
			directory = os.path.dirname(current_document)
		directory = os.path.abspath(directory)
		document_dir = directory
		cfg_file = self.make_document_config_filename(directory)
		previous_file = ''
		while previous_file != cfg_file and not os.path.exists(cfg_file):
			directory = os.path.dirname(directory)
			previous_file = cfg_file
			cfg_file = self.make_document_config_filename(directory)
		
		if previous_file != cfg_file:
			adir = os.path.dirname(cfg_file)
		else:
			ext = os.path.splitext(current_document)[-1]
			if FileType.is_tex_extension(ext):
				adir = document_dir
		
		if adir is None:
			self.__document_directory = directory
		else:
			self.__document_directory = adir

		if self._isdir(current_document):
			self.__document_filename = None
		else:
			self.__document_filename = os.path.relpath(current_document, self.__document_directory)

		return adir

	# noinspection PyBroadException
	@property
	def installation_directory(self) -> str:
		"""
		Replies the directory in which the program is installed.
		:return: The installation directory of the program.
		:rtype: str
		"""
		if self.__installation_directory is None:
			root = os.path.abspath(os.sep)
			path : str = os.path.dirname(__file__)
			while path and path != root and os.path.isdir(path):
				filename = os.path.join(path, 'VERSION')
				if os.path.isfile(filename):
					try:
						with open (filename, "r") as myfile:
							content = myfile.read().strip()
						if content.startswith('autolatex'):
							self.__installation_directory = path
							return self.__installation_directory or ''
					except BaseException as ex:
						logging.debug(str(ex))
				path = os.path.dirname(path)
		return self.__installation_directory or ''

	@property
	def name(self) -> str:
		"""
		Replies the base filename of the main script.
		:return: The main script filename.
		:rtype: str
		"""
		return self.__autolatex_script_name or ''

	@name.setter
	def name(self, name : str):
		"""
		Change the base filename of the main script.
		:param name: The main script filename.
		:type: str
		"""
		self.__autolatex_script_name = name
		if self.__autolatex_launch_name is None:
			self.__autolatex_launch_name = name

	@property
	def launch_name(self) -> str:
		"""
		Replies the base filename of the command which permits
		to launch the program. It could differ from the name
		due to several links.
		:return: The launchable script filename.
		:rtype: str
		"""
		return self.__autolatex_launch_name or ''

	@launch_name.setter
	def launch_name(self, name : str):
		"""
		Change the base filename of the command which permits
		to launch AutoLaTeX. It could differ from the AutoLaTeX name
		due to several links.
		:param name: The launchable AutoLaTeX script filename.
		:type: str
		"""
		self.__autolatex_launch_name = name
		if self.__autolatex_script_name is None:
			self.__autolatex_script_name = name

	@property
	def version(self) -> str:
		"""
		Replies the current version of the program.
		This number is extracted from the VERSION filename if
		it exists.
		This value must be set with a call to setAutoLaTeXInfo().
		:return: The version number.
		:rtype: str
		"""
		if self.__autolatex_version is None:
			directory =  self.installation_directory
			if directory is not None:
				with open (os.path.join(directory, 'VERSION'), "r") as myfile:
					line = myfile.read().strip()
				m = re.match(r'^autolatex\s+([0-9]+\.[0-9]+(-\S+)?)', line)
				if m:
					self.__autolatex_version = m.group(1)
					if not self.__autolatex_version:
						raise IOError(T("invalid line in the VERSION file: %s") % line)
			else:
				raise IOError(T("installation directory cannot be detected"))
		return self.__autolatex_version or ''

	@property
	def generation(self) -> GenerationConfig:
		"""
		Replies the configuration dedicated to the generation process.
		:return: the generation configuration.
		:rtype: GenerationConfig
		"""
		if self.__generation is None:
			self.__generation = GenerationConfig()
		assert self.__generation is not None
		return self.__generation

	@generation.setter
	def generation(self, config : GenerationConfig):
		"""
		Set the configuration dedicated to the generation process.
		:param config: the generation configuration.
		:type config: GenerationConfig
		"""
		self.__generation = config

	@property
	def view(self) -> ViewerConfig:
		"""
		Replies the configuration dedicated to the view.
		:return: the view configuration.
		:rtype: ViewerConfig
		"""
		if self.__view is None:
			self.__view = ViewerConfig()
		assert self.__view is not None
		return self.__view

	@view.setter
	def view(self, config : ViewerConfig):
		"""
		Set the configuration dedicated to the view process.
		:param config: the view configuration.
		:type config: ViewerConfig
		"""
		self.__view = config

	@property
	def translators(self) -> TranslatorConfig:
		"""
		Replies the configuration dedicated to the translators.
		:return: the translator configuration.
		:rtype: TranslatorConfig
		"""
		if self.__translation is None:
			self.__translation = TranslatorConfig()
		assert self.__translation is not None
		return self.__translation

	@translators.setter
	def translators(self, config : TranslatorConfig):
		"""
		Set the configuration dedicated to the translators.
		:param config: the translator configuration.
		:type config: TranslatorConfig
		"""
		self.__translation = config

	@property
	def logging(self) -> LoggingConfig:
		"""
		Replies the configuration dedicated to the logging system.
		:return: the logging configuration.
		:rtype: LoggingConfig
		"""
		if self.__logging is None:
			self.__logging = LoggingConfig()
		assert self.__logging is not None
		return self.__logging

	@logging.setter
	def logging(self, config : LoggingConfig):
		"""
		Set the configuration dedicated to the logging system.
		:param config: the logging configuration.
		:type config: LoggingConfig
		"""
		self.__logging = config

	@property
	def scm(self) -> ScmConfig:
		"""
		Replies the configuration dedicated to the SCM system.
		:return: the SCM configuration.
		:rtype: ScmConfig
		"""
		if self.__scm is None:
			self.__scm = ScmConfig()
		assert self.__scm is not None
		return self.__scm

	@scm.setter
	def scm(self, config : ScmConfig):
		"""
		Set the configuration dedicated to the SCM system.
		:param config: the SCM configuration.
		:type config: ScmConfig
		"""
		self.__scm = config

	@property
	def infinite_loop(self) -> bool:
		"""
		Replies if the program runs an infinite loop on the generation.
		The "infiniteLoopDelay" property indicates the delay between two runs.
		:return: True if infinite loop is activated.
		:rtype: bool
		"""
		return self.__infinite_loop

	@infinite_loop.setter
	def infinite_loop(self, enable : bool):
		"""
		Change if AutoLaTeX runs an infinite loop on the generation.
		The "infiniteLoopDelay" property indicates the delay between two runs.
		:param enable: True if infinite loop is activated.
		:param enable: bool
		"""
		self.__infinite_loop = enable

	@property
	def infinite_loop_delay(self) -> int:
		"""
		Replies the delay between two runs of the program when it is running in infinite loop.
		:return: The number of seconds to wait.
		:rtype: int
		"""
		return self.__infinite_loop_delay

	@infinite_loop_delay.setter
	def infinite_loop_delay(self, delay : int):
		"""
		Change the delay between two runs of AutoLaTeX when it is running in infinite loop.
		:param delay: The number of seconds to wait.
		:type delay: int
		"""
		if delay <= 0:
			self.infinite_loop_delay = 0
		else:
			self.__infinite_loop_delay = delay

	def get_system_ist_file(self) -> str:
		"""
		Replies the system IST file.
		:return: the IST filename.
		:rtype: str
		"""
		return os.path.join(self.installation_directory, 'default.ist')

	def get_system_sty_file(self) -> str:
		"""
		Replies the system STY file.
		:return: the STY filename.
		:rtype: str
		"""
		return os.path.join(self.installation_directory, 'tex', 'autolatex.sty')

	def get_system_beamer_sty_file(self) -> str:
		"""
		Replies the system Beamer STY file.
		:return: the STY filename.
		:rtype: str
		"""
		return os.path.join(self.installation_directory, 'tex', 'autolatex-beamer.sty')

	@property
	def clean(self) -> CleanConfig:
		"""
		Replies the configuration dedicated to the cleaning feature.
		:return: the cleaning configuration.
		:rtype: CleanConfig
		"""
		if self.__clean is None:
			self.__clean = CleanConfig()
		assert self.__clean is not None
		return self.__clean

	@clean.setter
	def clean(self, config : CleanConfig):
		"""
		Set the configuration dedicated to the cleaning feature.
		:param config: the cleaning configuration.
		:type config: CleanConfig
		"""
		self.__clean = config

	@property
	def default_cli_action(self) -> str:
		"""
		Replies the default command-line action.
		:return: The name of the action.
		:rtype: str
		"""
		return self.__default_cli_action

	@default_cli_action.setter
	def default_cli_action(self, name : str):
		"""
		Change the name of the default command-line action.
		:param name: The name.
		:type name: str
		"""
		if name is None or not name:
			self.__default_cli_action = Config.DEFAULT_CLI_ACTION
		else:
			self.__default_cli_action = name

