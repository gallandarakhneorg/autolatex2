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

from autolatex2.config.configobj import Config
from autolatex2.make.maker import AutoLaTeXMaker
from autolatex2tests.abstract_base_test import AbstractBaseTest


class TestBuildWithBibunitsBiberMaker(AbstractBaseTest):
	"""
	Document using Bibunits databases and Biber tool.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__included_translators = [
				'eps2pdf_epstopdf',
				'imggz2img',
				'svg2pdf_inkscape',
			]
		self.__excluded_translators = [
				'asml2pdf',
				'astah2pdf',
				'astah2png',
				'asy2pdf',
				'cpp2tex_texify',
				'dia2pdf',
				'dia2pdf+tex',
				'dot2pdf',
				'dot2png',
				'dot2tex',
				'fig2pdf',
				'fig2pdf+tex',
				'java2tex_texify',
				'gxl2pdf',
				'gxl2png',
				'lisp2tex_texify',
				'matlab2tex_texify',
				'ml2tex_texify',
				'oct2pdf',
				'oct2png',
				'odg2pdf',
				'perl2tex_texify',
				'plot2pdf',
				'plot2pdf+tex',
				'ppt2pdf_libreoffice',
				'python2tex_texify',
				'ruby2tex_texify',
				'sql2tex_texify',
				'svg2pdf+layers_inkscape',
				'svg2pdf+layers+tex_inkscape',
				'svg2pdf+tex_inkscape',
				'svg2png_inkscape',
				'vsd2pdf',
				'xcf2pdf',
				'xcf2png',
				'xmi2pdf_umbrello',
			]

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__working_directory = os.getcwd()
		self.__resource_directory = os.path.normpath(os.path.join(str(os.path.dirname(__file__)),  '..', 'dev-resources'))
		self.__translators_directory = os.path.normpath(os.path.join(self.__resource_directory,  'translators'))
		self.__install_test_environment()

	@override
	def tearDown(self):
		super().tearDown()
		os.chdir(self.__working_directory)
		self._delete_temp_directory(self.__tmp_folder)

	def __install_test_environment(self):
		self.__tmp_folder = self._create_temp_directory()
		self.__tmp_folder_name = self.__tmp_folder.name
		self.__img_folder = os.path.normpath(os.path.join(self.__tmp_folder_name, 'imgs', 'auto'))
		self.__root_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.tex'))
		self.__bib_a_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.bib'))
		self.__bib_b_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'secondbib.bib'))
		self.__bbl_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.bbl'))
		self.__aux_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.aux'))
		self.__img_a_file = os.path.normpath(os.path.join(self.__img_folder, 'img1.svg'))
		self.__pdf_img_a_file = os.path.normpath(os.path.join(self.__img_folder, 'img1.pdf'))
		self.__img_b_file = os.path.normpath(os.path.join(self.__img_folder, 'img2.png.gz'))
		self.__png_img_b_file = os.path.normpath(os.path.join(self.__img_folder, 'img2.png'))
		self.__pdf_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.pdf'))
		self.__glo_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.glo'))
		self.__gls_file = os.path.normpath(os.path.join(self.__tmp_folder_name, 'rootfile.gls'))

		self.__config = Config()
		self.__config.document_directory = self.__tmp_folder_name
		self.__config.document_filename = 'rootfile.tex'

		# Activate the Biber tool
		self.__config.generation.is_biber = True

		self.__config.generation.pdf_mode = True
		self.__config.translators.add_image_path(self.__img_folder)
		self.__config.translators.is_translator_enable = True
		self.__config.translators.ignore_user_translators = True
		self.__config.translators.ignore_document_translators = True
		for trans in self.__included_translators:
			self.__config.translators.set_included(trans, None, True)
		for trans in self.__excluded_translators:
			self.__config.translators.set_included(trans, None, False)

		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test26.tex')), self.__root_file)
		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test26.bib')), self.__bib_a_file)
		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'test26.bib')), self.__bib_b_file)
		os.makedirs(self.__img_folder, exist_ok=True)
		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'translators', 'testimg.svg')), self.__img_a_file)
		shutil.copyfile(os.path.normpath(os.path.join(self.__resource_directory, 'translators', 'testimg.png.gz')), self.__img_b_file)

		self.__maker = AutoLaTeXMaker.create(self.__config)
		os.chdir(self.__tmp_folder_name)

	def test_fresh(self):
		"""
		Build the build list from a fresh installation
		"""
		generated_images = self.__maker.run_translators(force_generation= True, detect_conflicts = False)
		self.assertEqual(2, len(generated_images))
		self.assertIn(self.__img_a_file, generated_images)
		self.assertEqual(self.__pdf_img_a_file, generated_images[self.__img_a_file])
		self.assertIn(self.__img_b_file, generated_images)
		self.assertEqual(self.__png_img_b_file, generated_images[self.__img_b_file])

		result = self.__maker.build()
		self.assertTrue(result)
		self.assertTrue(os.path.isfile(self.__pdf_file))
		warns = self.__maker.standard_warnings
		self.assertFalse(warns)


if __name__ == '__main__':
	unittest.main()

