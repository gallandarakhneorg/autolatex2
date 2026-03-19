#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 1998-2021 Stephane Galland <galland@arakhne.org>
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
Configuration for the translators.
"""

from enum import IntEnum, unique

import gettext
_T = gettext.gettext


######################################################################
##
@unique
class TranslatorLevel(IntEnum):
	"""
	Level of execution of a translator.
	"""
	NEVER = -1
	SYSTEM = 0
	USER = 1
	DOCUMENT = 2

	def __str__(self):
		return _T(self.name.lower())


class TranslatorConfig:
	"""
	Configuration of the AutoLaTeX translators.
	"""

	def __init__(self):	
		self.__ignore_system_translators = False
		self.__ignore_user_translators = False
		self.__ignore_document_translators = False
		self.__include_paths = list()
		self.__image_paths = list()
		self.__images_to_convert = set()
		self.__recursive_image_path = True
		self.__inclusions = list((dict(), dict(), dict()))
		self.__is_translator_enable = True
		self.__enable_translatorfile_format_1 = False

	def reset_internal_attributes(self):
		"""
		Reset the internal attributes.
		"""
		self.__ignore_system_translators = False
		self.__ignore_user_translators = False
		self.__ignore_document_translators = False
		self.__include_paths = list()
		self.__image_paths = list()
		self.__images_to_convert = set()
		self.__recursive_image_path = True
		self.__inclusions = list((dict(), dict(), dict()))
		self.__is_translator_enable = True
		self.__enable_translatorfile_format_1 = False

	@property
	def is_translator_fileformat_1_enable(self) -> bool:
		"""
		Replies if the reading of the translators' fils in format 1 is activated.
		:rtype: bool
		"""
		return self.__enable_translatorfile_format_1

	@is_translator_fileformat_1_enable.setter
	def is_translator_fileformat_1_enable(self, enable : bool):
		"""
		Change the activation flag for the reading of the translators' fils in format 1.
		:type enable: bool
		"""
		self.__enable_translatorfile_format_1 = enable

	@property
	def is_translator_enable(self) -> bool:
		"""
		Replies if the translators are activated.
		:rtype: bool
		"""
		return self.__is_translator_enable

	@is_translator_enable.setter
	def is_translator_enable(self, enable : bool):
		"""
		Change the activation flag for the translators.
		:type enable: bool
		"""
		self.__is_translator_enable = enable

	@property
	def ignore_system_translators(self) -> bool:
		return self.__ignore_system_translators

	@ignore_system_translators.setter
	def ignore_system_translators(self, ignore : bool):
		self.__ignore_system_translators = ignore

	@property
	def ignore_user_translators(self) -> bool:
		return self.__ignore_user_translators

	@ignore_user_translators.setter
	def ignore_user_translators(self, ignore : bool):
		self.__ignore_user_translators = ignore

	@property
	def ignore_document_translators(self) -> bool:
		return self.__ignore_document_translators

	@ignore_document_translators.setter
	def ignore_document_translators(self, ignore : bool):
		self.__ignore_document_translators = ignore

	@property
	def include_paths(self) -> list[str]:
		"""
		Replies the inclusion paths for the translators.
		:rtype: list
		"""
		return self.__include_paths

	@include_paths.setter
	def include_paths(self, path : list[str] | None):
		"""
		Set the inclusion paths for the translators.
		:param path: The inclusion paths.
		:type path: list
		"""
		if path is None:
			self.__include_paths = list()
		else:
			for p in path:
				if p is None:
					raise Exception(_T('Illegal None value for the include path'))
			self.__include_paths = list(path)

	def add_include_path(self, path : str | None):
		"""
		Add a translator path for the translators.
		:param path: the path to add.
		:type path: str
		"""
		if path is None:
			raise Exception(_T('Illegal None value for the include path'))
		self.__include_paths.append(path)

	@property
	def image_paths(self) -> list[str]:
		"""
		Replies the image paths for the translators.
		:rtype: list
		"""
		return self.__image_paths

	@image_paths.setter
	def image_paths(self, path : list[str] | None):
		"""
		Set the image paths for the translators.
		:param path: The image paths.
		:type path: list
		"""
		if path is None:
			self.__image_paths = list()
		else:
			self.__image_paths = path

	def add_image_path(self, path : str):
		"""
		Add an image path for the translators.
		:param path: the path to add.
		:type path: str
		"""
		self.__image_paths.append(path)

	@property
	def images_to_convert(self) -> set[str]:
		"""
		Replies the images to convert that are manually specified.
		:rtype: set
		"""
		return self.__images_to_convert

	@images_to_convert.setter
	def images_to_convert(self, images : set[str]):
		"""
		Set manually the image to convert.
		:param images: The images.
		:type images: set
		"""
		self.__images_to_convert = images

	def add_image_to_convert(self, img_path : str):
		"""
		Add an image to be converted.
		:param img_path: the path of the image to convert.
		:type img_path: str
		"""
		self.__images_to_convert.add(img_path)

	@property
	def recursive_image_path(self) -> bool:
		"""
		Replies if the image search is recursive in the directory tree.
		:rtype: bool
		"""
		return self.__recursive_image_path

	@recursive_image_path.setter
	def recursive_image_path(self, recursive : bool):
		"""
		Set if the image search is recursive in the directory tree.
		:param recursive: True if recursive.
		:type recursive: bool
		"""
		self.__recursive_image_path = recursive

	@property
	def inclusions(self) -> list[dict[str,str]]:
		"""
		Replies the inclusion configuration.
		:return: The internal data structure for specifying the inclusions.
		:rtype: list
		"""
		return self.__inclusions

	def set_included(self, translator : str, level : TranslatorLevel | None, included : bool | None):
		"""
		Set if the given translator is marked as included in configuration.
		:param translator: The name of the translator.
		:type translator: str
		:param level: The level at which the inclusion must be considered (see TranslatorLevel enumeration).
		:type level: TranslatorLevel | None
		:param included: True if included. False if not included. None if not specified in the configuration.
		:type included: bool | None
		:
		"""
		if level is None or level == TranslatorLevel.NEVER:
			level = TranslatorLevel.SYSTEM
		if included is None:
			if translator in self.__inclusions[level.value]:
				del self.__inclusions[level.value][translator]
		else:
			self.__inclusions[level.value][translator] = included

	def included(self, translator : str, level : TranslatorLevel, inherit : bool = True) -> bool | None:
		"""
		Replies if the given translator is marked as included in configuration.
		:param translator: The name of the translator.
		:type translator: str
		:param level: The level at which the inclusion must be considered (see TranslatorLevel enumeration).
		:type level: TranslatorLevel
		:param inherit: Indicates if the inclusions of the lower levels are inherited. Default value: True.
		:type inherit: bool
		:return: The inclusion. True if included. False if not included. None if not specified in the configuration.
		:rtype: bool
		:
		"""
		if level is None or level == TranslatorLevel.NEVER or not translator:
			return None
		if inherit:
			# +1 because of the NEVER element at index 0
			# +1 because of the use of the range operator: [start_index:end_index+1]
			max_level = int(level.value) + 2
			lvls = list(TranslatorLevel)[1:max_level]
			for level in reversed(lvls):
				if translator in self.__inclusions[level.value] and self.__inclusions[level.value][translator] is not None:
					return self.__inclusions[level.value][translator]
		elif translator in self.__inclusions[level.value]:
			return self.__inclusions[level.value][translator]
		return None

	def inclusion_level(self, translator : str) -> TranslatorLevel | None:
		"""
		Replies the highest level at which the translator is included.
		:param translator: The name of the translator.
		:type translator: str
		:return: The inclusion level (see TranslatorLevel enumeration) or None if not included or 'unspecified' if not specified.
		:rtype: TranslatorLevel
		:
		"""
		lvls = list(TranslatorLevel)[1:]
		for level in reversed(lvls):
			if translator in self.__inclusions[level.value] and self.__inclusions[level.value][translator] is not None:
				if self.__inclusions[level.value][translator]:
					return level
				else:
					return TranslatorLevel.NEVER
		return None

	def translators(self) -> dict[str,bool]:
		"""
		Replies the list of the registered translators with their inclusion status.
		:return: The pairs of translator names and inclusion status.
		:rtype: dict
		:
		"""
		trans = dict()
		lvls = list(TranslatorLevel)[1:]
		for level in reversed(lvls):
			for translator,  included in self.__inclusions[level].items():
				if translator not in trans and included is not None:
					trans[translator] = included
		return trans
