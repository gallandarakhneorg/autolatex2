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

import re
import shutil
import unittest
import os

from autolatex2tests.translators.abstract_test_translator import AbstractTranslatorTest


class TestIssue00009(AbstractTranslatorTest):
	"""
	Issue #9: Invalid generation of layered figure from SVG+layer.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__('+layers.svg', 'pdftex_t', 'svg2pdf+layers_inkscape',
						 ['svg2pdf_inkscape', 'svg2pdf+layers+tex_inkscape',
						  'svg2pdf+tex_inkscape', 'svg2png_inkscape'],
						 *args, **kwargs)
		self.__svg_filename = None
		self.__pdftex_filename = None

	def _install_test_environment(self, image_extension : str, target_extension : str, translator_name : str, excluded_translators : list[str]):
		super()._install_test_environment(image_extension, target_extension, translator_name, excluded_translators)
		# Overwrite the source image
		self.__svg_filename = os.path.normpath(os.path.join(self._resource_directory, '..', 'issues', 'issue_00009_valid.svg'))
		self.__pdftex_filename = os.path.normpath(os.path.join(self._img_folder, 'testimg.pdftex_t'))
		shutil.copyfile(self.__svg_filename, self._img_file)

	def assertPdftex_Tex(self, expected_specifications : list[str]):
		with open(self.__pdftex_filename, 'rt') as pdft_file:
			content = pdft_file.read()
		matches = re.finditer(r"\\node\s*\<\s*([^\>]+)\s*\>\s*\(X\)", content)
		specifications = [match.group(1).strip() for match in matches]
		self.assertEqual('\n'.join(expected_specifications), '\n'.join(specifications))


	def test_run_translator(self):
		build_map = self._maker.run_translators(detect_conflicts = False)
		self.assertGeneratedFile(build_map)
		# Now test the content of the generated file
		self.assertPdftex_Tex([
			'1-',
			'1,3-',
			'2',
			'1-2,4-',
			'3',
			'1-3,5-',
			'4',
			'1-4,6-',
			'5',
			'1-5,7-',
			'6',
			'1-6',
			'7',
		])


if __name__ == '__main__':
	unittest.main()

