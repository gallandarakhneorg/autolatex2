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
import unittest
from typing import override

from autolatex2.config.configobj import Config
from autolatex2tests.cli.commands.abstract_command_test import AbstractCommandTest


class TestInitAction(AbstractCommandTest):

	def __init__(self, x):
		super().__init__(x, 'init')

	@override
	def setUp(self):
		super().setUp()
		self._initialize_test_folder()

	def _initialize_test_folder(self):
		self._working_directory = os.getcwd()

		self._tmp_folder = self._create_temp_directory()
		self._tmp_folder_name = self._tmp_folder.name
		self._img_folder = os.path.normpath(os.path.join(self._tmp_folder_name, 'imgs', 'auto'))
		self._main_tex_file = os.path.normpath(os.path.join(self._tmp_folder_name, 'main.tex'))
		self._gitignore_file = os.path.normpath(os.path.join(self._tmp_folder_name, '.gitignore'))

		self._config = Config()

		self._cfg_file = self._config.make_document_config_filename(self._tmp_folder_name)


	@override
	def tearDown(self):
		super().tearDown()
		self._delete_temp_directory(self._tmp_folder)

	def test_regular(self):
		self.do_test('--out', self._tmp_folder_name, config=self._config)
		self.assertTrue(os.path.isfile(self._main_tex_file))
		self.assertTrue(os.path.isfile(self._cfg_file))
		self.assertTrue(os.path.isfile(self._gitignore_file))


	def test_existing_tex_file_wo_force(self):
		with open(self._main_tex_file, "w") as f:
			f.write("test")
		with self.assertRaises(Exception):
			self.do_test('--out', self._tmp_folder_name, config=self._config)
		self.assertTrue(os.path.isfile(self._main_tex_file))
		self.assertFalse(os.path.isfile(self._cfg_file))
		self.assertFalse(os.path.isfile(self._gitignore_file))


	def test_existing_cfg_file_wo_force(self):
		with open(self._cfg_file, "w") as f:
			f.write("test")
		with self.assertRaises(Exception):
			self.do_test('--out', self._tmp_folder_name, config=self._config)
		self.assertFalse(os.path.isfile(self._main_tex_file))
		self.assertTrue(os.path.isfile(self._cfg_file))
		self.assertFalse(os.path.isfile(self._gitignore_file))


	def test_existing_gitignore_file_wo_force(self):
		with open(self._gitignore_file, "w") as f:
			f.write("test")
		with self.assertRaises(Exception):
			self.do_test('--out', self._tmp_folder_name, config=self._config)
		self.assertFalse(os.path.isfile(self._main_tex_file))
		self.assertFalse(os.path.isfile(self._cfg_file))
		self.assertTrue(os.path.isfile(self._gitignore_file))


	def test_existing_tex_file_w_force(self):
		with open(self._main_tex_file, "w") as f:
			f.write("test")
		self.do_test('--out', self._tmp_folder_name, '--force', config=self._config)
		self.assertTrue(os.path.isfile(self._main_tex_file))
		self.assertTrue(os.path.isfile(self._cfg_file))
		self.assertTrue(os.path.isfile(self._gitignore_file))


	def test_existing_cfg_file_w_force(self):
		with open(self._cfg_file, "w") as f:
			f.write("test")
		self.do_test('--out', self._tmp_folder_name, '--force', config=self._config)
		self.assertTrue(os.path.isfile(self._main_tex_file))
		self.assertTrue(os.path.isfile(self._cfg_file))
		self.assertTrue(os.path.isfile(self._gitignore_file))


	def test_existing_gitignore_file_w_force(self):
		with open(self._gitignore_file, "w") as f:
			f.write("test")
		self.do_test('--out', self._tmp_folder_name, '--force', config=self._config)
		self.assertTrue(os.path.isfile(self._main_tex_file))
		self.assertTrue(os.path.isfile(self._cfg_file))
		self.assertTrue(os.path.isfile(self._gitignore_file))


if __name__ == '__main__':
	unittest.main()

