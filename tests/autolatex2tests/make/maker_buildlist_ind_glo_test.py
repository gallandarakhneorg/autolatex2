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
from autolatex2.tex.utils import FileType
from autolatex2.make.maker import AutoLaTeXMaker
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestBuildListIndexGlossaryMaker(AbstractBaseTest):
	"""
	Create a build list from a project with index and glossary.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__working_directory = os.getcwd()
		self.__resource_directory = os.path.normpath(os.path.join(str(os.path.dirname(__file__)), '..', 'dev-resources'))
		self.__install_test_environment()

	@override
	def tearDown(self):
		super().tearDown()
		os.chdir(self.__working_directory)
		self._delete_temp_directory(self.__tmp_folder)

	@property
	@override
	def root_file(self):
		return self.__root_file

	def __install_test_environment(self):
		self.__tmp_folder = self._create_temp_directory()
		self.__tmp_folder_name = self.__tmp_folder.name
		self.__root_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.tex'))
		self.__texa_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'test12a.tex'))
		self.__texb_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'test12b.tex'))
		self.__aux_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.aux'))
		self.__img_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'img.pdf'))
		self.__pdf_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.pdf'))
		self.__glo_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.glo'))
		self.__gls_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.gls'))
		self.__idx_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.idx'))
		self.__ind_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.ind'))

		self.__config = Config()
		self.__config.document_directory = self.__tmp_folder_name
		self.__config.document_filename = 'rootfile.tex'

		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test31.tex')), self.__root_file)
		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test12a.tex')), self.__texa_file)
		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test12b.tex')), self.__texb_file)
		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test12img.pdf')), self.__img_file)

		self.__maker = AutoLaTeXMaker.create(self.__config)
		os.chdir(self.__tmp_folder_name)
		pdf_file, self.__dependencies = self.__maker.compute_dependencies(self.__root_file, read_aux_file= False)

	def ensure_stamps(self):
		self.__maker.build_internal_execution_list(self.__root_file, self.__pdf_file, self.__dependencies)
		self.__maker.stamp_manager.write_build_stamps(self.__tmp_folder_name)
		self.__maker.stamp_manager.read_build_stamps(self.__tmp_folder_name)

	def reset_changes(self):
		for name, description in self.__dependencies.items():
			description.reset_change()

	def test_fresh_w_initial_latex(self):
		"""
		Build the build list from a fresh installation with --force
		"""
		build_list = self.__maker.build_internal_execution_list(self.__root_file, self.__pdf_file, self.__dependencies,
																enable_initial_latex_run=True)
		expected_list = [
			{
				"output_filename": self.__aux_file,
				"input_filename": self.__root_file,
				"type": FileType.aux,
			},
			[
				{
					"output_filename": self.__gls_file,
					"input_filename": self.__root_file,
					"type": FileType.gls,
				},
				{
					"output_filename": self.__ind_file,
					"input_filename": self.__idx_file,
					"type": FileType.ind,
				},
				{
					"output_filename": self.__idx_file,
					"input_filename": self.__root_file,
					"type": FileType.idx,
				},
			],
			{
				"output_filename": self.__pdf_file,
				"input_filename": self.__root_file,
				"type": FileType.pdf,
			}
		]
		self.assertBuildingList(expected_list, build_list)
		self.assertBuildingListOrder(build_list, FileType.idx, FileType.ind)


	def test_fresh_wo_initial_latex(self):
		"""
		Build the build list from a fresh installation with --force
		"""
		build_list = self.__maker.build_internal_execution_list(self.__root_file, self.__pdf_file, self.__dependencies,
																enable_initial_latex_run=False)
		expected_list = [
			[
				{
					"output_filename": self.__gls_file,
					"input_filename": self.__root_file,
					"type": FileType.gls,
				},
				{
					"output_filename": self.__ind_file,
					"input_filename": self.__idx_file,
					"type": FileType.ind,
				},
				{
					"output_filename": self.__idx_file,
					"input_filename": self.__root_file,
					"type": FileType.idx,
				},
			],
			{
				"output_filename": self.__pdf_file,
				"input_filename": self.__root_file,
				"type": FileType.pdf,
			}
		]
		self.assertBuildingList(expected_list, build_list)
		self.assertBuildingListOrder(build_list, FileType.idx, FileType.ind)



if __name__ == '__main__':
	unittest.main()

