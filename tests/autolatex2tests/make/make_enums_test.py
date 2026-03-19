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
from typing import override

from autolatex2.make.make_enums import TeXCompiler, TeXTools, BibCompiler, IndexCompiler, GlossaryCompiler
from autolatex2tests.abstract_base_test import AbstractBaseTest


class TestMakeEnumerationTypes(AbstractBaseTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)

	def test_texcompiler_pdflatex(self):
		self.assertEqual(TeXTools.pdflatex, TeXCompiler.pdflatex)

	def test_texcompiler_latex(self):
		self.assertEqual(TeXTools.latex, TeXCompiler.latex)

	def test_texcompiler_xelatex(self):
		self.assertEqual(TeXTools.xelatex, TeXCompiler.xelatex)

	def test_texcompiler_lualatex(self):
		self.assertEqual(TeXTools.lualatex, TeXCompiler.lualatex)

	def test_bibcompiler_bibtex(self):
		self.assertEqual(TeXTools.bibtex, BibCompiler.bibtex)

	def test_bibcompiler_biber(self):
		self.assertEqual(TeXTools.biber, BibCompiler.biber)

	def test_indexcompiler_makeindex(self):
		self.assertEqual(TeXTools.makeindex, IndexCompiler.makeindex)

	def test_indexcompiler_texindy(self):
		self.assertEqual(TeXTools.texindy, IndexCompiler.texindy)

	def test_glossarycompiler_texindy(self):
		self.assertEqual(TeXTools.makeglossaries, GlossaryCompiler.makeglossaries)




if __name__ == '__main__':
	unittest.main()

