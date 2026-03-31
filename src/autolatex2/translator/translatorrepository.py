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
from argparse import ArgumentError
from typing import override, Iterator, Self

from sortedcontainers import SortedSet

from autolatex2.config .configobj import Config
from autolatex2.config .translator import TranslatorLevel
from autolatex2.translator.translatorobj import Translator
from autolatex2.utils.extlogging import LogLevel
from autolatex2.utils.i18n import T



class TranslatorConflictError(Exception):

	def __init__(self, msg : str):
		super().__init__(msg)
		self.message : str = msg

	@override
	def __str__(self) -> str:
		return self.message


class SourceTranslatorMapping:
	"""
	Set of translators that maps a source filename extension to its translator.
	"""
	def __init__(self):
		self.__translators : dict[str,Translator] = dict()

	def __contains__(self, item : str) -> bool:
		return item in self.__translators

	def __len__(self) -> int:
		return len(self.__translators)

	def __iter__(self) -> Iterator[tuple[str,Translator]]:
		class _Iter(Iterator):
			def __init__(self, iterator : Iterator):
				self.__iterator : Iterator = iterator
			def __iter__(self) -> Self:
				return self
			def __next__(self) -> tuple[str,Translator]:
				name, translator = self.__iterator.__next__()
				return name, translator
		return _Iter(self.__translators.items().__iter__())

	def __getitem__(self, item : str) -> Translator | None:
		if item in self.__translators:
			return self.__translators[item]
		return None

	def __setitem__(self, source : str, value : Translator):
		assert source is not None and source
		assert value is not None
		self.__translators[source] = value
		return None

	def merge_with(self, new_data : 'SourceTranslatorMapping'):
		"""
		Add the entries from the given translator set in this translator set.
		:param new_data: the translator set to merge inside.
		:type new_data: SourceTranslatorMapping
		"""
		self.__translators.update(new_data.__translators)

	def translators(self) -> Iterator[Translator]:
		"""
		Replies the iterator on the translators that are stored in this set.
		:return: the iterator on the translators.
		"""
		class _Iter(Iterator):
			def __init__(self, iterator : Iterator):
				self.__iterator : Iterator = iterator
			def __iter__(self) -> Self:
				return self
			def __next__(self) -> Translator:
				translator = self.__iterator.__next__()
				return translator
		return _Iter(self.__translators.values().__iter__())



class InstalledTranslatorDescription:
	"""
	Description of the installed translators per level.
	"""
	def __init__(self):
		self.__system_translators = SourceTranslatorMapping()
		self.__user_translators = SourceTranslatorMapping()
		self.__document_translators = SourceTranslatorMapping()

	def __len__(self):
		return len(self.__system_translators) + len(self.__user_translators) + len(self.__document_translators)

	def __getitem__(self, item) -> SourceTranslatorMapping:
		if item == TranslatorLevel.SYSTEM:
			return self.__system_translators
		elif item == TranslatorLevel.USER:
			return self.__user_translators
		elif item == TranslatorLevel.DOCUMENT:
			return self.__document_translators
		raise ArgumentError(item, T('Invalid translator level: %s') % str(item))

	def get_level_for(self, translator_name : str) -> TranslatorLevel | None:
		"""
		Search for the translator in the installed translators, and reply its level.
		:param translator_name: The name of the translator.
		:type translator_name: str
		:return: The level, or None if not found
		:rtype: TranslatorLevel | None
		"""
		if translator_name in self.__document_translators:
			return TranslatorLevel.DOCUMENT
		if translator_name in self.__user_translators:
			return TranslatorLevel.USER
		if translator_name in self.__system_translators:
			return TranslatorLevel.SYSTEM
		return None


class ConflictMapping:
	"""
	Set of translators that are under conflict per source.
	"""
	def __init__(self):
		self.__conflicts : dict[str,set[Translator]] = dict()

	def __contains__(self, item : str) -> bool:
		return item in self.__conflicts

	def __len__(self):
		return len(self.__conflicts)

	def __iter__(self) -> Iterator[tuple[str,set[Translator]]]:
		class _Iter(Iterator):
			def __init__(self, iterator : Iterator):
				self.__iterator : Iterator = iterator
			def __next__(self) -> tuple[str,set[Translator]]:
				name, translators = self.__iterator.__next__()
				return name, translators
		return _Iter(self.__conflicts.items().__iter__())

	def __getitem__(self, item) -> set[Translator]:
		if item not in self.__conflicts:
			self.__conflicts[item] = set()
		return self.__conflicts[item]

	def add_conflict(self, source : str, translator : Translator):
		"""
		Add a translator under conflict.
		:param source: The source name.
		:type source: str
		:param translator: The conflicting translator to add.
		:type translator: Translator
		"""
		assert source is not None and source
		assert translator is not None
		if source not in self.__conflicts:
				self.__conflicts[source] = set()
		self.__conflicts[source].add(translator)

	def remove_conflict(self, source : str):
		"""
		Remove a source from the conflict set.
		:param source: The source name.
		:type source: str
		"""
		assert source is not None and source
		del self.__conflicts[source]


