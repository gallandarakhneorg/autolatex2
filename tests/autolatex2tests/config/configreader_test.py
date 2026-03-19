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
from typing import override

from autolatex2.config import configreader
from autolatex2.config.configobj import Config
from autolatex2.config.translator import TranslatorLevel
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestOldStyleConfigReader(AbstractBaseTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = None
		self.__filename = None
		self.__reader = None
		self.__cfg = None
		self._dir = None

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__config = Config()
		self._dir = os.path.normpath(os.path.join(os.path.dirname(__file__),  '..', 'dev-resources'))
		self.__filename = os.path.join(self._dir,  'config.ini')
		self.__reader = configreader.OldStyleConfigReader()
		self.__cfg = self.__reader.read(self.__filename,  TranslatorLevel.USER)
		self.assertIsNotNone(self.__cfg)

	@property
	def rconfig(self) -> Config:
		return self.__cfg

	def test_generation_generateimages(self):
		self.assertTrue(self.rconfig.translators.is_translator_enable)

	def test_generation_imagedirectory(self):
		self.assertEqual([os.path.join(self._dir, 'a', 'b', 'c', 'd'),
			os.path.join(self._dir, 'x', 'y', 'z')], self.rconfig.translators.image_paths)

	def test_generation_generationtype(self):
		self.assertFalse(self.rconfig.generation.pdf_mode)

	def test_generation_texcompiler(self):
		self.assertEqual('xelatex', self.rconfig.generation.latex_compiler)

	def test_generation_synctex(self):
		self.assertTrue(self.rconfig.generation.synctex)

	def test_generation_tranlatorincludepath(self):
		actual = self.rconfig.translators.include_paths
		self.assertEqual([os.path.join(self._dir, 'path1'),
			os.path.join(self._dir, 'path2', 'a')],  actual)

	def test_generation_latexcmd(self):
		self.assertEqual(['latex2'], self.rconfig.generation.latex_cli)

	def test_generation_bibtexcmd(self):
		self.assertEqual(['bibtex2'], self.rconfig.generation.bibtex_cli)

	def test_generation_bibercmd(self):
		self.assertEqual(['biber2'], self.rconfig.generation.biber_cli)

	def test_generation_makeglossariescmd(self):
		self.assertEqual(['mkg'], self.rconfig.generation.makeglossary_cli)

	def test_generation_makeindexcmd(self):
		self.assertEqual(['mkidx'], self.rconfig.generation.makeindex_cli)

	def test_generation_dvi2pscmd(self):
		self.assertEqual(['dvips2'], self.rconfig.generation.dvips_cli)

	def test_generation_latexflags(self):
		self.assertEqual(['-f1',  '-f2'], self.rconfig.generation.latex_flags)

	def test_generation_bibtexflags(self):
		self.assertEqual(['-f3',  '-f4'], self.rconfig.generation.bibtex_flags)

	def test_generation_biberflags(self):
		self.assertEqual(['-f5',  '-f6'], self.rconfig.generation.biber_flags)

	def test_generation_makegossariesflags(self):
		self.assertEqual(['-f7',  '-f8'], self.rconfig.generation.makeglossary_flags)

	def test_generation_makeindexflags(self):
		self.assertEqual(['-f9',  '-f10'], self.rconfig.generation.makeindex_flags)

	def test_generation_dvi2psflags(self):
		self.assertEqual(['-f11',  '-f12'], self.rconfig.generation.dvips_flags)

	def test_generation_mainfile(self):
		absdir = os.path.dirname(os.path.normpath(os.path.join(self._dir,  os.path.join('.',  'a',  't.tex'))))
		self.assertEqual(absdir, self.rconfig.document_directory)
		self.assertEqual('t.tex', self.rconfig.document_filename)

	def test_generation_makeindexstyle(self):
		self.assertEqual(os.path.join(self.__config.installation_directory, 'default.ist'), self.rconfig.generation.makeindex_style_filename)




if __name__ == '__main__':
	unittest.main()

