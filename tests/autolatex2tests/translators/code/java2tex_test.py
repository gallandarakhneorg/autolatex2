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

from autolatex2tests.translators.abstract_test_translator import AbstractTranslatorTest

class TestJava2texTranslator(AbstractTranslatorTest):

	def __init__(self, *args, **kwargs):
		super().__init__('java', 'tex', 'java2tex_texify',
						 [],
						 *args, **kwargs)


	def test_run_translator(self):
		build_map = self._maker.run_translators(detect_conflicts = False)
		self.assertGeneratedFile(build_map)


if __name__ == '__main__':
	unittest.main()

