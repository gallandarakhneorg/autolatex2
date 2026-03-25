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

import os
import re
import logging
from typing import override

from autolatex2.config .configobj import Config
from autolatex2.config .translator import TranslatorLevel
from autolatex2.translator.translatorobj import Translator
from autolatex2.utils.extlogging import LogLevel
from autolatex2.utils.i18n import T



class TranslatorConflictError(Exception):

	def __init__(self, msg : str):
		super().__init__(msg)
		self.message = msg

	@override
	def __str__(self) -> str:
		return self.message



######################################################################
##
class TranslatorRepository:
	"""
	Repository of translators.
	"""

	def __init__(self, configuration : Config):
		"""
		Construct the repository of translators.
		:param configuration: The current configuration.
		:type configuration: Config
		"""
		self.configuration = configuration
		self._installed_translators = None
		self._installed_translator_names = None
		self._included_translators = None
		self.__reset_repositories()

	def __reset_repositories(self):
		"""
		Reset the internal repositories.
		"""
		self._installed_translators : list[dict[str,Translator]] = [None] * 3
		self._installed_translators[TranslatorLevel.SYSTEM] = dict()
		self._installed_translators[TranslatorLevel.USER] = dict()
		self._installed_translators[TranslatorLevel.DOCUMENT] = dict()
		self._installed_translator_names : set[str] = set()
		self._included_translators : dict[str,Translator] = dict()

	@property
	def installed_translators(self) -> list[dict[str,Translator]]:
		"""
		Replies the installed translators.
		The function sync() must be call for updating the list of the installed translators.
		:return: The lists of the dictionary of the installed translators in which the keys are the names and the values are the filename of the translators.
		:rtype: list[dict[str,Translator]]
		"""
		return self._installed_translators

	@property
	def installed_translator_names(self) -> set[str]:
		"""
		Replies the names of the installed translators.
		:return: The set of the names.
		:rtype: set[str]
		"""
		return self._installed_translator_names

	@property
	def included_translators(self) -> dict[str,Translator]:
		"""
		Replies the included translators.
		The function sync() must be call for updating the list of the included translators.
		:return: The dictionary of the included translators in which the keys are the source types and the values are the translators.
		:rtype: dict[str,Translator]
		"""
		return self._included_translators

	def _read_directory(self, *, directory : str, recursive : bool = False, warn : bool = False) -> dict[str,Translator]:
		"""
		Detect translators from the translator files installed in the directory.
		:param directory: The path to the directory to explore.
		:type directory: str
		:param recursive: Indicates if the function must recurse in the directories. Default value: False.
		:type recursive: bool
		:param warn: Indicates if the warning may be output or not. Default value: False.
		:type warn: bool
		:return: The loaded translators.
		:rtype: dict[str,Translator]
		"""
		loaded_translators = dict()

		if os.path.isdir(directory):
			if not os.path.isabs(directory):
				directory = os.path.abspath(directory)
			if recursive:
				for root, dirs, files in os.walk(directory):
					for filename in files:
						m = re.match(r'^([a-zA-Z+-]+2[a-zA-Z0-9+-]+(?:_[a-zA-Z0-9_+-]+)?).transdef([0-9]*)$', filename, re.I)
						if m:
							script_name = m.group(1)
							version = m.group(2)
							if (version and int(version) > 1) or self.configuration.translators.is_translator_fileformat_1_enable:
								translator = Translator(script_name, self.configuration)
								translator.filename = os.path.join(root, filename)
								loaded_translators[script_name] = translator
			else:
				for child in os.listdir(directory):
					abs_path = os.path.join(directory, child)
					if not os.path.isdir(abs_path):
						m = re.match(r'^([a-zA-Z+-]+2[a-zA-Z0-9+-]+(?:_[a-zA-Z0-9_+-]+)?).transdef([0-9]*)$', child, re.I)
						if m:
							script_name = m.group(1)
							version = m.group(2)
							if (version and int(version) > 1) or self.configuration.translators.is_translator_fileformat_1_enable:
								translator = Translator(script_name, self.configuration)
								translator.filename = abs_path
								loaded_translators[script_name] = translator
		elif warn:
			logging.log(LogLevel.FINE_INFO, T("%s is not a directory") % directory)

		return loaded_translators

	def _get_install_level_for(self, translator_name : str) -> TranslatorLevel | None:
		"""
		Search for the translator in the installed translators, and reply its level.
		:param translator_name: The name of the translator.
		:type translator_name: str
		:return: The level, or None if not found
		:rtype: TranslatorLevel | None
		"""
		lvls = list(TranslatorLevel)[1:]
		for level in reversed(lvls):
			if translator_name in self._installed_translators[level.value]:
				return level
		return None

	def get_object_for(self, translator_name : str) -> Translator | None:
		"""
		Search for the translator in the installed translators.
		:param translator_name: The name of the translator.
		:type translator_name: str
		:return: The translator, or None if not found
		:rtype: Translator | None
		"""
		lvls = list(TranslatorLevel)
		for level in reversed(lvls):
			if translator_name in self._installed_translators[level.value]:
				return self._installed_translators[level.value][translator_name]
		return None

	def get_included_translators_with_levels(self) -> dict[str,TranslatorLevel]:
		"""
		Replies the included translators according to the given configuration.
		All the translators are included, except if the configuration specify something different.
		:return: The dictionary with translator names as keys and inclusion levels as values.
		:rtype: dict[str,TranslatorLevel]
		"""
		included = dict()
		for translatorName in self._installed_translator_names:
			install_level = self._get_install_level_for(translatorName)
			if install_level is not None:
				inc = self.configuration.translators.inclusion_level(translatorName)
				if inc is None:
					included[translatorName] = install_level
				elif  inc != TranslatorLevel.NEVER:
					if inc >= install_level:
						included[translatorName] = TranslatorLevel(inc)
					else:
						included[translatorName] = install_level
		return included

	def _detect_conflicts(self) -> list[dict[str,Translator]]:
		"""
		Replies the translators under conflict per level and source according to the given configuration.
		:return: The data structure described by list[level] = dict(source, set(translator)).
		:rtype: list[dict[str,Translator]]
		"""
		conflicts = list([dict(), dict(), dict()])
		# Build the list of the included translators per level
		translators = self.get_included_translators_with_levels()
		for (translatorName, activationLevel) in translators.items():
			translator = self.get_object_for(translatorName)
			source = translator.full_source
			for a_level in (range(activationLevel,len(conflicts))):
				if source not in conflicts[a_level]:
					conflicts[a_level][source] = set()
				conflicts[a_level][source].add(translator)
		# Remove any entry that are not indicating a translator conflict.
		for level_dict in conflicts:
			to_delete = list()
			for k, v in level_dict.items():
				if v and len(v) <= 1:
					to_delete.append(k)
			for k in to_delete:
				del level_dict[k]
		return conflicts

	# noinspection DuplicatedCode
	def sync(self, detect_conflicts : bool = True):
		"""
		Synchronize the repository with directories according to the given configuration.
		:param detect_conflicts: Indicates if the conflicts in translator loading is run. Default is True.
		:type detect_conflicts: bool
		"""
		self.__reset_repositories()

		# Load distribution/system modules
		if not self.configuration.translators.ignore_system_translators:
			dirname = os.path.join(self.configuration.installation_directory, 'translators')
			logging.debug(T("Get loadable translators from %s") % dirname)
			v0 = self._read_directory(directory=dirname, recursive=True, warn=True)
			self._installed_translators[TranslatorLevel.SYSTEM].update(v0)

		# Load user modules recursively from ~/.autolatex/translators
		if not self.configuration.translators.ignore_user_translators:
			dirname = os.path.join(self.configuration.user_config_directory, 'translators')
			logging.debug(T("Get loadable translators from %s") % dirname)
			v1 = self._read_directory(directory = dirname, recursive=True, warn=True)
			self._installed_translators[TranslatorLevel.USER].update(v1)

		# Load document modules
		directory = self.configuration.document_directory
		if not self.configuration.translators.ignore_document_translators:
			if directory is not None:
				logging.debug(T("Get loadable translators from %s") % directory)
				v2 = self._read_directory(directory=directory, recursive=False, warn=True)
				self._installed_translators[TranslatorLevel.DOCUMENT].update(v2)

		# Load user modules non-recursively the paths specified inside the configurations
		for path in self.configuration.translators.include_paths:
			logging.debug(T("Get loadable translators from %s") % path)
			v3 = self._read_directory(directory=path, recursive=True, warn=True)
			self._installed_translators[TranslatorLevel.DOCUMENT].update(v3)

		# Finalize initialization of the loadable translators.
		for translator in self._installed_translators[TranslatorLevel.SYSTEM].values():
			translator.level = TranslatorLevel.SYSTEM
			self._installed_translator_names.add(translator.name)
		for translator in self._installed_translators[TranslatorLevel.USER].values():
			translator.level = TranslatorLevel.USER
			self._installed_translator_names.add(translator.name)
		for translator in self._installed_translators[TranslatorLevel.DOCUMENT].values():
			translator.level = TranslatorLevel.DOCUMENT
			self._installed_translator_names.add(translator.name)

		# Determine the included translators
		if detect_conflicts:
			conflicts = self._detect_conflicts()
			if directory:
				specific_conflicts = conflicts[TranslatorLevel.DOCUMENT]
				filename = self.configuration.make_document_config_filename(directory)
			else:
				specific_conflicts = conflicts[TranslatorLevel.USER]
				filename = self.configuration.user_config_file

			self._fail_on_conflict(specific_conflicts, filename)

		# Save the included translators
		self._included_translators = self._build_included_translator_dict()

	def _build_included_translator_dict(self) -> dict[str,Translator]:
		"""
		Build the dictionary of the included translators.
		:return: The dictionary with source types as keys, and translators as values.
		:rtype: dict[str,Translator]
		"""
		included = dict()
		for translatorName in self.get_included_translators_with_levels():
			translator = self.get_object_for(translatorName)
			source = translator.full_source
			included[source] = translator
		return included

	# noinspection PyMethodMayBeStatic
	def _fail_on_conflict(self, conflicts : dict, config_filename : str):
		"""
		Fail if a conflict exists between translators.
		:param conflicts: The list of conflicts, replied by the function _detectConflicts().
		:type conflicts: dict
		:param config_filename: The filename of the configuration file to put in the error message.
		:type config_filename: str
		"""
		for source, translators in conflicts.items():
			msg = ''
			exclude_msg = ''
			first_translator = None
			for translator in translators:
				if msg:
					msg += ",\n"
				msg += str(translator)
				if first_translator is None:
					exclude_msg += "[%s]\ninclude module = yes\n" % translator.name
					first_translator = translator
				else:
					exclude_msg += "[%s]\ninclude module = no\n" % translator.name
			raise TranslatorConflictError(T("Several possibilities exist for generating a figure from a %s file:\n%s\n\nYou must specify which to include (resp. exclude) with --include (resp. --exclude).\n\nIt is recommended to update your %s file with the following configuration for each translator to exclude (example on the translator %s):\n\n%s\n" %
							(source,
							 msg,
							 config_filename,
							 first_translator.name,
							 exclude_msg )))
