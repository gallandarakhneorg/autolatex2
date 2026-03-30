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
Description of a file for the AutoLaTeX Maker.
"""

import json
from typing import override
from sortedcontainers import SortedSet

from autolatex2.tex.utils import FileType
from autolatex2.utils import utilfunctions as genutils



class FileDescription:
	"""
	Description of a file in the making process.
	"""

	def __init__(self, output_filename : str, file_type : FileType, input_filename : str, main_filename : str):
		"""
		Construct a file description.
		:param output_filename: Name of the file to generate.
		:type output_filename: str
		:param file_type: Type of the file. See FileType.
		:type file_type: FileType
		:param input_filename: Name of the file to read for generating this file.
		:type input_filename: str
		:param main_filename: Name of the main file.
		:type main_filename: str
		"""
		self.__type = file_type
		self.__output_filename = output_filename
		self.__input_filename = input_filename
		self.__main_file = main_filename
		self.__dependencies = SortedSet()
		self.__has_change_date = False
		self.__change_date = None
		self.__use_biber = False
		self.__use_xindy = False

	@override
	def __str__(self):
		return self.__output_filename

	@override
	def __repr__(self):
		js = dict()
		js['output_filename'] = self.output_filename
		js['input_filename'] = self.input_filename
		js['type'] = self.file_type
		js['mainfile'] = self.main_filename
		js['change'] = self.change
		js['use_biber'] = self.use_biber
		js['use_xindy'] = self.use_xindy
		js['dependencies'] = list()
		for dep in self.dependencies:
			js['dependencies'].append(dep)
		return json.dumps(js,  indent = 4)

	@property
	def file_type(self) -> FileType:
		"""
		Replies the type of the file.
		:rtype: FileType
		"""
		return self.__type

	@property
	def output_filename(self) -> str:
		"""
		Replies the name of the output file.
		:rtype: str
		"""
		return self.__output_filename

	@property
	def input_filename(self) -> str:
		"""
		Replies the name of the input file.
		:rtype: str
		"""
		return self.__input_filename

	@property
	def dependencies(self) -> SortedSet:
		"""
		Replies the names of the files that are needed to build the current file.
		:rtype: SortedSet
		"""
		return self.__dependencies

	@property
	def main_filename(self) -> str:
		"""
		Replies the name of the main file.
		:rtype: str
		"""
		return self.__main_file

	@property
	def change(self) -> float | None:
		"""
		Replies the date of the last change of the file.
		:rtype: float|None
		"""
		if not self.__has_change_date:
			self.__has_change_date = True
			self.__change_date = genutils.get_file_last_change(self.__output_filename)
		return self.__change_date

	@property
	def use_biber(self) -> bool:
		"""
		Replies if Biber should be used to generate this file.
		:rtype: bool
		"""
		return self.__use_biber

	@use_biber.setter
	def use_biber(self,  use : bool):
		"""
		Change the flag that indicates if Biber should be used to generate this file.
		:param use: The flag.
		:type use: bool
		"""
		self.__use_biber = use

	@property
	def use_xindy(self) -> bool:
		"""
		Replies if texindy should be used to generate this file.
		:rtype: bool
		"""
		return self.__use_xindy

	@use_xindy.setter
	def use_xindy(self,  use : bool):
		"""
		Change the flag that indicates if texindy should be used to generate this file.
		:param use: The flag.
		:type use: bool
		"""
		self.__use_xindy = use


