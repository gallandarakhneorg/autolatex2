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
import os.path
import unittest
import logging
from typing import override

from autolatex2.make.stamps import StampManager
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestStampManager(AbstractBaseTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__tmp_folder = self._create_temp_directory()
		self.__tmp_folder_name = self.__tmp_folder.name
		self.__aux_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'doc.aux'))
		self.__bcf_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'doc.bcf'))
		self.__idx_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'myindex.idx'))
		self.__gls_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'myglos.gls'))

		with open(os.path.join(self.__tmp_folder_name, 'mystamps'), "w") as f:
			f.write("BIB(ABC):" + self.__bcf_file + "\n")
			f.write("BIB(XYZ):" + self.__aux_file + "\n")
			f.write("IDX(uvw):" + self.__idx_file + "\n")
			f.write("GLS(123):" + self.__gls_file + "\n")

		self.__manager = StampManager()

	@override
	def tearDown(self):
		super().tearDown()
		self._delete_temp_directory(self.__tmp_folder)


	def test_get_biber_stamp(self):
		self.assertFalse(self.__manager.get_biber_stamp(self.__bcf_file))

	def test_set_biber_stamp(self):
		self.assertFalse(self.__manager.get_biber_stamp(self.__bcf_file))
		self.__manager.set_biber_stamp(self.__bcf_file, "uvw")
		self.assertEqual("uvw", self.__manager.get_biber_stamp(self.__bcf_file))

	def test_get_bibtex_stamp(self):
		self.assertFalse(self.__manager.get_bibtex_stamp(self.__aux_file))

	def test_set_bibtex_stamp(self):
		self.assertFalse(self.__manager.get_bibtex_stamp(self.__aux_file))
		self.__manager.set_bibtex_stamp(self.__aux_file, "123")
		self.assertEqual("123", self.__manager.get_bibtex_stamp(self.__aux_file))

	def test_get_index_stamp(self):
		self.assertFalse(self.__manager.get_index_stamp(self.__idx_file))

	def test_set_index_stamp(self):
		self.assertFalse(self.__manager.get_index_stamp(self.__idx_file))
		self.__manager.set_index_stamp(self.__idx_file, "ABC")
		self.assertEqual("ABC", self.__manager.get_index_stamp(self.__idx_file))

	def test_get_glossary_stamp(self):
		self.assertFalse(self.__manager.get_glossary_stamp(self.__gls_file))

	def test_set_glossary_stamp(self):
		self.assertFalse(self.__manager.get_glossary_stamp(self.__gls_file))
		self.__manager.set_glossary_stamp(self.__gls_file, "XYZ")
		self.assertEqual("XYZ", self.__manager.get_glossary_stamp(self.__gls_file))

	def test_reset(self):
		self.__manager.set_biber_stamp(self.__bcf_file, "uvw")
		self.__manager.set_bibtex_stamp(self.__aux_file, "123")
		self.__manager.set_index_stamp(self.__idx_file, "ABC")
		self.__manager.set_glossary_stamp(self.__gls_file, "XYZ")
		self.__manager.reset()
		self.assertFalse(self.__manager.get_biber_stamp(self.__bcf_file))
		self.assertFalse(self.__manager.get_bibtex_stamp(self.__aux_file))
		self.assertFalse(self.__manager.get_index_stamp(self.__idx_file))
		self.assertFalse(self.__manager.get_glossary_stamp(self.__gls_file))

	def test_read_build_stamps(self):
		self.__manager.read_build_stamps(self.__tmp_folder_name, basename="mystamps")
		self.assertEqual("ABC", self.__manager.get_biber_stamp(self.__bcf_file))
		self.assertEqual("XYZ", self.__manager.get_bibtex_stamp(self.__aux_file))
		self.assertEqual("uvw", self.__manager.get_index_stamp(self.__idx_file))
		self.assertEqual("123", self.__manager.get_glossary_stamp(self.__gls_file))

	def test_write_build_stamps(self):
		self.__manager.set_biber_stamp(self.__bcf_file, "uvw")
		self.__manager.set_bibtex_stamp(self.__aux_file, "123")
		self.__manager.set_index_stamp(self.__idx_file, "ABC")
		self.__manager.set_glossary_stamp(self.__gls_file, "XYZ")
		self.__manager.write_build_stamps(self.__tmp_folder_name, basename="mystamps2")
		self.__manager.read_build_stamps(self.__tmp_folder_name, basename="mystamps2")
		self.assertEqual("uvw", self.__manager.get_biber_stamp(self.__bcf_file))
		self.assertEqual("123", self.__manager.get_bibtex_stamp(self.__aux_file))
		self.assertEqual("ABC", self.__manager.get_index_stamp(self.__idx_file))
		self.assertEqual("XYZ", self.__manager.get_glossary_stamp(self.__gls_file))


if __name__ == '__main__':
	unittest.main()

