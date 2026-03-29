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
