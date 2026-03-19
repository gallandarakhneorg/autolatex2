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


class TestDvipsMaker(AbstractBaseTest):

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
		self.__dvi_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.dvi'))
		self.__ps_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.ps'))

		self.__config = Config()
		self.__config.document_directory = self.__tmp_folder_name
		self.__config.document_filename = 'rootfile.tex'
		self.__config.generation.pdf_mode = False

		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test3.tex')), self.__root_file)

		self.__maker = AutoLaTeXMaker.create(self.__config)
		os.chdir(self.__tmp_folder_name)
		self.__maker.run_latex(self.__root_file, loop=False)


	def ___printlogs(self):
		with open(os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.log'))) as file:
			print(file.read())


	def test_run_dvips_valid(self):
		self.assertTrue(os.path.isfile(self.__dvi_file))
		err = self.__maker.run_dvips(self.__dvi_file)
		#self.___printlogs()
		self.assertIsNone(err)
		self.assertTrue(os.path.isfile(self.__ps_file))


if __name__ == '__main__':
	unittest.main()

