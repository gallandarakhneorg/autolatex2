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
from unittest import skip

from sortedcontainers import SortedSet

from autolatex2.config.configobj import Config
from autolatex2.make.filedescription import FileDescription
from autolatex2.make.maker import AutoLaTeXMaker
from autolatex2tests.abstract_base_test import AbstractBaseTest


class TestBibunitsDependenciesMaker(AbstractBaseTest):

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
		self.__bib_a_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.bib'))
		self.__bib_b_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'secondbib.bib'))
		self.__bbl_a_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'bu1.bbl'))
		self.__bbl_b_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'bu2.bbl'))
		self.__aux_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.aux'))
		self.__aux_a_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'bu1.aux'))
		self.__aux_b_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'bu2.aux'))
		self.__img_a_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'img1.pdf'))
		self.__img_b_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'img2.pdf'))
		self.__pdf_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.pdf'))
		self.__glo_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.glo'))
		self.__gls_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.gls'))

		self.__config = Config()
		self.__config.document_directory = self.__tmp_folder_name
		self.__config.document_filename = 'rootfile.tex'

		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test26.tex')), self.__root_file)
		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test26.bib')), self.__bib_a_file)
		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test26.bib')), self.__bib_b_file)
		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test12img.pdf')), self.__img_a_file)
		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test12img.pdf')), self.__img_b_file)

		self.__maker = AutoLaTeXMaker.create(self.__config)
		os.chdir(self.__tmp_folder_name)

	# noinspection PyUnusedLocal
	def __assertDependencies(self, name : str, expected : dict, actual : FileDescription):
		self.assertEqual(expected['output_filename'], actual.output_filename, 'Invalid output files for %s' % name)
		self.assertEqual(expected['input_filename'], actual.input_filename, 'Invalid input files for %s' % name)

		expected_deps = SortedSet()
		for d in expected['dependencies']:
			expected_deps.add(d)
		expected_deps = "\n".join(expected_deps)

		actual_deps = SortedSet()
		for d in actual.dependencies:
			actual_deps.add(d)
		actual_deps = "\n".join(actual_deps)

		self.assertEqual(expected_deps, actual_deps, 'Invalid dependencies for %s' % name)

	def assertDependencies(self, expected : dict, actual : dict):
		for fn, expectedItem in expected.copy().items():
			if fn in actual:
				del expected[fn]
				actual_item = actual[fn]
				self.__assertDependencies(fn, expectedItem, actual_item)
			else:
				self.fail('Unexpected dependency file: ' + fn) 
		self.assertEqual(0, len(expected))


	def test_compute_dependencies_wo_aux(self):
		"""
		Compute dependencies only from TeX sources
		"""
		(pdf_file,  files) = self.__maker.compute_dependencies(self.__root_file, read_aux_file= False)
		self.assertEqual(self.__pdf_file, pdf_file)
		self.assertDependencies({
			self.__pdf_file: {
				"output_filename": self.__pdf_file,
				"input_filename": self.__root_file,
				"dependencies": [
					self.__gls_file,
					self.__root_file,
					self.__bbl_a_file,
					self.__bbl_b_file
				]
			},
			self.__root_file: {
				"output_filename": self.__root_file,
				"input_filename": self.__root_file,
				"dependencies": [
				]
			},
			self.__bbl_a_file: {
				"output_filename": self.__bbl_a_file,
				"input_filename": self.__aux_a_file,
				"dependencies": [
					self.__root_file,
					self.__bib_a_file
				]
			},
			self.__bbl_b_file: {
				"output_filename": self.__bbl_b_file,
				"input_filename": self.__aux_b_file,
				"dependencies": [
					self.__root_file,
					self.__bib_b_file
				]
			},
			self.__glo_file: {
				"output_filename": self.__glo_file,
				"input_filename": self.__root_file,
				"dependencies": [
					self.__root_file,
				]
			},
			self.__gls_file: {
				"output_filename": self.__gls_file,
				"input_filename": self.__root_file,
				"dependencies": [
					self.__glo_file
				]
			}
		}, files)

	def test_compute_dependencies_w_aux(self):
		"""
		Compute dependencies from TeX sources and auxiliary files
		"""
		(pdf_file,  files) = self.__maker.compute_dependencies(self.__root_file, read_aux_file= True)
		self.assertEqual(self.__pdf_file, pdf_file)
		self.assertDependencies({
			self.__pdf_file: {
				"output_filename": self.__pdf_file,
				"input_filename": self.__root_file,
				"dependencies": [
					self.__gls_file,
					self.__root_file,
					self.__bbl_a_file,
					self.__bbl_b_file
				]
			},
			self.__root_file: {
				"output_filename": self.__root_file,
				"input_filename": self.__root_file,
				"dependencies": [
				]
			},
			self.__bbl_a_file: {
				"output_filename": self.__bbl_a_file,
				"input_filename": self.__aux_a_file,
				"dependencies": [
					self.__root_file,
					self.__bib_a_file
				]
			},
			self.__bbl_b_file: {
				"output_filename": self.__bbl_b_file,
				"input_filename": self.__aux_b_file,
				"dependencies": [
					self.__root_file,
					self.__bib_b_file
				]
			},
			self.__glo_file: {
				"output_filename": self.__glo_file,
				"input_filename": self.__root_file,
				"dependencies": [
					self.__root_file,
				]
			},
			self.__gls_file: {
				"output_filename": self.__gls_file,
				"input_filename": self.__root_file,
				"dependencies": [
					self.__glo_file
				]
			}
		}, files)


if __name__ == '__main__':
	unittest.main()

