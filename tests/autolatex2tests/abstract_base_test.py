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

import logging
import os
import tempfile
import unittest
from abc import ABC
from typing import override

from autolatex2.make.filedescription import FileDescription
from autolatex2.tex.utils import FileType
from autolatex2.utils import extprint


class AbstractBaseTest(unittest.TestCase,ABC):

	def __init__(self, x):
		super().__init__(x)
		self.__auto_delete = True
		extprint.IS_ACTIVATED = False
		logging.getLogger().setLevel(logging.CRITICAL)

	@property
	def autodelete(self):
		return self.__auto_delete

	@autodelete.setter
	def autodelete(self, enable : bool):
		self.__auto_delete = enable

	@property
	def detaillogging(self):
		return extprint.IS_ACTIVATED

	@detaillogging.setter
	def detaillogging(self, enable : bool):
		extprint.IS_ACTIVATED = enable

	@override
	def shortDescription(self) -> str | None:
		# Return a custom name based on the test method's docstring or logic
		name = super().shortDescription()
		if not name:
			name = self._testMethodName
		if name.startswith('test_'):
			name = name[5:]
		return name

	def _create_temp_directory(self, delete : bool = False) -> tempfile.TemporaryDirectory:
		"""
		Create and configure a temporary directory for the tests.
		:return: The temporary folder
		:rtype: tempfile.TemporaryDirectory
		"""
		directory = tempfile.TemporaryDirectory(delete=delete)
		with open(os.path.join(directory.name, '.test_id.json'), 'wt') as f:
			f.write(str('{\n\tid: "%s",\n\tdescription: "%s"\n}' % (self.id(), self.shortDescription())))
		return directory

	def _delete_temp_directory(self, directory : tempfile.TemporaryDirectory):
		"""
		Delete if possible the temporary directory for the tests.
		:param directory: The temporary folder to delete
		:type directory: tempfile.TemporaryDirectory
		"""
		if directory is not None and self.autodelete:
			directory.cleanup()

	@property
	def root_file(self):
		raise NotImplementedError()

	def __assertBuildingListItem(self, i : int, expected : dict, actual : FileDescription):
		self.assertEqual(expected['output_filename'], actual.output_filename, "Invalid output filename for actual #%d" % i)
		self.assertEqual(expected['input_filename'], actual.input_filename, "Invalid input filename for actual #%d" % i)
		self.assertEqual(expected['type'], actual.file_type, "Invalid file type for actual #%d" % i)
		self.assertEqual(self.root_file, actual.main_filename, "Invalid main filename for actual #%d" % i)
		self.assertFalse(actual.use_biber, "Unexpected Biber usage for actual #%d" % i)
		self.assertFalse(actual.use_xindy, "Unexpected Xindy usage for actual #%d" % i)

	# noinspection PyMethodMayBeStatic
	def __index_of(self, expected : list, output_filename : str, input_filename : str, file_type : FileType) -> int:
		i = 0
		for element in expected:
			if isinstance(element, dict):
				if ('type' in element and element['type'] == file_type and
					'output_filename' in element and element['output_filename'] == output_filename and
					'input_filename' in element and element['input_filename'] == input_filename):
					return i
			i += 1
		return -1

	def assertBuildingList(self, expected : list[dict|list[dict]], actual : list[FileDescription]):
		if not expected:
			self.assertFalse(actual, "Unexpected value for for actual. It is expected to be empty")
		else:
			i = 0
			j = 0
			candidate = expected[j]
			for actual_element in actual:
				if not candidate:
					j += 1
					candidate = expected[j]
				if isinstance(candidate, list):
					# Multiple candidates that may be found without a specific order
					idx = self.__index_of(candidate, actual_element.output_filename,
										  actual_element.input_filename, actual_element.file_type)
					if idx < 0 or idx >= len(candidate):
						self.fail('Unexpected element with index %d:  %s' % (idx, repr(actual_element)))
					else:
						found_candidate = candidate[idx]
						self.__assertBuildingListItem(i, dict(found_candidate), actual_element)
						del candidate[idx]
				else:
					# A specific item that must be next available
					self.__assertBuildingListItem(i, dict(candidate), actual_element)
					candidate = None
				i += 1

	def assertBuildingListOrder(self, build_list : list[FileDescription], *types : FileType):
		atypes = [ *types ]
		for build_item in build_list:
			if atypes and build_item.file_type == atypes[0]:
				# The build item corresponds to the first expected type
				atypes = atypes[1:]
		if atypes:
			self.fail("File type %s not found" % atypes[0].name)
