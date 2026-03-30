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
import time
from pathlib import Path
from typing import override

from autolatex2.config.configobj import Config
from autolatex2.make.filedescription import FileDescription
from autolatex2.tex.utils import FileType
from autolatex2.make.maker import AutoLaTeXMaker
from autolatex2tests.abstract_base_test import AbstractBaseTest
import autolatex2.utils.utilfunctions as genutils

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

		self.ensure_valid_change_dates()

		self.__maker = AutoLaTeXMaker.create(self.__config)
		os.chdir(self.__tmp_folder_name)
		pdf_file, self.__dependencies = self.__maker.compute_dependencies(self.__root_file, read_aux_file= False)

	# noinspection PyMethodMayBeStatic
	def __reliable_touch(self, filepath : str) -> bool:
		"""
        Reliable touch that ensures timestamps are updated even on operating systems that have no real support for mtime.
        """
		path = Path(filepath)
		path.touch(exist_ok=True)
		# Force timestamp update even on 'noatime' filesystems
		# by doing a small write operation
		with open(path, 'rb+') as f:
			f.seek(0)
			# Rewrite same content
			f.write(f.read())
		return True

	def force_touch(self, filename : str):
		self.ensure_stamps()
		self.ensure_valid_change_dates()
		self.__reliable_touch(self.__pdf_file)
		time.sleep(0.5)
		self.__reliable_touch(self.__root_file)
		self.__dependencies = None
		pdf_file,  self.__dependencies = self.__maker.compute_dependencies(self.__root_file, read_aux_file= False)

	def ensure_valid_change_dates(self):
		"""
		Ensure that all files have a increasing change dates.
		"""
		self.__reliable_touch(self.__texa_file)
		self.__reliable_touch(self.__texb_file)
		self.__reliable_touch(self.__img_file)
		self.__reliable_touch(self.__root_file)
		self.__reliable_touch(self.__bib_file)
		self.__reliable_touch(self.__bbl_file)
		self.__reliable_touch(self.__glo_file)
		self.__reliable_touch(self.__gls_file)
		self.__reliable_touch(self.__idx_file)
		self.__reliable_touch(self.__ind_file)
		self.__reliable_touch(self.__aux_file)
		self.__reliable_touch(self.__pdf_file)

	def ensure_stamps(self):
		self.__maker.build_internal_execution_list(self.__root_file, self.__pdf_file, self.__dependencies, force_changes=False)
		self.__maker.write_build_stamps(self.__tmp_folder_name)
		self.__maker.read_build_stamps(self.__tmp_folder_name)

	def __assertBuildingList(self, index : int, expected : dict, actual : FileDescription):
		self.assertEqual(expected['output_filename'], actual.output_filename)
		self.assertEqual(expected['input_filename'], actual.input_filename)
		self.assertEqual(expected['type'], actual.file_type)
		self.assertEqual(self.__root_file, actual.main_filename)
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
				actual_item = actual[i]
				self.__assertBuildingList(i, expectedItem, actual_item)
				i = i + 1


	def test_fresh_w_force_changes(self):
		"""
		Build the build list from a fresh installation with --force
		"""
		build_list = self.__maker.build_internal_execution_list(self.__root_file, self.__pdf_file, self.__dependencies,
																force_changes=True)
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
					self.__bbl_file
				]
			}
		])
		self.assertBuildingList(expected_list, build_list)

	def test_fresh_wo_forcechanges_wo_stamp(self):
		"""
		Build the build list from a fresh installation and without --force ind.
		Because the stamps were not computed before, the stamp-based builds are needed (bibliography, index, glossary)
		"""
		build_list = self.__maker.build_internal_execution_list(self.__root_file, self.__pdf_file, self.__dependencies, force_changes=False)
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
					self.__bbl_file
				]
			}
		])
		self.assertBuildingList(expected_list, build_list)

	def test_fresh_wo_forcechanges_w_stamp(self):
		"""
		Build the build list from a fresh installation and without --force ind.
		The stamps were read before running the test.
		"""
		self.ensure_stamps()
		build_list = self.__maker.build_internal_execution_list(self.__root_file, self.__pdf_file, self.__dependencies, force_changes=False)
		expected_list = list([])
		self.assertBuildingList(expected_list, build_list)


	def test_recent_root_texfile(self):
		"""
		Build the build list from a fresh installation with a recent TeX root file and without --force
		The stamps were read before running the test.
		"""
		self.force_touch(self.__root_file)

		build_list = self.__maker.build_internal_execution_list(self.__root_file, self.__pdf_file, self.__dependencies,
																force_changes=False)
		expected_list = list([
			{
				"output_filename": self.__idx_file,
				"input_filename": self.__root_file,
				"type": FileType.idx,
				"dependencies": [
					self.__root_file
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
					self.__bbl_file
				]
			}

		])
		self.assertBuildingList(expected_list, build_list)

	# def test_recent_bibfile(self):
	# 	"""
	# 	Build the build list from a fresh installation with a recent bibtex file and without --force
	# 	"""
	# 	self.fail("To-Do")
	# 	time.sleep(0.5)
	# 	Path(self.__bib_file).touch(exist_ok=True)
	#
	# 	build_list = self.__maker.build_internal_execution_list(self.__root_file, self.__pdf_file, self.__dependencies,
	# 															force_changes=False)
	# 	expected_list = list([
	# 		{
	# 			"output_filename": self.__idx_file,
	# 			"input_filename": self.__root_file,
	# 			"type": FileType.idx,
	# 			"dependencies": [
	# 				self.__root_file
	# 			]
	# 		},
	# 		{
	# 			"output_filename": self.__ind_file,
	# 			"input_filename": self.__idx_file,
	# 			"type": FileType.ind,
	# 			"dependencies": [
	# 				self.__idx_file
	# 			]
	# 		},
	# 		{
	# 			"output_filename": self.__bbl_file,
	# 			"input_filename": self.__root_file,
	# 			"type": FileType.bbl,
	# 			"dependencies": [
	# 				self.__root_file,
	# 				self.__bib_file
	# 			]
	# 		},
	# 		{
	# 			"output_filename": self.__pdf_file,
	# 			"input_filename": self.__root_file,
	# 			"type": FileType.pdf,
	# 			"dependencies": [
	# 				self.__gls_file,
	# 				self.__ind_file,
	# 				self.__root_file,
	# 				self.__bbl_file
	# 			]
	# 		}
	#
	# 	])
	# 	self.assertBuildingList(expected_list, build_list)




if __name__ == '__main__':
	unittest.main()

