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

from sortedcontainers import SortedSet

from autolatex2.config.configobj import Config
from autolatex2.make.filedescription import FileDescription
from autolatex2.make.maker import AutoLaTeXMaker
from autolatex2tests.abstract_base_test import AbstractBaseTest


class TestSimpleTeXDependenciesMaker(AbstractBaseTest):

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
		self.__bbl_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.bbl'))
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
					self.__ind_file,
					self.__root_file,
					self.__bbl_file
				]
			},
			self.__root_file: {
				"output_filename": self.__root_file,
				"input_filename": self.__root_file,
				"dependencies": [
					self.__texa_file,
					self.__texb_file,
				]
			},
			self.__texa_file: {
				"output_filename": self.__texa_file,
				"input_filename": self.__texa_file,
				"dependencies": [
				]
			},
			self.__texb_file: {
				"output_filename": self.__texb_file,
				"input_filename": self.__texb_file,
				"dependencies": [
				]
			},
			self.__bbl_file: {
				"output_filename": self.__bbl_file,
				"input_filename": self.__root_file,
				"dependencies": [
					self.__root_file,
					self.__bib_file
				]
			},
			self.__idx_file: {
				"output_filename": self.__idx_file,
				"input_filename": self.__root_file,
				"dependencies": [
					self.__root_file,
				]
			},
			self.__ind_file: {
				"output_filename": self.__ind_file,
				"input_filename": self.__idx_file,
				"dependencies": [
					self.__idx_file
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
		Compute dependencies from TeX sources and auxilliary files
		"""
		(pdf_file,  files) = self.__maker.compute_dependencies(self.__root_file, read_aux_file= True)
		self.assertEqual(self.__pdf_file, pdf_file)
		self.assertDependencies({
			self.__pdf_file: {
				"output_filename": self.__pdf_file,
				"input_filename": self.__root_file,
				"dependencies": [
					self.__gls_file,
					self.__ind_file,
					self.__root_file,
					self.__bbl_file
				]
			},
			self.__root_file: {
				"output_filename": self.__root_file,
				"input_filename": self.__root_file,
				"dependencies": [
					self.__texa_file,
					self.__texb_file,
				]
			},
			self.__texa_file: {
				"output_filename": self.__texa_file,
				"input_filename": self.__texa_file,
				"dependencies": [
				]
			},
			self.__texb_file: {
				"output_filename": self.__texb_file,
				"input_filename": self.__texb_file,
				"dependencies": [
				]
			},
			self.__bbl_file: {
				"output_filename": self.__bbl_file,
				"input_filename": self.__root_file,
				"dependencies": [
					self.__root_file,
					self.__bib_file
				]
			},
			self.__idx_file: {
				"output_filename": self.__idx_file,
				"input_filename": self.__root_file,
				"dependencies": [
					self.__root_file,
				]
			},
			self.__ind_file: {
				"output_filename": self.__ind_file,
				"input_filename": self.__idx_file,
				"dependencies": [
					self.__idx_file
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

