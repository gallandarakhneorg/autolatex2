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

import logging
import os
import unittest
from typing import override

from autolatex2.cli.abstract_main import AbstractAutoLaTeXMain
from autolatex2.translator.translatorobj import TranslatorLevel
from autolatex2.utils.extlogging import LogLevel
import autolatex2.utils.extprint as eprintpkg
from autolatex2tests.abstract_base_test import AbstractBaseTest


class TestAbstractMain(AbstractBaseTest):

	class InternalMainMock(AbstractAutoLaTeXMain):
		def __init__(self):
			super().__init__()

		@override
		def _run_program(self, positional_arguments: list[str], unknown_arguments: list[str]):
			raise NotImplementedError



	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__resource_directory = os.path.normpath(os.path.join(os.path.dirname(__file__),  '..', 'dev-resources'))
		self.__translator_resource_directory = os.path.normpath(os.path.join(self.__resource_directory,  'translators'))
		self.__resource_file = os.path.normpath(os.path.join(self.__resource_directory,  'test1.tex'))
		self.__ist_file = os.path.normpath(os.path.join(os.path.dirname(__file__),  '..', '..', '..', 'src', 'autolatex2', 'default.ist'))
		self.__sty_file = os.path.normpath(os.path.join(os.path.dirname(__file__),  '..', '..', '..', 'src', 'autolatex2', 'tex', 'autolatex.sty'))
		self.__obj = TestAbstractMain.InternalMainMock()

	def test_get_system_sty_file(self):
		self.assertEqual(self.__sty_file, self.__obj.configuration.get_system_sty_file())

	def test_directory(self):
		self.assertIsNone(self.__obj.configuration.document_directory)
		self.assertIsNone(self.__obj.configuration.document_filename)
		
		self.__obj._add_standard_cli_options_path()
		self.__obj.cli_parser.parse_known_args(['--directory', self.__resource_directory])
		
		self.assertEqual(self.__resource_directory, self.__obj.configuration.document_directory)
		self.assertIsNone(self.__obj.configuration.document_filename)

	def test_file(self):
		self.assertIsNone(self.__obj.configuration.document_directory)
		self.assertIsNone(self.__obj.configuration.document_filename)
		
		self.__obj._add_standard_cli_options_path()
		self.__obj.cli_parser.parse_known_args(['--file', self.__resource_file])
		
		self.assertEqual(self.__resource_directory, self.__obj.configuration.document_directory)
		self.assertEqual('test1.tex', self.__obj.configuration.document_filename)

	def test_search_project_from(self):
		self.assertIsNone(self.__obj.configuration.document_directory)
		self.assertIsNone(self.__obj.configuration.document_filename)
		
		self.__obj._add_standard_cli_options_path()
		self.__obj.cli_parser.parse_known_args(['--search-project-from', self.__resource_file])
		
		self.assertIsNone(self.__obj.configuration.document_directory)
		self.assertIsNone(self.__obj.configuration.document_filename)

	def test_pdf(self):
		self.assertTrue(self.__obj.configuration.generation.pdf_mode)
		self.__obj.configuration.generation.pdf_mode = False
		self.assertFalse(self.__obj.configuration.generation.pdf_mode)
		
		self.__obj._add_standard_cli_options_output()
		self.__obj.cli_parser.parse_known_args(['--pdf'])
		
		self.assertTrue(self.__obj.configuration.generation.pdf_mode)

	def test_dvi(self):
		self.assertTrue(self.__obj.configuration.generation.pdf_mode)
		
		self.__obj._add_standard_cli_options_output()
		self.__obj.cli_parser.parse_known_args(['--dvi'])
		
		self.assertFalse(self.__obj.configuration.generation.pdf_mode)

	def test_ps(self):
		self.assertTrue(self.__obj.configuration.generation.pdf_mode)
		
		self.__obj._add_standard_cli_options_output()
		self.__obj.cli_parser.parse_known_args(['--ps'])
		
		self.assertFalse(self.__obj.configuration.generation.pdf_mode)

	def test_stdout(self):
		eprintpkg.IS_STANDARD_OUTPUT = False
		self.assertFalse(eprintpkg.IS_STANDARD_OUTPUT)
		
		self.__obj._add_standard_cli_options_output()
		self.__obj.cli_parser.parse_known_args(['--stdout'])
		
		self.assertTrue(eprintpkg.IS_STANDARD_OUTPUT)

	def test_stderr(self):
		eprintpkg.IS_STANDARD_OUTPUT = True
		self.assertTrue(eprintpkg.IS_STANDARD_OUTPUT)
		
		self.__obj._add_standard_cli_options_output()
		self.__obj.cli_parser.parse_known_args(['--stderr'])
		
		self.assertFalse(eprintpkg.IS_STANDARD_OUTPUT)

	def test_pdflatex(self):
		self.__obj.configuration.generation.latex_compiler = 'xyz'
		self.assertEqual('xyz', self.__obj.configuration.generation.latex_compiler)
		
		self.__obj._add_standard_cli_options_tex()
		self.__obj.cli_parser.parse_known_args(['--pdflatex'])
		
		self.assertEqual('pdflatex', self.__obj.configuration.generation.latex_compiler)

	def test_latex(self):
		self.__obj.configuration.generation.latex_compiler = 'xyz'
		self.assertEqual('xyz', self.__obj.configuration.generation.latex_compiler)
		
		self.__obj._add_standard_cli_options_tex()
		self.__obj.cli_parser.parse_known_args(['--latex'])
		
		self.assertEqual('latex', self.__obj.configuration.generation.latex_compiler)

	def test_lualatex(self):
		self.__obj.configuration.generation.latex_compiler = 'xyz'
		self.assertEqual('xyz', self.__obj.configuration.generation.latex_compiler)
		
		self.__obj._add_standard_cli_options_tex()
		self.__obj.cli_parser.parse_known_args(['--lualatex'])
		
		self.assertEqual('lualatex', self.__obj.configuration.generation.latex_compiler)

	def test_xelatex(self):
		self.__obj.configuration.generation.latex_compiler = 'xyz'
		self.assertEqual('xyz', self.__obj.configuration.generation.latex_compiler)
		
		self.__obj._add_standard_cli_options_tex()
		self.__obj.cli_parser.parse_known_args(['--xelatex'])
		
		self.assertEqual('xelatex', self.__obj.configuration.generation.latex_compiler)

	def test_synctex(self):
		self.__obj.configuration.generation.synctex = False
		self.assertFalse(self.__obj.configuration.generation.synctex)
		
		self.__obj._add_standard_cli_options_tex()
		self.__obj.cli_parser.parse_known_args(['--synctex'])
		
		self.assertTrue(self.__obj.configuration.generation.synctex)

	def test_nosynctex(self):
		self.__obj.configuration.generation.synctex = True
		self.assertTrue(self.__obj.configuration.generation.synctex)
		
		self.__obj._add_standard_cli_options_tex()
		self.__obj.cli_parser.parse_known_args(['--nosynctex'])
		
		self.assertFalse(self.__obj.configuration.generation.synctex)

	def test_auto(self):
		self.__obj.configuration.translators.is_translator_enable = False
		self.assertFalse(self.__obj.configuration.translators.is_translator_enable)
		
		self.__obj._add_standard_cli_options_translator()
		self.__obj.cli_parser.parse_known_args(['--auto'])
		
		self.assertTrue(self.__obj.configuration.translators.is_translator_enable)

	def test_noauto(self):
		self.__obj.configuration.translators.is_translator_enable = True
		self.assertTrue(self.__obj.configuration.translators.is_translator_enable)
		
		self.__obj._add_standard_cli_options_translator()
		self.__obj.cli_parser.parse_known_args(['--noauto'])
		
		self.assertFalse(self.__obj.configuration.translators.is_translator_enable)

	def test_exclude_specified(self):
		self.__obj.configuration.translators.set_included('svg2pdf_inkscape', TranslatorLevel.DOCUMENT, True)
		self.__obj.configuration.translators.set_included('svg2pdf_inkscape', TranslatorLevel.USER, False)
		self.__obj.configuration.translators.set_included('svg2pdf_inkscape', TranslatorLevel.SYSTEM, False)
		
		self.__obj._add_standard_cli_options_translator()
		self.__obj.cli_parser.parse_known_args(['--exclude', 'svg2pdf_inkscape'])
		
		self.assertEqual(TranslatorLevel.NEVER, self.__obj.configuration.translators.inclusion_level('svg2pdf_inkscape'))

	def test_exclude_notspecified(self):
		self.__obj.configuration.translators.set_included('svg2pdf_inkscape', TranslatorLevel.DOCUMENT, True)
		self.__obj.configuration.translators.set_included('svg2pdf_inkscape', TranslatorLevel.USER, None)
		self.__obj.configuration.translators.set_included('svg2pdf_inkscape', TranslatorLevel.SYSTEM, None)
		
		self.__obj._add_standard_cli_options_translator()
		self.__obj.cli_parser.parse_known_args(['--exclude', 'svg2pdf_inkscape'])
		
		self.assertEqual(TranslatorLevel.NEVER, self.__obj.configuration.translators.inclusion_level('svg2pdf_inkscape'))

	def test_include(self):
		self.__obj.configuration.translators.set_included('svg2pdf_inkscape', TranslatorLevel.DOCUMENT, False)
		self.__obj.configuration.translators.set_included('svg2pdf_inkscape', TranslatorLevel.USER, False)
		self.__obj.configuration.translators.set_included('svg2pdf_inkscape', TranslatorLevel.SYSTEM, False)
		self.assertEqual(TranslatorLevel.NEVER, self.__obj.configuration.translators.inclusion_level('svg2pdf_inkscape'))
		
		self.__obj._add_standard_cli_options_translator()
		self.__obj.cli_parser.parse_known_args(['--include', 'svg2pdf_inkscape'])
		
		self.assertEqual(TranslatorLevel.DOCUMENT, self.__obj.configuration.translators.inclusion_level('svg2pdf_inkscape'))

	def test_include_path(self):
		self.__obj.configuration.translators.include_paths = None
		self.assertEqual(list(), self.__obj.configuration.translators.include_paths)
		
		self.__obj._add_standard_cli_options_translator()
		self.__obj.cli_parser.parse_known_args(['--include-path', self.__translator_resource_directory + os.path.pathsep + self.__resource_directory])
		
		self.assertEqual([self.__translator_resource_directory, self.__resource_directory], self.__obj.configuration.translators.include_paths)

	def test_imgdirectory(self):
		self.__obj.configuration.translators.image_paths = None
		self.assertEqual(list(), self.__obj.configuration.translators.image_paths)
		
		self.__obj._add_standard_cli_options_translator()
		self.__obj.cli_parser.parse_known_args(['--imgdirectory', self.__translator_resource_directory + os.path.pathsep + self.__resource_directory])
		
		self.assertEqual([self.__translator_resource_directory, self.__resource_directory], self.__obj.configuration.translators.image_paths)

	def test_biblio(self):
		self.__obj.configuration.generation.is_biblio_enable = False
		self.assertFalse(self.__obj.configuration.generation.is_biblio_enable)
		
		self.__obj._add_standard_cli_options_biblio()
		self.__obj.cli_parser.parse_known_args(['--biblio'])
		
		self.assertTrue(self.__obj.configuration.generation.is_biblio_enable)

	def test_nobiblio(self):
		self.__obj.configuration.generation.is_biblio_enable = True
		self.assertTrue(self.__obj.configuration.generation.is_biblio_enable)
		
		self.__obj._add_standard_cli_options_biblio()
		self.__obj.cli_parser.parse_known_args(['--nobiblio'])
		
		self.assertFalse(self.__obj.configuration.generation.is_biblio_enable)

	def test_defaultist(self):
		self.assertEqual(self.__ist_file, self.__obj.configuration.get_system_ist_file())
		self.__obj.configuration.generation.makeindex_style_filename = 'xyz'
		self.assertEqual('xyz', self.__obj.configuration.generation.makeindex_style_filename)
		
		self.__obj._add_standard_cli_options_index()
		self.__obj.cli_parser.parse_known_args(['--defaultist'])
		
		self.assertEqual(self.__ist_file, self.__obj.configuration.generation.makeindex_style_filename)

	def test_index(self):
		self.__obj.configuration.generation.is_index_enable = False
		self.assertFalse(self.__obj.configuration.generation.is_index_enable)
		self.assertEqual(self.__ist_file, self.__obj.configuration.get_system_ist_file())
		self.__obj.configuration.generation.makeindex_style_filename = 'xyz'
		self.assertEqual('xyz', self.__obj.configuration.generation.makeindex_style_filename)
		
		self.__obj._add_standard_cli_options_index()
		self.__obj.cli_parser.parse_known_args(['--index', self.__resource_file])
		
		self.assertTrue(self.__obj.configuration.generation.is_index_enable)
		self.assertEqual(self.__resource_file, self.__obj.configuration.generation.makeindex_style_filename)

	def test_noindex(self):
		self.__obj.configuration.generation.is_index_enable = True
		self.assertTrue(self.__obj.configuration.generation.is_index_enable)
		
		self.__obj._add_standard_cli_options_index()
		self.__obj.cli_parser.parse_known_args(['--noindex'])
		
		self.assertFalse(self.__obj.configuration.generation.is_index_enable)

	def test_glossary(self):
		self.__obj.configuration.generation.is_glossary_enable = False
		self.assertFalse(self.__obj.configuration.generation.is_glossary_enable)
		
		self.__obj._add_standard_cli_options_glossary()
		self.__obj.cli_parser.parse_known_args(['--glossary'])
		
		self.assertTrue(self.__obj.configuration.generation.is_glossary_enable)

	def test_gloss(self):
		self.__obj.configuration.generation.is_glossary_enable = False
		self.assertFalse(self.__obj.configuration.generation.is_glossary_enable)
		
		self.__obj._add_standard_cli_options_glossary()
		self.__obj.cli_parser.parse_known_args(['--gloss'])
		
		self.assertTrue(self.__obj.configuration.generation.is_glossary_enable)

	def test_noglossary(self):
		self.__obj.configuration.generation.is_glossary_enable = True
		self.assertTrue(self.__obj.configuration.generation.is_glossary_enable)
		
		self.__obj._add_standard_cli_options_glossary()
		self.__obj.cli_parser.parse_known_args(['--noglossary'])
		
		self.assertFalse(self.__obj.configuration.generation.is_glossary_enable)

	def test_nogloss(self):
		self.__obj.configuration.generation.is_glossary_enable = True
		self.assertTrue(self.__obj.configuration.generation.is_glossary_enable)
		
		self.__obj._add_standard_cli_options_glossary()
		self.__obj.cli_parser.parse_known_args(['--nogloss'])
		
		self.assertFalse(self.__obj.configuration.generation.is_glossary_enable)

	def test_file_line_warning(self):
		self.__obj.configuration.generation.extended_warnings = False
		self.assertFalse(self.__obj.configuration.generation.extended_warnings)
		
		self.__obj._add_standard_cli_options_warning()
		self.__obj.cli_parser.parse_known_args(['--file-line-warning'])
		
		self.assertTrue(self.__obj.configuration.generation.extended_warnings)


	def test_nofile_line_warning(self):
		self.__obj.configuration.generation.extended_warnings = True
		self.assertTrue(self.__obj.configuration.generation.extended_warnings)
		
		self.__obj._add_standard_cli_options_warning()
		self.__obj.cli_parser.parse_known_args(['--nofile-line-warning'])
		
		self.assertFalse(self.__obj.configuration.generation.extended_warnings)

	def test_debug(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.assertEqual(logging.CRITICAL, logging.getLogger().level)
		
		self.__obj._add_standard_cli_options_logging()
		self.__obj.cli_parser.parse_known_args(['--debug'])
		
		self.assertEqual(LogLevel.DEBUG, logging.getLogger().level)

	def test_quiet(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.assertEqual(logging.CRITICAL, logging.getLogger().level)
		
		self.__obj._add_standard_cli_options_logging()
		self.__obj.cli_parser.parse_known_args(['--quiet'])
		
		self.assertEqual(LogLevel.ERROR, logging.getLogger().level)

	def test_silent(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.assertEqual(logging.CRITICAL, logging.getLogger().level)
		
		self.__obj._add_standard_cli_options_logging()
		self.__obj.cli_parser.parse_known_args(['--silent'])
		
		self.assertEqual(LogLevel.OFF, logging.getLogger().level)

	def test_verbose_1(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.assertEqual(logging.CRITICAL, logging.getLogger().level)
		
		self.__obj._add_standard_cli_options_logging()
		self.__obj.cli_parser.parse_known_args(['--verbose'])
		
		self.assertEqual(LogLevel.ERROR, logging.getLogger().level)

	def test_verbose_2(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.assertEqual(logging.CRITICAL, logging.getLogger().level)
		
		self.__obj._add_standard_cli_options_logging()
		self.__obj.cli_parser.parse_known_args(['--verbose', '--verbose'])
		
		self.assertEqual(LogLevel.WARNING, logging.getLogger().level)

	def test_verbose_3(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.assertEqual(logging.CRITICAL, logging.getLogger().level)
		
		self.__obj._add_standard_cli_options_logging()
		self.__obj.cli_parser.parse_known_args(['--verbose', '--verbose', '--verbose'])
		
		self.assertEqual(LogLevel.FINE_WARNING, logging.getLogger().level)

	def test_verbose_4(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.assertEqual(logging.CRITICAL, logging.getLogger().level)
		
		self.__obj._add_standard_cli_options_logging()
		self.__obj.cli_parser.parse_known_args(['--verbose', '--verbose', '--verbose', '--verbose'])
		
		self.assertEqual(LogLevel.INFO, logging.getLogger().level)

	def test_verbose_5(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.assertEqual(logging.CRITICAL, logging.getLogger().level)
		
		self.__obj._add_standard_cli_options_logging()
		self.__obj.cli_parser.parse_known_args(['--verbose', '--verbose', '--verbose', '--verbose', '--verbose'])
		
		self.assertEqual(LogLevel.FINE_INFO, logging.getLogger().level)

	def test_verbose_6(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.assertEqual(logging.CRITICAL, logging.getLogger().level)
		
		self.__obj._add_standard_cli_options_logging()
		self.__obj.cli_parser.parse_known_args(['--verbose', '--verbose', '--verbose', '--verbose', '--verbose', '--verbose'])
		
		self.assertEqual(LogLevel.DEBUG, logging.getLogger().level)

	def test_verbose_7(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.assertEqual(logging.CRITICAL, logging.getLogger().level)
		
		self.__obj._add_standard_cli_options_logging()
		self.__obj.cli_parser.parse_known_args(['--verbose', '--verbose', '--verbose', '--verbose', '--verbose', '--verbose', '--verbose'])
		
		self.assertEqual(LogLevel.TRACE, logging.getLogger().level)

	def test_wall(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.assertEqual(logging.CRITICAL, logging.getLogger().level)
		
		self.__obj._add_standard_cli_options_logging()
		self.__obj.cli_parser.parse_known_args(['--Wall'])
		
		self.assertEqual(LogLevel.FINE_WARNING, logging.getLogger().level)

	def test_wnone(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.assertEqual(logging.CRITICAL, logging.getLogger().level)
		
		self.__obj._add_standard_cli_options_logging()
		self.__obj.cli_parser.parse_known_args(['--Wnone'])
		
		self.assertEqual(LogLevel.ERROR, logging.getLogger().level)


if __name__ == '__main__':
	unittest.main()

