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

from abc import ABC
import logging
import os
import shutil
from typing import override

from autolatex2.config.configobj import Config
from autolatex2.make.maker import AutoLaTeXMaker
from autolatex2tests.abstract_base_test import AbstractBaseTest


class AbstractTranslatorTest(AbstractBaseTest,ABC):

	def __init__(self, image_extension : str, target_extension : str, translator_name : str, excluded_translators : list[str], *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._image_extension = image_extension
		self._target_extension = target_extension
		self._translator_name = translator_name
		self._excluded_translators = excluded_translators

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		#logging.getLogger().setLevel(logging.DEBUG)
		self._working_directory = os.getcwd()
		self._resource_directory = os.path.normpath(os.path.join(os.path.dirname(__file__),  '..', 'dev-resources', 'translators'))
		self._translators_directory = os.path.normpath(os.path.join(os.path.dirname(__file__),  '..', '..', 'src', 'autolatex2', 'translators'))
		self._install_test_environment(self._image_extension, self._target_extension, self._translator_name, self._excluded_translators)

	@override
	def tearDown(self):
		super().tearDown()
		os.chdir(self._working_directory)
		self._delete_temp_directory(self._tmp_folder)

	def _makebasename(self, image_extension):
		if image_extension.startswith('+'):
			return 'testimg' + image_extension
		return 'testimg.' + image_extension

	def _install_test_environment(self, image_extension : str, target_extension : str, translator_name : str, excluded_translators : list[str]):
		self._tmp_folder = self._create_temp_directory()
		self._tmp_folder_name = self._tmp_folder.name
		self._img_folder = os.path.normpath(os.path.join(self._tmp_folder_name, 'imgs', 'auto'))

		self._img_srcfile = os.path.normpath(os.path.join(self._resource_directory, self._makebasename(image_extension)))
		self._img_file = os.path.normpath(os.path.join(self._img_folder, self._makebasename(image_extension)))
		
		self._img_out_file = os.path.normpath(os.path.join(self._img_folder, 'testimg.' + target_extension))

		self._config = Config()
		self._config.document_directory = self._tmp_folder_name
		self._config.document_filename = 'rootfile.tex'
		self._config.generation.pdf_mode = (target_extension == 'pdf' or target_extension == 'pdftex_t')
		self._config.translators.is_translator_enable = True
		self._config.translators.ignore_user_translators = True
		self._config.translators.ignore_document_translators = True
		self._config.translators.set_included(translator_name, None, True)
		for trans in excluded_translators:
			self._config.translators.set_included(trans, None, False)
		self._config.translators.add_image_to_convert(self._img_file)
		
		os.makedirs(self._img_folder)
		shutil.copyfile(self._img_srcfile, self._img_file)

		self._maker = AutoLaTeXMaker.create(self._config)
		os.chdir(self._tmp_folder_name)


	def _printlogs(self):
		with open(os.path.normpath(os.path.join(self._tmp_folder_name, 'rootfile.log'))) as file:
			print(file.read())


	def assertGeneratedFile(self, build_map : dict):
		if build_map[self._img_file] and os.path.isfile(build_map[self._img_file]):
			return
		if self._img_out_file and os.path.isfile(self._img_out_file):
			return
		if build_map[self._img_file] == self._img_out_file:
			self.fail("Generated image not found. Expecting: " + self._img_out_file)
		else:
			self.fail("Generated image not found. Expecting: " + build_map[self._img_file] + "\nor: " + self._img_out_file)

