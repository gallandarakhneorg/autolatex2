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

from autolatex2.config import generation
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestGenerationConfig(AbstractBaseTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = None

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__config = generation.GenerationConfig()

	@property
	def config(self) -> generation.GenerationConfig:
		return self.__config

	def test_get_pdfMode(self):
		self.assertTrue(self.config.pdf_mode)

	def test_set_pdfMode(self):
		self.config.pdf_mode = False
		self.assertFalse(self.config.pdf_mode)
		self.config.pdf_mode = True
		self.assertTrue(self.config.pdf_mode)
		self.config.pdf_mode = False
		self.assertFalse(self.config.pdf_mode)
		self.config.pdf_mode = True
		self.assertTrue(self.config.pdf_mode)



if __name__ == '__main__':
	unittest.main()

