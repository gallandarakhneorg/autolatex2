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
import os
import shutil
from typing import override

from autolatex2.config.configobj import Config
from autolatex2.make.maker import AutoLaTeXMaker
from autolatex2tests.abstract_base_test import AbstractBaseTest


class TestBiblioMaker(AbstractBaseTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__working_directory = os.getcwd()
		self.__resource_directory = os.path.normpath(os.path.join(os.path.dirname(__file__),  '..', 'dev-resources'))
		self.__install_test_environment()

	@override
	def tearDown(self):
		super().tearDown()
		os.chdir(self.__working_directory)
		self._delete_temp_directory(self.__tmp_folder)

	def __install_test_environment(self):
		self.__tmp_folder = self._create_temp_directory()
		self.__tmp_folder_name = self.__tmp_folder.name
		self.__root_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.tex'))
		self.__bib_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.bib'))
		self.__aux_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.aux'))

		self.__config = Config()
		self.__config.document_directory = self.__tmp_folder_name
		self.__config.document_filename = 'rootfile.tex'
		self.__config.generation.is_biber = False

		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test15.tex')), self.__root_file)
		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test15.bib')), self.__bib_file)

		self.__aux_file_0 = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.aux'))
		self.__aux_file_1 = os.path.normpath(os.path.join(self.__tmp_folder_name, 'subfolder0', 'subf0.aux'))
		self.__aux_file_2 = os.path.normpath(os.path.join(self.__tmp_folder_name, 'subfolder1', 'subf1.aux'))
		self.__tex_file_1 = os.path.normpath(os.path.join(self.__tmp_folder_name, 'subfolder1', 'subf1.tex'))
		self.__aux_file_3 = os.path.normpath(os.path.join(self.__tmp_folder_name, 'subfolder2', 'subf2.aux'))
		self.__tex_file_2 = os.path.normpath(os.path.join(self.__tmp_folder_name, 'subfolder2', 'subf2.tex'))
		self.__aux_file_4 = os.path.normpath(os.path.join(self.__tmp_folder_name, 'bu1.aux'))

		self.__create_file(self.__aux_file_0, False)
		self.__create_file(self.__aux_file_1, True)
		self.__create_file(self.__aux_file_2, True)
		self.__create_file(self.__aux_file_3, False)
		self.__create_file(self.__aux_file_4, True)
		self.__create_file(self.__tex_file_1, True)
		self.__create_file(self.__tex_file_2, True)

		self.__maker = AutoLaTeXMaker.create(self.__config)
		os.chdir(self.__tmp_folder_name)


	def __create_file(self, filename, citation: bool):
		os.makedirs(os.path.dirname(filename), exist_ok=True)
		with open(filename, 'w') as f:
			if citation:
				f.write("...\n\\citation{x}\n...\n")


	def test_detect_aux_files_with_biliography_wo_content_check(self):
		result = self.__maker.detect_aux_files_with_biliography(filename=self.__root_file, check_aux_content=False)
		self.assertIsNotNone(result)
		self.assertEqual(4, len(result))
		self.assertTrue(self.__aux_file_0 in result)
		self.assertFalse(self.__aux_file_1 in result)
		self.assertTrue(self.__aux_file_2 in result)
		self.assertTrue(self.__aux_file_3 in result)
		self.assertTrue(self.__aux_file_4 in result)


if __name__ == '__main__':
	unittest.main()

