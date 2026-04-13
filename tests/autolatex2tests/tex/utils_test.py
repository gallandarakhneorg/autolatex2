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
import tempfile
import logging
from typing import override

from autolatex2.tex.utils import *

import autolatex2.utils.utilfunctions as genutils
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestUtils(AbstractBaseTest):

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)


	def test_find_aux_files_1_file_wo_subfolder_wo_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0)
			self.assertIsNotNone(aux_files)
			self.assertEqual(1, len(aux_files))
			self.assertTrue(aux_file_0 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_2_files_wo_subfolder_wo_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			aux_file_1 = os.path.join(folder.name, "root_file_0.aux")
			with open(aux_file_1, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0)
			self.assertIsNotNone(aux_files)
			self.assertEqual(2, len(aux_files))
			self.assertTrue(aux_file_0 in aux_files)
			self.assertTrue(aux_file_1 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_3_files_wo_subfolder_wo_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			aux_file_1 = os.path.join(folder.name, "root_file_0.aux")
			with open(aux_file_1, 'w') as f:
				f.write("xyz")
			aux_file_2 = os.path.join(folder.name, "bu1.aux")
			with open(aux_file_2, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0)
			self.assertIsNotNone(aux_files)
			self.assertEqual(3, len(aux_files))
			self.assertTrue(aux_file_0 in aux_files)
			self.assertTrue(aux_file_1 in aux_files)
			self.assertTrue(aux_file_2 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_1_file_w_subfolder_wo_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			subfolder_0 = os.path.join(folder.name, "sub0")
			os.makedirs(subfolder_0)
			aux_sfile_1 = os.path.join(subfolder_0, "sub0.aux")
			with open(aux_sfile_1, 'w') as f:
				f.write("xyz")
			subfolder_1 = os.path.join(folder.name, "sub1")
			os.makedirs(subfolder_1)
			aux_sfile_2 = os.path.join(subfolder_1, "sub1.aux")
			with open(aux_sfile_2, 'w') as f:
				f.write("xyz")
			tex_file_1 = os.path.join(subfolder_1, "sub1.tex")
			with open(tex_file_1, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0)
			self.assertIsNotNone(aux_files)
			self.assertEqual(2, len(aux_files))
			self.assertTrue(aux_file_0 in aux_files)
			self.assertFalse(aux_sfile_1 in aux_files)
			self.assertTrue(aux_sfile_2 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_2_files_w_subfolder_wo_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			aux_file_1 = os.path.join(folder.name, "root_file_0.aux")
			with open(aux_file_1, 'w') as f:
				f.write("xyz")
			subfolder_0 = os.path.join(folder.name, "sub0")
			os.makedirs(subfolder_0)
			aux_sfile_1 = os.path.join(subfolder_0, "sub0.aux")
			with open(aux_sfile_1, 'w') as f:
				f.write("xyz")
			subfolder_1 = os.path.join(folder.name, "sub1")
			os.makedirs(subfolder_1)
			aux_sfile_2 = os.path.join(subfolder_1, "sub1.aux")
			with open(aux_sfile_2, 'w') as f:
				f.write("xyz")
			tex_file_1 = os.path.join(subfolder_1, "sub1.tex")
			with open(tex_file_1, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0)
			self.assertIsNotNone(aux_files)
			self.assertEqual(3, len(aux_files))
			self.assertTrue(aux_file_0 in aux_files)
			self.assertTrue(aux_file_1 in aux_files)
			self.assertFalse(aux_sfile_1 in aux_files)
			self.assertTrue(aux_sfile_2 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_3_files_w_subfolder_wo_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			aux_file_1 = os.path.join(folder.name, "root_file_0.aux")
			with open(aux_file_1, 'w') as f:
				f.write("xyz")
			aux_file_2 = os.path.join(folder.name, "bu1.aux")
			with open(aux_file_2, 'w') as f:
				f.write("xyz")
			subfolder_0 = os.path.join(folder.name, "sub0")
			os.makedirs(subfolder_0)
			aux_sfile_1 = os.path.join(subfolder_0, "sub0.aux")
			with open(aux_sfile_1, 'w') as f:
				f.write("xyz")
			subfolder_1 = os.path.join(folder.name, "sub1")
			os.makedirs(subfolder_1)
			aux_sfile_2 = os.path.join(subfolder_1, "sub1.aux")
			with open(aux_sfile_2, 'w') as f:
				f.write("xyz")
			tex_file_1 = os.path.join(subfolder_1, "sub1.tex")
			with open(tex_file_1, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0)
			self.assertIsNotNone(aux_files)
			self.assertEqual(4, len(aux_files))
			self.assertTrue(aux_file_0 in aux_files)
			self.assertTrue(aux_file_1 in aux_files)
			self.assertTrue(aux_file_2 in aux_files)
			self.assertFalse(aux_sfile_1 in aux_files)
			self.assertTrue(aux_sfile_2 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_1_file_wo_subfolder_w_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0, lambda x: '1' in os.path.basename(x))
			self.assertIsNotNone(aux_files)
			self.assertEqual(0, len(aux_files))
		finally:
			folder.cleanup()

	def test_find_aux_files_2_files_wo_subfolder_w_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			aux_file_1 = os.path.join(folder.name, "root_file_0.aux")
			with open(aux_file_1, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0, lambda x: '1' in os.path.basename(x))
			self.assertIsNotNone(aux_files)
			self.assertEqual(0, len(aux_files))
		finally:
			folder.cleanup()

	def test_find_aux_files_3_files_wo_subfolder_w_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			aux_file_1 = os.path.join(folder.name, "root_file_0.aux")
			with open(aux_file_1, 'w') as f:
				f.write("xyz")
			aux_file_2 = os.path.join(folder.name, "bu1.aux")
			with open(aux_file_2, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0, lambda x: '1' in os.path.basename(x))
			self.assertIsNotNone(aux_files)
			self.assertEqual(1, len(aux_files))
			self.assertFalse(aux_file_0 in aux_files)
			self.assertFalse(aux_file_1 in aux_files)
			self.assertTrue(aux_file_2 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_1_file_w_subfolder_w_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			subfolder_0 = os.path.join(folder.name, "sub0")
			os.makedirs(subfolder_0)
			aux_sfile_1 = os.path.join(subfolder_0, "sub0.aux")
			with open(aux_sfile_1, 'w') as f:
				f.write("xyz")
			subfolder_1 = os.path.join(folder.name, "sub1")
			os.makedirs(subfolder_1)
			aux_sfile_2 = os.path.join(subfolder_1, "sub1.aux")
			with open(aux_sfile_2, 'w') as f:
				f.write("xyz")
			tex_file_1 = os.path.join(subfolder_1, "sub1.tex")
			with open(tex_file_1, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0, lambda x: '1' in os.path.basename(x))
			self.assertIsNotNone(aux_files)
			self.assertEqual(1, len(aux_files))
			self.assertFalse(aux_file_0 in aux_files)
			self.assertFalse(aux_sfile_1 in aux_files)
			self.assertTrue(aux_sfile_2 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_2_files_w_subfolder_w_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			aux_file_1 = os.path.join(folder.name, "root_file_0.aux")
			with open(aux_file_1, 'w') as f:
				f.write("xyz")
			subfolder_0 = os.path.join(folder.name, "sub0")
			os.makedirs(subfolder_0)
			aux_sfile_1 = os.path.join(subfolder_0, "sub0.aux")
			with open(aux_sfile_1, 'w') as f:
				f.write("xyz")
			subfolder_1 = os.path.join(folder.name, "sub1")
			os.makedirs(subfolder_1)
			aux_sfile_2 = os.path.join(subfolder_1, "sub1.aux")
			with open(aux_sfile_2, 'w') as f:
				f.write("xyz")
			tex_file_1 = os.path.join(subfolder_1, "sub1.tex")
			with open(tex_file_1, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0, lambda x: '1' in os.path.basename(x))
			self.assertIsNotNone(aux_files)
			self.assertEqual(1, len(aux_files))
			self.assertFalse(aux_file_0 in aux_files)
			self.assertFalse(aux_file_1 in aux_files)
			self.assertFalse(aux_sfile_1 in aux_files)
			self.assertTrue(aux_sfile_2 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_3_files_w_subfolder_w_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			aux_file_1 = os.path.join(folder.name, "root_file_0.aux")
			with open(aux_file_1, 'w') as f:
				f.write("xyz")
			aux_file_2 = os.path.join(folder.name, "bu1.aux")
			with open(aux_file_2, 'w') as f:
				f.write("xyz")
			subfolder_0 = os.path.join(folder.name, "sub0")
			os.makedirs(subfolder_0)
			aux_sfile_1 = os.path.join(subfolder_0, "sub0.aux")
			with open(aux_sfile_1, 'w') as f:
				f.write("xyz")
			subfolder_1 = os.path.join(folder.name, "sub1")
			os.makedirs(subfolder_1)
			aux_sfile_2 = os.path.join(subfolder_1, "sub1.aux")
			with open(aux_sfile_2, 'w') as f:
				f.write("xyz")
			tex_file_1 = os.path.join(subfolder_1, "sub1.tex")
			with open(tex_file_1, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0, lambda x: '1' in os.path.basename(x))
			self.assertIsNotNone(aux_files)
			self.assertEqual(2, len(aux_files))
			self.assertFalse(aux_file_0 in aux_files)
			self.assertFalse(aux_file_1 in aux_files)
			self.assertTrue(aux_file_2 in aux_files)
			self.assertFalse(aux_sfile_1 in aux_files)
			self.assertTrue(aux_sfile_2 in aux_files)
		finally:
			folder.cleanup()

	def test_create_extended_tex_filename_w_ext(self):
		self.assertEqual("xxxx_autolatex_autogenerated.ltx", create_extended_tex_filename('xxxx.ltx'))

	def test_create_extended_tex_filename_w_otherext(self):
		self.assertEqual("xxxx.txt_autolatex_autogenerated", create_extended_tex_filename('xxxx.txt'))

	def test_create_extended_tex_filename_wo_ext(self):
		self.assertEqual("xxxx_autolatex_autogenerated", create_extended_tex_filename('xxxx'))

	def test_get_original_tex_filename_w_postfix_w_ext(self):
		self.assertEqual("xxxx.ltx", get_original_tex_filename('xxxx_autolatex_autogenerated.ltx'))

	def test_get_original_tex_filename_w_postfix_w_otherext(self):
		self.assertEqual("xxxx_autolatex_autogenerated.txt", get_original_tex_filename('xxxx_autolatex_autogenerated.txt'))

	def test_get_original_tex_filename_w_postfix_wo_ext(self):
		self.assertEqual("xxxx", get_original_tex_filename('xxxx_autolatex_autogenerated'))



if __name__ == '__main__':
	unittest.main()

