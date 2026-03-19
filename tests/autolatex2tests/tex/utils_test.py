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

from autolatex2.tex.utils import *

import autolatex2.utils.utilfunctions as genutils
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestUtils(AbstractBaseTest):

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)



	def test_getTeXFileExtensions(self):
		self.assertEqual(['.tex', '.latex', '.ltx'], get_tex_file_extensions())

	def test_isTeXFileExtension(self):
		self.assertTrue(is_tex_file_extension('.tex'))
		self.assertTrue(is_tex_file_extension('.latex'))
		self.assertTrue(is_tex_file_extension('.ltx'))
		self.assertTrue(is_tex_file_extension('.TeX'))
		self.assertTrue(is_tex_file_extension('.LaTeX'))
		self.assertFalse(is_tex_file_extension('.doc'))

	def test_isTeXdocument(self):
		self.assertTrue(is_tex_document('file.tex'))
		self.assertTrue(is_tex_document('file.latex'))
		self.assertTrue(is_tex_document('file.ltx'))
		self.assertTrue(is_tex_document('file.TeX'))
		self.assertTrue(is_tex_document('file.LaTeX'))
		self.assertFalse(is_tex_document('file.doc'))

	def test_extractTeXWarningFromLine_00(self):
		wset = set()
		self.assertTrue(extract_tex_warning_from_line('\n\nWarning: There were undefined references. re-run the LaTeX compiler', wset))
		self.assertEqual(set([]), wset)
	
	def test_extractTeXWarningFromLine_01(self):
		wset = set()
		self.assertFalse(extract_tex_warning_from_line('\n\nWarning: There were undefined references', wset))
		self.assertEqual(set([TeXWarnings.undefined_reference]), wset)

	def test_extractTeXWarningFromLine_02(self):
		wset = set()
		self.assertFalse(extract_tex_warning_from_line('\n\nWarning: Citation XYZ undefined', wset))
		self.assertEqual(set([TeXWarnings.undefined_citation]), wset)

	def test_extractTeXWarningFromLine_03(self):
		wset = set()
		self.assertFalse(extract_tex_warning_from_line('\n\nWarning: There were multiply-defined labels', wset))
		self.assertEqual(set([TeXWarnings.multiple_definition]), wset)

	def test_extractTeXWarningFromLine_04(self):
		wset = set()
		self.assertFalse(extract_tex_warning_from_line('\n\nWarning: This is a warning', wset))
		self.assertEqual(set([TeXWarnings.other_warning]), wset)

	def test_parseTeXLogFile_noFatal(self):
		filename = genutils.find_file_in_path("test1.txt")
		if filename:
			filename = genutils.find_file_in_path("test1.txt", use_environment_variable=True)
		self.assertIsNotNone(filename)
		fatal_error, blocks = parse_tex_log_file(filename)
		self.assertEqual('', fatal_error)
		self.assertEqual(164, len(blocks))

	def test_parseTeXLogFile_fatal(self):
		filename = genutils.find_file_in_path("test2.txt")
		if filename:
			filename = genutils.find_file_in_path("test2.txt", use_environment_variable=True)
		self.assertIsNotNone(filename)
		fatal_error, blocks = parse_tex_log_file(filename)
		self.assertTrue(fatal_error.startswith("Undefined control sequence."))
		self.assertEqual(42, len(blocks))



if __name__ == '__main__':
	unittest.main()

