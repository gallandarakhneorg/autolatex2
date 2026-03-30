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

import unittest
import logging
from typing import override

from autolatex2.make.filedescription import FileDescription
from autolatex2.tex.utils import FileType
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestMakeFileDescription(AbstractBaseTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__desc = FileDescription('./path0/filename0.aux', FileType.tex, './path0/filename0.tex', './path0/main0.tex')

	def test___str__(self):
		self.assertEqual('./path0/filename0.aux', str(self.__desc))

	def test___repr__(self):
		self.assertEqual('{\n    "output_filename": "./path0/filename0.aux",\n    "input_filename": "./path0/filename0.tex",\n    "type": 0,\n    "mainfile": "./path0/main0.tex",\n    "change": null,\n    "use_biber": false,\n    "use_xindy": false,\n    "dependencies": []\n}', repr(self.__desc))

	def test_file_type(self):
		self.assertEqual(FileType.tex, self.__desc.file_type)

	def test_output_filename(self):
		self.assertEqual('./path0/filename0.aux', self.__desc.output_filename)

	def test_input_filename(self):
		self.assertEqual('./path0/filename0.tex', self.__desc.input_filename)

	def test_dependencies(self):
		self.assertEqual('SortedSet([])', str(self.__desc.dependencies))

	def test_mainfilename(self):
		self.assertEqual('./path0/main0.tex', self.__desc.main_filename)

	def test_change(self):
		self.assertIsNone(self.__desc.change)

	def test_use_biber(self):
		self.assertFalse(self.__desc.use_biber)

	def test_set_use_biber(self):
		self.__desc.use_biber = True		
		self.assertTrue(self.__desc.use_biber)

	def test_use_xindy(self):
		self.assertFalse(self.__desc.use_xindy)

	def test_set_use_xindy(self):
		self.__desc.use_xindy = True		
		self.assertTrue(self.__desc.use_xindy)


if __name__ == '__main__':
	unittest.main()