class ConflictingTranslators:
	"""
	Description of conflicting translators per level.
	"""
	def __init__(self):
		self.__system_conflicts = ConflictMapping()
		self.__user_conflicts = ConflictMapping()
		self.__document_conflicts = ConflictMapping()

	def __len__(self):
		return len(self.__system_conflicts) + len(self.__user_conflicts) + len(self.__document_conflicts)

	def __getitem__(self, item) -> ConflictMapping:
		if item == TranslatorLevel.SYSTEM:
			return self.__system_conflicts
		elif item == TranslatorLevel.USER:
			return self.__user_conflicts
		elif item == TranslatorLevel.DOCUMENT:
			return self.__document_conflicts
		raise ArgumentError(item, T('Invalid translator level: %s') % str(item))

	def detect_conflicts(self, translators : dict[Translator,TranslatorLevel]):
		"""
		Detect the conflicts among the installed translators passed as argument and fill up this conflicting
		repository.
		:param translators: The list of installed translators with the highest installation level.
		:type translators: dict[str,TranslatorLevel]
		"""
		self.__system_conflicts = ConflictMapping()
		self.__user_conflicts = ConflictMapping()
		self.__document_conflicts = ConflictMapping()
		# Detect conflicts
		for translator, activation_level in translators.items():
			source = translator.full_source
			for a_level_number in (range(activation_level,TranslatorLevel.DOCUMENT.value + 1)):
				a_level = TranslatorLevel(a_level_number)
				self[a_level][source].add(translator)
		# Remove any entry that are not indicating a translator conflict.
		for level in TranslatorLevel:
			if level != TranslatorLevel.NEVER:
				to_delete = list()
				for source, translators in self[level]:
					if not translators or len(translators) <= 1:
						to_delete.append(source)
				for source in to_delete:
					self[level].remove_conflict(source)


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
		self.configuration : Config = configuration
		self._installed_translators : InstalledTranslatorDescription = InstalledTranslatorDescription()
		self._translator_names : SortedSet = SortedSet()
		self._included_translators : SourceTranslatorMapping = SourceTranslatorMapping()

	def __reset_repositories(self):
		"""
		Reset the internal repositories.
		"""
		self._installed_translators = InstalledTranslatorDescription()
		self._translator_names = SortedSet()
		self._included_translators = SourceTranslatorMapping()

	@property
	def installed_translators(self) -> InstalledTranslatorDescription:
		"""
		Replies the installed translators.
		The function sync() must be call for updating the list of the installed translators.
		:return: The container of the installed translators.
		:rtype: InstalledTranslatorDescription
		"""
		return self._installed_translators

	@property
	def installed_translator_names(self) -> SortedSet:
		"""
		Replies the names of the installed translators.
		:return: The set of the names.
		:rtype: SortedSet
		"""
		return self._translator_names

	@property
	def included_translators(self) -> SourceTranslatorMapping:
		"""
		Replies the included translators.
		The function sync() must be call for updating the list of the included translators.
		:return: The dictionary of the included translators in which the keys are the source types and the values are the translators.
		:rtype: SourceTranslatorMapping
		"""
		return self._included_translators

	def _read_directory(self, *, directory : str, recursive : bool = False, warn : bool = False) -> SourceTranslatorMapping:
		"""
		Detect translators from the translator files installed in the directory.
		:param directory: The path to the directory to explore.
		:type directory: str
		:param recursive: Indicates if the function must recurse in the directories. Default value: False.
		:type recursive: bool
		:param warn: Indicates if the warning may be output or not. Default value: False.
		:type warn: bool
		:return: The loaded translators.
		:rtype: SourceTranslatorMapping
		"""
		loaded_translators = SourceTranslatorMapping()

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

	def get_included_translator_names_with_levels(self) -> dict[str,TranslatorLevel]:
		"""
		Replies the names of the included translators according to the given configuration.
		All the translators are included, except if the configuration specify something different.
		:return: The dictionary with translator names as keys and inclusion levels as values.
		:rtype: dict[str,TranslatorLevel]
		"""
		included = dict()
		for translator_name in self._translator_names:
			install_level = self._installed_translators.get_level_for(translator_name)
			if install_level is not None:
				inc = self.configuration.translators.inclusion_level(translator_name)
				if inc is None:
					included[translator_name] = install_level
				elif  inc != TranslatorLevel.NEVER:
					if inc >= install_level:
						included[translator_name] = TranslatorLevel(inc)
					else:
						included[translator_name] = install_level
		return included

	def get_included_translators_with_levels(self) -> dict[Translator,TranslatorLevel]:
		"""
		Replies the included translators according to the given configuration.
		All the translators are included, except if the configuration specify something different.
		:return: The dictionary with translator names as keys and inclusion levels as values.
		:rtype: dict[Translator,TranslatorLevel]
		"""
		included = dict()
		for translator_name in self._translator_names:
			install_level = self._installed_translators.get_level_for(translator_name)
			if install_level is not None:
				inc = self.configuration.translators.inclusion_level(translator_name)
				if inc is None:
					included[self.get_object_for(translator_name)] = install_level
				elif  inc != TranslatorLevel.NEVER:
					if inc >= install_level:
						included[self.get_object_for(translator_name)] = TranslatorLevel(inc)
					else:
						included[self.get_object_for(translator_name)] = install_level
		return included

	def _detect_conflicts(self) -> ConflictingTranslators:
		"""
		Replies the translators under conflict per level and source according to the given configuration.
		:return: The data structure described by list[level] = dict(source, set(translator)).
		:rtype: list[dict[str,Translator]]
		"""
		conflicts = ConflictingTranslators()
		conflicts.detect_conflicts(self.get_included_translators_with_levels())
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
			self._installed_translators[TranslatorLevel.SYSTEM].merge_with(v0)

		# Load user modules recursively from ~/.autolatex/translators
		if not self.configuration.translators.ignore_user_translators:
			dirname = os.path.join(self.configuration.user_config_directory, 'translators')
			logging.debug(T("Get loadable translators from %s") % dirname)
			v1 = self._read_directory(directory = dirname, recursive=True, warn=True)
			self._installed_translators[TranslatorLevel.USER].merge_with(v1)

		# Load document modules
		directory = self.configuration.document_directory
		if not self.configuration.translators.ignore_document_translators:
			if directory is not None:
				logging.debug(T("Get loadable translators from %s") % directory)
				v2 = self._read_directory(directory=directory, recursive=False, warn=True)
				self._installed_translators[TranslatorLevel.DOCUMENT].merge_with(v2)

		# Load user modules non-recursively the paths specified inside the configurations
		for path in self.configuration.translators.include_paths:
			logging.debug(T("Get loadable translators from %s") % path)
			v3 = self._read_directory(directory=path, recursive=True, warn=True)
			self._installed_translators[TranslatorLevel.DOCUMENT].merge_with(v3)

		# Finalize initialization of the loadable translators.
		for translator in self._installed_translators[TranslatorLevel.SYSTEM].translators():
			translator.level = TranslatorLevel.SYSTEM
			self._translator_names.add(translator.name)
		for translator in self._installed_translators[TranslatorLevel.USER].translators():
			translator.level = TranslatorLevel.USER
			self._translator_names.add(translator.name)
		for translator in self._installed_translators[TranslatorLevel.DOCUMENT].translators():
			translator.level = TranslatorLevel.DOCUMENT
			self._translator_names.add(translator.name)

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

	def _build_included_translator_dict(self) -> SourceTranslatorMapping:
		"""
		Build the dictionary of the included translators.
		:return: The dictionary with source types as keys, and translators as values.
		:rtype: SourceTranslatorMapping
		"""
		included = SourceTranslatorMapping()
		for translator in self.get_included_translators_with_levels().keys():
			source = translator.full_source
			included[source] = translator
		return included

	# noinspection PyMethodMayBeStatic
	def _fail_on_conflict(self, conflicts : ConflictMapping, config_filename : str):
		"""
		Fail if a conflict exists between translators.
		:param conflicts: The list of conflicts, replied by the function _detectConflicts().
		:type conflicts: dict
		:param config_filename: The filename of the configuration file to put in the error message.
		:type config_filename: str
		"""
		for source, translators in conflicts:
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
			assert first_translator is not None
			raise TranslatorConflictError(T("Several possibilities exist for generating a figure from a %s file:\n%s\n\nYou must specify which to include (resp. exclude) with --include (resp. --exclude).\n\nIt is recommended to update your %s file with the following configuration for each translator to exclude (example on the translator %s):\n\n%s\n" %
							(source,
							 msg,
							 config_filename,
							 first_translator.name,
							 exclude_msg )))
