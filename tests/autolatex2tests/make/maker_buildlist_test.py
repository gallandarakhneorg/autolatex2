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
from unittest import skip

from sortedcontainers import SortedSet

from autolatex2.config.configobj import Config
from autolatex2.make.filedescription import FileDescription
from autolatex2.tex.utils import FileType
from autolatex2.make.maker import AutoLaTeXMaker
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestBuildListMaker(AbstractBaseTest):

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

	def __install_test_environment(self):
		self.__tmp_folder = self._create_temp_directory()
		self.__tmp_folder_name = self.__tmp_folder.name
		self.__root_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.tex'))
		self.__texa_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'test12a.tex'))
		self.__texb_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'test12b.tex'))
		self.__bib_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'test5.bib'))
		self.__bbl_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.bbl'))
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
		self.__reliable_touch(filename)
		self.__dependencies = None
		pdf_file,  self.__dependencies = self.__maker.compute_dependencies(self.__root_file, read_aux_file= False)

	def ensure_valid_change_dates(self):
		"""
		Ensure that all files have an increasing change dates.
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

	def __assertBuildingListItem(self, i : int, expected : dict, actual : FileDescription):
		self.assertEqual(expected['output_filename'], actual.output_filename, "Invalid output filename for actual #%d" % i)
		self.assertEqual(expected['input_filename'], actual.input_filename, "Invalid input filename for actual #%d" % i)
		self.assertEqual(expected['type'], actual.file_type, "Invalid file type for actual #%d" % i)
		self.assertEqual(self.__root_file, actual.main_filename, "Invalid main filename for actual #%d" % i)
		self.assertFalse(actual.use_biber, "Unexpected Biber usage for actual #%d" % i)
		self.assertFalse(actual.use_xindy, "Unexpected Xindy usage for actual #%d" % i)
		self.__assertDependencies(i, expected['dependencies'], actual.dependencies)

	# noinspection PyUnusedLocal
	def __assertDependencies(self, i : int, expected, actual):
		expected_deps = SortedSet()
		for d in expected:
			expected_deps.add(d)
		expected_deps = "\n".join(expected_deps)

		actual_deps = SortedSet()
		for d in actual:
			actual_deps.add(d)
		actual_deps = "\n".join(actual_deps)

		self.assertEqual(expected_deps, actual_deps, 'Invalid dependencies for actual #%d' % i)

	# noinspection PyMethodMayBeStatic
	def __index_of(self, expected : list, output_filename : str, input_filename : str, file_type : FileType) -> int:
		i = 0
		for element in expected:
			if isinstance(element, dict):
				if ('type' in element and element['type'] == file_type and
					'output_filename' in element and element['output_filename'] == output_filename and
					'input_filename' in element and element['input_filename'] == input_filename):
					return i
			i += 1
		return -1

	def assertBuildingList(self, expected : list[dict|list[dict]], actual : list):
		if not expected:
			self.assertFalse(actual, "Unexpected value for for actual. It is expected to be empty")
		else:
			i = 0
			j = 0
			candidate = expected[j]
			for actual_element in actual:
				if not candidate:
					j += 1
					candidate = expected[j]
				if isinstance(candidate, list):
					# Multiple candidates that may be found without a specific order
					idx = self.__index_of(candidate, actual_element.output_filename,
										  actual_element.input_filename, actual_element.file_type)
					if idx < 0 or idx >= len(candidate):
						self.fail('Expecting element %s' % repr(actual_element))
					else:
						found_candidate = candidate[idx]
						self.__assertBuildingListItem(i, dict(found_candidate), actual_element)
						del candidate[idx]
				else:
					# A specific item that must be next available
					self.__assertBuildingListItem(i, dict(candidate), actual_element)
				i += 1

	def test_fresh_w_force_changes(self):
		"""
		Build the build list from a fresh installation with --force
		"""
		build_list = self.__maker.build_internal_execution_list(self.__root_file, self.__pdf_file, self.__dependencies,
																force_changes=True)
		expected_list = [
			[
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
					"input_filename": self.__aux_file,
					"type": FileType.bbl,
					"dependencies": [
						self.__root_file,
						self.__bib_file
					]
				},
			],
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
		]
		self.assertBuildingList(expected_list, build_list)

	def test_fresh_wo_forcechanges_wo_stamp(self):
		"""
		Build the build list from a fresh installation and without --force ind.
		Because the stamps were not computed before, the stamp-based builds are needed (bibliography, index, glossary)
		"""
		build_list = self.__maker.build_internal_execution_list(self.__root_file, self.__pdf_file, self.__dependencies, force_changes=False)
		expected_list = list([
			[
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
					"input_filename": self.__aux_file,
					"type": FileType.bbl,
					"dependencies": [
						self.__root_file,
						self.__bib_file
					]
				}
			],
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
		expected_list = []
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
			[
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
					"input_filename": self.__aux_file,
					"type": FileType.bbl,
					"dependencies": [
						self.__root_file,
						self.__bib_file
					]
				}
			],
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



	def test_recent_bibfile(self):
		"""
		Build the build list from a fresh installation with a recent BibTeX file and without --force
		The stamps were read before running the test.
		"""
		self.force_touch(self.__bib_file)

		build_list = self.__maker.build_internal_execution_list(self.__root_file, self.__pdf_file, self.__dependencies,
																force_changes=False)
		expected_list = list([
			{
				"output_filename": self.__bbl_file,
				"input_filename": self.__aux_file,
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



if __name__ == '__main__':
	unittest.main()

