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
Configuration for the Cleaning feature.
"""

import os

class CleanConfig:
	"""
	Configuration of a AutoLaTeX instance.
	This configuration is based on two lists of filenames.
	These filenames correspond to files that must be cleaned
	during the "clean" state or the "cleanall" stage.
	"""

	def __init__(self):
		self.__clean_files = list()
		self.__cleanall_files = list()

	def reset_internal_attributes(self):
		"""
		Reset the internal attributes.
		"""
		self.__clean_files = list()
		self.__cleanall_files = list()

	@property
	def clean_files(self) -> list[str]:
		"""
		List of files to be removed during the "clean" stage.
		:return: the list of filenames.
		:rtype: list[str]
		"""
		return self.__clean_files

	@clean_files.setter
	def clean_files(self, files : list[str] | str | None):
		"""
		Change the list of files to be removed durin the "clean" stage.
		:param files: the specification of filenames. This specification may be a list of filenames or a single string containing te filenames separated by the path seperator, e.g., ':' on Unix systems and ';' on Windows systems.
		"""
		if files is None:
			self.__clean_files = list()
		elif isinstance(files,  list):
			self.__clean_files = files
		else:
			self.__clean_files = str(files).split(os.pathsep)

	def add_clean_file(self, file : str):
		"""
		Add a file to the list of files to be removed during the "clean" stage.
		:param file: file name
		:type: str
		"""
		if file:
			self.__clean_files.append(file)

	@property
	def cleanall_files(self) -> list[str]:
		"""
		List of files to be removed during the "cleanall" stage.
		:return: the list of filenames.
		:rtype: list[str]
		"""
		return self.__cleanall_files

	@cleanall_files.setter
	def cleanall_files(self, files : list[str] | str | None):
		"""
		Change the list of files to be removed durin the "cleanall" stage.
		:param files: the specification of filenames. This specification may be a list of filenames or a single string containing te filenames separated by the path seperator, e.g., ':' on Unix systems and ';' on Windows systems.
		"""
		if files is None:
			self.__cleanall_files = list()
		elif isinstance(files,  list):
			self.__cleanall_files = files
		else:
			self.__cleanall_files = str(files).split(os.pathsep)

	def add_cleanall_file(self, file : str):
		"""
		Add a file to the list of files to be removed during the "cleanall" stage.
		:param file: file name
		:type: str
		"""
		if file:
			self.__cleanall_files.append(file)


