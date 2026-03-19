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
import unittest
from typing import override

from autolatex2.config.configobj import Config
from autolatex2.make.maker import AutoLaTeXMaker
from autolatex2tests.cli.commands.abstract_command_test import AbstractCommandTest


class TestIndexAction(AbstractCommandTest):

	def __init__(self, x):
		super().__init__(x, 'index')

	@override
	def setUp(self):
		super().setUp()
		self._initialize_test_folder()

	def _initialize_test_folder(self):
		self._working_directory = os.getcwd()
		self._resource_directory = os.path.normpath(os.path.join(os.path.dirname(__file__),  '..', '..', 'dev-resources'))

		self._tmp_folder = self._create_temp_directory()
		self._tmp_folder_name = self._tmp_folder.name

		self._config = Config()
		self._config.document_directory = self._tmp_folder_name
		self._config.document_filename = 'rootfile.tex'
		self._config.translators.is_translator_enable = False

		self._tex_file = os.path.normpath(os.path.join(self._tmp_folder_name, 'rootfile.tex'))
		self._idx_file = os.path.normpath(os.path.join(self._tmp_folder_name, 'rootfile.idx'))
		self._ind_file = os.path.normpath(os.path.join(self._tmp_folder_name, 'rootfile.ind'))

		shutil.copyfile(os.path.normpath(os.path.join(self._resource_directory, 'test22.tex')),
						self._tex_file)



	@override
	def tearDown(self):
		super().tearDown()
		self._delete_temp_directory(self._tmp_folder)

	def test_wo_latex_compilation(self):
		with self.assertRaises(Exception):
			self.do_test(config=self._config)
		self.assertFalse(os.path.isfile(self._ind_file))

	def test_w_latex_compilation(self):
		maker = AutoLaTeXMaker.create(self._config)
		maker.run_latex(self._tex_file)
		self.assertTrue(os.path.isfile(self._idx_file))
		self.do_test(config=self._config)
		self.assertTrue(os.path.isfile(self._ind_file))


if __name__ == '__main__':
	unittest.main()

