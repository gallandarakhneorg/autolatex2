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

import os
import shutil
import tempfile
import unittest
from typing import override

from autolatex2.config.configobj import Config
from autolatex2.config.configreader import OldStyleConfigReader
from autolatex2.make.maker import AutoLaTeXMaker
from autolatex2tests.cli.commands.abstract_command_test import AbstractCommandTest


class TestDocumentAction(AbstractCommandTest):

	def __init__(self, x):
		super().__init__(x, 'makeflat')

	@override
	def setUp(self):
		super().setUp()
		self._initialize_test_folder()

	def _initialize_test_folder(self):
		self._working_directory = os.getcwd()
		self._resource_directory2 = os.path.normpath(os.path.join(os.path.dirname(__file__),  '..', '..', 'dev-resources'))
		self._resource_directory = os.path.normpath(os.path.join(self._resource_directory2, 'translators'))

		self._tmp_folder = self._create_temp_directory()
		self._tmp_folder_name = self._tmp_folder.name
		self._img_base_folder = os.path.normpath(os.path.join(self._tmp_folder_name, 'imgs'))
		self._img_folder = os.path.normpath(os.path.join(self._img_base_folder, 'auto'))

		self._tex_file = os.path.normpath(os.path.join(self._tmp_folder_name, 'rootfile.tex'))
		self._img1_file = os.path.normpath(os.path.join(self._img_folder, 'img1.pdf'))
		self._img2_file = os.path.normpath(os.path.join(self._img_folder, 'img2.pdf'))

		self._flat_tex_file = os.path.normpath(os.path.join(self._tmp_folder_name, 'flat_version', 'rootfile.tex'))
		self._flat_img1_file = os.path.normpath(os.path.join(self._tmp_folder_name, 'flat_version', 'img1.pdf'))
		self._flat_img2_file = os.path.normpath(os.path.join(self._tmp_folder_name, 'flat_version', 'img2.pdf'))

		self._flat_tex_file2 = os.path.normpath(os.path.join(self._tmp_folder_name, 'myflat', 'rootfile.tex'))
		self._flat_img1_file2 = os.path.normpath(os.path.join(self._tmp_folder_name, 'myflat', 'img1.pdf'))
		self._flat_img2_file2 = os.path.normpath(os.path.join(self._tmp_folder_name, 'myflat', 'img2.pdf'))

		self._config = Config()
		self._config.document_directory = self._tmp_folder_name
		self._config.document_filename = 'rootfile.tex'
		self._config.translators.is_translator_enable = True
		self._config.translators.ignore_user_translators = True
		self._config.translators.ignore_document_translators = True
		self._config.translators.add_image_path(self._img_folder)
		config_reader = OldStyleConfigReader()
		config_reader.read_system_config_safely(self._config)
		config_reader.read_user_config_safely(self._config)

		os.makedirs(self._img_folder)

		shutil.copyfile(os.path.normpath(os.path.join(self._resource_directory, 'testimg.svg')),
						os.path.normpath(os.path.join(self._img_folder, 'img1.svg')))
		shutil.copyfile(os.path.normpath(os.path.join(self._resource_directory2, 'test12img.pdf')), self._img1_file)

		shutil.copyfile(os.path.normpath(os.path.join(self._resource_directory, 'testimg.svg')),
						os.path.normpath(os.path.join(self._img_folder, 'img2.svg')))
		shutil.copyfile(os.path.normpath(os.path.join(self._resource_directory2, 'test12img.pdf')), self._img2_file)

		shutil.copyfile(os.path.normpath(os.path.join(self._resource_directory2, 'test25.bib')),
						os.path.normpath(os.path.join(self._tmp_folder_name, 'rootfile.bib')))

		shutil.copyfile(os.path.normpath(os.path.join(self._resource_directory2, 'test25.tex')),
						self._tex_file)

		self.__maker = AutoLaTeXMaker.create(self._config)
		os.chdir(self._tmp_folder_name)
		self.__maker.run_latex(self._tex_file, loop=False)
		self.__maker.run_bibtex(self._tex_file)
		self.__maker.run_makeglossaries(self._tex_file)


	@override
	def tearDown(self):
		super().tearDown()
		os.chdir(self._working_directory)
		self._delete_temp_directory(self._tmp_folder)

	def test_regular(self):
		self.do_test(config=self._config)
		self.assertTrue(os.path.isfile(self._flat_tex_file))
		self.assertTrue(os.path.isfile(self._flat_img1_file))
		self.assertTrue(os.path.isfile(self._flat_img2_file))


	def test_other_folder(self):
		self.do_test('--out', os.path.normpath(os.path.join(self._tmp_folder_name, 'myflat')), config=self._config)
		self.assertTrue(os.path.isfile(self._flat_tex_file2))
		self.assertTrue(os.path.isfile(self._flat_img1_file2))
		self.assertTrue(os.path.isfile(self._flat_img2_file2))

if __name__ == '__main__':
	unittest.main()

