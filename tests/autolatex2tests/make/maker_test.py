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
from collections.abc import Callable
from typing import override

from autolatex2.config.configobj import Config
from autolatex2.make.abstractbuilder import Builder
from autolatex2.make.maker import AutoLaTeXMaker
from autolatex2.tex.utils import FileType
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestMaker(AbstractBaseTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__config = Config()
		self.__config.document_directory = './tests/rootfolder'
		self.__config.document_filename = 'rootfile.tex'
		self.__maker = AutoLaTeXMaker.create(self.__config)

	def test_reset_commands(self):
		self.__maker.compiler_definition
		self.__maker.reset_commands()
		compiler = self.__maker.compiler_definition
		self.assertIsNotNone(compiler)
		self.assertEqual('pdflatex', compiler['cmd'])
		self.assertTrue(compiler['flags'])
		self.assertTrue(compiler['to_dvi'])
		self.assertFalse(compiler['to_ps'])
		self.assertTrue(compiler['to_pdf'])
		self.assertTrue(compiler['synctex'])
		self.assertTrue(compiler['jobname'])
		self.assertTrue(compiler['output_dir'])
		self.assertTrue(compiler['ewarnings'])
		self.assertFalse(compiler['utf8'])

	def test_compiler_definition(self):
		compiler = self.__maker.compiler_definition
		self.assertIsNotNone(compiler)
		self.assertEqual('pdflatex', compiler['cmd'])
		self.assertTrue(compiler['flags'])
		self.assertTrue(compiler['to_dvi'])
		self.assertFalse(compiler['to_ps'])
		self.assertTrue(compiler['to_pdf'])
		self.assertTrue(compiler['synctex'])
		self.assertTrue(compiler['jobname'])
		self.assertTrue(compiler['output_dir'])
		self.assertTrue(compiler['ewarnings'])
		self.assertFalse(compiler['utf8'])


	def test_extended_warnings_enabled(self):
		self.assertTrue(self.__maker.extended_warnings_enabled)


	def test_extended_warnings_code(self):
		self.assertNotEqual('', self.__maker.extended_warnings_code)


	def test_latex_cli(self):
		cli = self.__maker.latex_cli
		self.assertEqual(
			['pdflatex', '-halt-on-error', '-interaction', 'batchmode', '-file-line-error', '-output-format=pdf'],
			cli)


	def test_bibtex_cli(self):
		cli = self.__maker.bibtex_cli
		self.assertEqual(
			['bibtex'],
			cli)


	def test_biber_cli(self):
		cli = self.__maker.biber_cli
		self.assertEqual(
			['biber'],
			cli)


	def test_makeindex_cli(self):
		cli = self.__maker.makeindex_cli
		self.assertEqual(
			['makeindex'],
			cli)


	def test_texindy_cli(self):
		cli = self.__maker.texindy_cli
		self.assertEqual(
			['texindy', '-C', 'utf8'],
			cli)


	def test_makeglossaries_cli(self):
		cli = self.__maker.makeglossaries_cli
		self.assertEqual(
			['makeglossaries'],
			cli)


	def test_dvips_cli(self):
		cli = self.__maker.dvips_cli
		self.assertEqual(
			['dvips'],
			cli)


	def test_root_files(self):
		files = self.__maker.root_files
		self.assertEqual(
			{'./tests/rootfolder/rootfile.tex'},
			files)


	def test_add_root_file(self):
		self.__maker.add_root_file('./myfile.xyz')
		files = self.__maker.root_files
		self.assertEqual(
			{'./myfile.xyz', './tests/rootfolder/rootfile.tex'},
			files)


	def test_files(self):
		files = self.__maker.files
		self.assertEqual(
			{},
			files)


	def test_standard_warnings(self):
		warns = self.__maker.standard_warnings
		self.assertEqual(
			set(),
			warns)


	def test_extended_warnings(self):
		warns = self.__maker.extended_warnings
		self.assertEqual(
			list(),
			warns)

	def assertBuilder(self, builders : dict[FileType,Callable[[],Builder]], name : FileType):
		self.assertIn(name, builders)
		self.assertIsNotNone(builders[name])
		instance = builders[name]()
		self.assertIsNotNone(instance)

	def test_build_builder_dict(self):
		builders = self.__maker.build_builder_dict('autolatex2.make.builders')
		self.assertEqual(6, len(builders))
		self.assertBuilder(builders, FileType.aux)
		self.assertBuilder(builders, FileType.bbl)
		self.assertBuilder(builders, FileType.gls)
		self.assertBuilder(builders, FileType.idx)
		self.assertBuilder(builders, FileType.ind)
		self.assertBuilder(builders, FileType.pdf)


if __name__ == '__main__':
	unittest.main()

