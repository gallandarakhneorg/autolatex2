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
import tempfile
import logging
import os
from typing import override

from autolatex2.tex.utils import *

import autolatex2.utils.utilfunctions as genutils
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestFileType(AbstractBaseTest):

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)



	def test_tex_extensions(self):
		"""
		FileType.tex.extensions
		"""
		self.assertEqual(['.tex', '.latex', '.ltx'], FileType.tex.extensions())

	def test_file_type_tex_extensions(self):
		"""
		FileType.tex_extensions
		"""
		self.assertEqual(['.tex', '.latex', '.ltx', '.cls', '.sty'], FileType.tex_extensions())

	def test_is_tex_extension(self):
		"""
		FileType.is_tex_extension
		"""
		self.assertTrue(FileType.is_tex_extension('.tex'))
		self.assertTrue(FileType.is_tex_extension('.latex'))
		self.assertTrue(FileType.is_tex_extension('.ltx'))
		self.assertTrue(FileType.is_tex_extension('.TeX'))
		self.assertTrue(FileType.is_tex_extension('.LaTeX'))
		self.assertFalse(FileType.is_tex_extension('.doc'))

	def test_is_tex_document(self):
		"""
		FileType.is_tex_document
		"""
		self.assertTrue(FileType.is_tex_document('file.tex'))
		self.assertTrue(FileType.is_tex_document('file.latex'))
		self.assertTrue(FileType.is_tex_document('file.ltx'))
		self.assertTrue(FileType.is_tex_document('file.TeX'))
		self.assertTrue(FileType.is_tex_document('file.LaTeX'))
		self.assertFalse(FileType.is_tex_document('file.doc'))


if __name__ == '__main__':
	unittest.main()

