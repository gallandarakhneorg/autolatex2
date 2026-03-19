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

import platform
import os
import shutil
import unittest
from typing import override
from unittest import skip

from autolatex2.config.configobj import Config
from autolatex2.config.configreader import OldStyleConfigReader
from autolatex2tests.cli.commands.abstract_command_test import AbstractCommandTest


class TestCommitAction(AbstractCommandTest):

	def __init__(self, x):
		super().__init__(x, 'commit')
		
	@override
	def setUp(self):
		super().setUp()
		self._initialize_test_folder()

	def _initialize_test_folder(self):
		self._working_directory = os.getcwd()
		self._resource_directory2 = os.path.normpath(os.path.join(os.path.dirname(__file__),  '..', '..', 'dev-resources'))
		self._resource_directory = os.path.normpath(os.path.join(self._resource_directory2, 'translators'))
		self._resource_directory = os.path.normpath(os.path.join(self._resource_directory2, 'translators'))

		self._tmp_folder = self._create_temp_directory()
		self._tmp_folder_name = self._tmp_folder.name
		self._img_folder = os.path.normpath(os.path.join(self._tmp_folder_name, 'imgs', 'auto'))

		self._config = Config()
		self._config.document_directory = self._tmp_folder_name
		self._config.document_filename = 'rootfile.tex'
		self._config.translators.is_translator_enable = True
		self._config.translators.ignore_user_translators = True
		self._config.translators.ignore_document_translators = True
		config_reader = OldStyleConfigReader()
		config_reader.read_system_config_safely(self._config)
		config_reader.read_user_config_safely(self._config)

		os.makedirs(self._img_folder)
		shutil.copyfile(os.path.normpath(os.path.join(self._resource_directory, 'testimg.svg')),
						os.path.normpath(os.path.join(self._img_folder, 'img1.svg')))
		shutil.copyfile(os.path.normpath(os.path.join(self._resource_directory, 'testimg.svg')),
						os.path.normpath(os.path.join(self._img_folder, 'img2.svg')))
		shutil.copyfile(os.path.normpath(os.path.join(self._resource_directory, 'testimg.jpg.gz')),
						os.path.normpath(os.path.join(self._img_folder, 'img3.jpg.gz')))
		shutil.copyfile(os.path.normpath(os.path.join(self._resource_directory2, 'test20.tex')),
						os.path.normpath(os.path.join(self._tmp_folder_name, 'rootfile.tex')))


	@override
	def tearDown(self):
		super().tearDown()
		self._delete_temp_directory(self._tmp_folder)

	def test_wo_cmd(self):
		with self.assertRaises(Exception):
			self.do_test(config=self._config)

	def test_w_empty_cmd(self):
		self._config.scm.commit_cli = []
		with self.assertRaises(Exception):
			self.do_test(config=self._config)

	def test_w_invalid_cmd(self):
		self._config.scm.commit_cli = ['invalid-shell-command']
		with self.assertRaises(Exception):
			self.do_test(config=self._config)

	@skip
	def test_w_valid_cmd(self):
		command = "dir" if platform.system() == "Windows" else "ls"
		self._config.scm.commit_cli = [command]
		self.do_test(config=self._config)


if __name__ == '__main__':
	unittest.main()

