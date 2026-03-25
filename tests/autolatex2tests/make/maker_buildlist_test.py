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
import json

from autolatex2.config.configobj import Config
from autolatex2.make.filedescription import FileDescription
from autolatex2.make.make_enums import FileType
from autolatex2.make.maker import AutoLaTeXMaker
from autolatex2tests.abstract_base_test import AbstractBaseTest
from autolatex2.utils.i18n import T


class TestBuildListMaker(AbstractBaseTest):

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
		self.__texa_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'test12a.tex'))
		self.__texb_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'test12b.tex'))
		self.__bib_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'test5.bib'))
		self.__bbl_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'test5.bbl'))
		self.__aux_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.aux'))
		self.__img_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'test12img.pdf'))
		self.__pdf_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.pdf'))
		self.__glo_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.glo'))
		self.__gls_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.gls'))
		self.__idx_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.idx'))
		self.__ind_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.ind'))

		self.__config = Config()
		self.__config.document_directory = self.__tmp_folder_name
		self.__config.document_filename = 'rootfile.tex'

		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test12.tex')), self.__root_file)
		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test12a.tex')), self.__texa_file)
		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test12b.tex')), self.__texb_file)
		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test5.bib')), self.__bib_file)
		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test12img.pdf')), self.__img_file)

		self.__maker = AutoLaTeXMaker.create(self.__config)
		os.chdir(self.__tmp_folder_name)
		pdf_file,  self.__dependencies = self.__maker.compute_dependencies(self.__root_file, read_aux_file= False)


	def ___printlogs(self):
		with open(os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.log'))) as file:
			print(file.read())

	def __assertBuildingList(self, index : int, expected : dict, actual : FileDescription):
		self.assertEqual(expected['output_filename'], actual.output_filename)
		self.assertEqual(expected['input_filename'], actual.input_filename)
		self.assertEqual(expected['type'], actual.file_type)
		self.assertEqual(self.__root_file, actual.main_filename)
		self.assertIsNone(actual.change)
		self.assertFalse(actual.use_biber)
		self.assertFalse(actual.use_xindy)
		self.assertEqual(set(expected['dependencies']), set(actual.dependencies))

	def assertBuildingList(self, expected : list, actual : list):
		expectedlen = len(expected)
		actuallen = len(actual)
		if expectedlen != actuallen:
			self.fail("Not same number of elements, %i are expected, %i are provided" % (expectedlen, actuallen))
		else:
			i = 0
			for expectedItem in expected:
				actualItem = actual[i]
				self.__assertBuildingList(i, expectedItem, actualItem)
				i = i + 1




	def test_compute_build_internal_execution_list_wo_forceChanges(self):
		build_list = self.__maker.build_internal_execution_list(self.__root_file, self.__pdf_file, self.__dependencies, force_changes= False)
		#self.___printlogs()
		expected_list = list([
				{
					"output_filename": self.__gls_file,
					"input_filename": self.__root_file,
					"type": FileType.gls,
					"dependencies": [
						self.__glo_file
					]
				},
				{
					"output_filename": self.__ind_file,
					"input_filename": self.__idx_file,
					"type": FileType.ind,
					"dependencies": [
						self.__idx_file
					]
				},
				{
					"output_filename": self.__bbl_file,
					"input_filename": self.__root_file,
					"type": FileType.bbl,
					"dependencies": [
						self.__root_file,
						self.__bib_file
					]
				},
				{
					"output_filename": self.__pdf_file,
					"input_filename": self.__root_file,
					"type": FileType.pdf,
					"dependencies": [
						self.__gls_file,
						self.__ind_file,
						self.__root_file,
						self.__texa_file,
						self.__texb_file,
						self.__bbl_file
					]
				}
		
			])
		self.assertBuildingList(expected_list, build_list)



	def test_compute_build_internal_execution_list_w_force_changes(self):
		build_list = self.__maker.build_internal_execution_list(self.__root_file, self.__pdf_file, self.__dependencies, force_changes= True)
		#self.___printlogs()
		expected_list = list([
				{
					"output_filename": self.__gls_file,
					"input_filename": self.__root_file,
					"type": FileType.gls,
					"dependencies": [
						self.__glo_file
					]
				},
				{
					"output_filename": self.__ind_file,
					"input_filename": self.__idx_file,
					"type": FileType.ind,
					"dependencies": [
						self.__idx_file
					]
				},
				{
					"output_filename": self.__bbl_file,
					"input_filename": self.__root_file,
					"type": FileType.bbl,
					"dependencies": [
						self.__root_file,
						self.__bib_file
					]
				},
				{
					"output_filename": self.__pdf_file,
					"input_filename": self.__root_file,
					"type": FileType.pdf,
					"dependencies": [
						self.__gls_file,
						self.__ind_file,
						self.__root_file,
						self.__texa_file,
						self.__texb_file,
						self.__bbl_file
					]
				}
		
			])
		self.assertBuildingList(expected_list, build_list)


if __name__ == '__main__':
	unittest.main()

