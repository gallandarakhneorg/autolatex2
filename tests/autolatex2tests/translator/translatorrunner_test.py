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
import shutil
import tempfile
import time
import textwrap
from typing import override
import unittest

from autolatex2.config.translator import TranslatorLevel
from autolatex2.translator.translatorrepository import TranslatorRepository
from autolatex2.translator.translatorrunner import TranslatorRunner
from autolatex2.utils.extlogging import ensure_autolatex_logging_levels
import autolatex2.utils.utilfunctions as genutils
from autolatex2.config.configobj import Config
from autolatex2tests.abstract_base_test import AbstractBaseTest


def generate_translator_stubs():
	directory = tempfile.mkdtemp()
	with open(os.path.join(directory, "svg2pdf.transdef"), 'w') as f:
		f.write("MUST BE OVERRIDDEN")
		f.flush()
	with open(os.path.join(directory, "dot2pdf.transdef"), 'w') as f:
		f.write(textwrap.dedent("""\
			INPUT_EXTENSIONS = .dot

			OUTPUT_EXTENSIONS for pdf = .pdf
			OUTPUT_EXTENSIONs for eps = .eps

			TRANSLATOR_FUNCTION =<<EOL {
				if ($ispdfmode) {
					runCommandOrFail('dot', '-Tpdf', "$in", '-o', "$out");
					1;
				}
				else {
					my $svgFile = File::Spec->catfile(
								dirname($out),
								basename($out,@outexts).'.svg');
					runCommandOrFail('dot', '-Tsvg', "$in", '-o', "$svgFile");
					$transresult = runTranslator('svg2pdf', "$svgFile", "$out");
					unlink("$svgFile");
					$transresult;
				}
			}
			EOL
			"""))
		f.flush()
	subdir = os.path.join(directory, 'subdir')
	os.makedirs(subdir)
	with open(os.path.join(subdir, "svg2pdf.transdef"), 'w') as f:
		f.write(textwrap.dedent("""\
			# Test content only
			INPUT_EXTENSIONS = .svg .svgz

			OUTPUT_EXTENSIONS for pdf = .pdf
			OUTPUT_EXTENSIONS for eps = .eps

			COMMAND_LINE for pdf = inkscape --without-gui --export-area-page --export-pdf "$out" "$in"
			COMMAND_LINE for eps = inkscape --without-gui --export-area-page --export-eps "$out" "$in"
			"""))
		f.flush()
	with open(os.path.join(subdir, "svg2pdf+tex.transdef"), 'w') as f:
		f.write(textwrap.dedent("""\
			INPUT_EXTENSIONS = .svgt .svg_t .svgtex .svg+tex .tex.svg +tex.svg .svgzt .svgz_t .svgztex .svgz+tex .tex.svgz +tex.svgz

			OUTPUT_EXTENSIONS for pdf = .pdf .pdftex_t
			OUTPUT_EXTENSIONS for eps = .eps .pstex_t

			COMMAND_LINE = dosomething

			FILES_TO_CLEAN = $out.pdftex_t $out.pstex_t
			"""))
		f.flush()
	with open(os.path.join(subdir, "uml2pdf_umbrello.transdef"), 'w') as f:
		f.write("")
		f.flush()
	return directory


def generate_translator_stubs_for_generation():
	directory = tempfile.mkdtemp()
	with open(os.path.join(directory, "svg2pdf_cli.transdef"), 'w') as f:
		f.write(textwrap.dedent("""\
			INPUT_EXTENSIONS = .svg
			OUTPUT_EXTENSIONS = .pdf
			COMMAND_LINE = touch $out
			"""))
		f.flush()
	with open(os.path.join(directory, "svg2pdf_python.transdef"), 'w') as f:
		f.write(textwrap.dedent("""\
			INPUT_EXTENSIONS = .svg
			OUTPUT_EXTENSIONS = .pdf
			TRANSLATOR_FUNCTION with python =<<EOL
			with open(_out, 'w') as f:
				f.write("CONTENT\\n")
			EOL
			"""))
		f.flush()
	with open(os.path.join(directory, "svg2pdf_perl.transdef"), 'w') as f:
		f.write(textwrap.dedent('''\
			INPUT_EXTENSIONS = .svg
			OUTPUT_EXTENSIONS = .pdf
			TRANSLATOR_FUNCTION with perl =<<EOL
			{ local *FILE;
			  open(*FILE, "> $out") or die("$out: $!\n");
			  print FILE "CONTENT\\n";
			  close(*FILE);
			}
			EOL
			'''))
		f.flush()
	return directory

def generate_image_stubs():
	directory = tempfile.mkdtemp()
	with open(os.path.join(directory, "img1.svg"), 'w') as f:
		f.write("")
		f.flush()
	with open(os.path.join(directory, "img2.svg+tex"), 'w') as f:
		f.write("")
		f.flush()
	subdir = os.path.join(directory, 'subdir')
	os.makedirs(subdir)
	with open(os.path.join(subdir, "img3.dot"), 'w') as f:
		f.write("")
		f.flush()
	with open(os.path.join(subdir, "img4+tex.svg"), 'w') as f:
		f.write("")
		f.flush()
	with open(os.path.join(subdir, "img5.unsupported"), 'w') as f:
		f.write("")
		f.flush()
	return directory



class TestTranslatorRunner(AbstractBaseTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.directory1 = None
		self.directory2 = None
		self.repo = None
		self.runner = None
		self.config = None

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.directory1 = generate_translator_stubs()
		self.directory2 = generate_image_stubs()
		self.config = Config()
		self.config.translators.is_translator_fileformat_1_enable = True
		self.config.translators.ignore_system_translators = True
		self.config.translators.ignore_user_translators = True
		self.config.translators.ignore_document_translators = True
		self.config.translators.include_paths = [self.directory1]
		self.config.translators.image_paths = [self.directory2]
		self.repo = TranslatorRepository(self.config)
		self.runner = TranslatorRunner(self.repo)
		self.runner.sync()

	@override
	def tearDown(self):
		if self.autodelete and self.directory1 is not None:
			shutil.rmtree(self.directory1)
			self.directory1 = None
		if self.autodelete and self.directory2 is not None:
			shutil.rmtree(self.directory2)
			self.directory2 = None


	def test_get_source_images_notRecursive(self):
		self.config.translators.recursive_image_path = False
		images = self.runner.get_source_images()
		self.assertSetEqual(
			{	os.path.join(self.directory2, 'img1.svg'),
				os.path.join(self.directory2, 'img2.svg+tex'),
			}, images)


	def test_get_source_images_recursive(self):
		self.config.translators.recursive_image_path = True
		images = self.runner.get_source_images()
		self.assertSetEqual(
			{	os.path.join(self.directory2, 'img1.svg'),
				os.path.join(self.directory2, 'img2.svg+tex'),
				os.path.join(self.directory2, 'subdir', 'img3.dot'),
				os.path.join(self.directory2, 'subdir', 'img4+tex.svg'),
			}, images)


	def __assert_gtf(self,  filename : str,  translator_name : str):
		expected = self.repo.get_object_for(translator_name)
		actual = self.runner.get_translator_for(filename)
		self.assertEqual(expected, actual)
		
	def test_get_translator_for(self):
		self.__assert_gtf('img1.svg', 'svg2pdf')
		self.__assert_gtf('img1.svg+tex',  'svg2pdf+tex')
		self.__assert_gtf('img1+tex.svg', 'svg2pdf+tex')
		self.__assert_gtf('img1.tex.svg', 'svg2pdf+tex')
		self.__assert_gtf('img1_tex.svg', 'svg2pdf')
		self.__assert_gtf('img1.svgz', 'svg2pdf')



class TestTranslatorRunnerGeneration(AbstractBaseTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.directory1 = None
		self.directory2 = None
		self.repo = None
		self.runner = None
		self.config = None

	@override
	def setUp(self):
		ensure_autolatex_logging_levels()
		logging.getLogger().setLevel(logging.CRITICAL)
		self.directory1 = generate_translator_stubs_for_generation()
		self.directory2 = generate_image_stubs()
		self.config = Config()
		self.config.translators.is_translator_fileformat_1_enable = True
		self.config.translators.ignore_system_translators = True
		self.config.translators.ignore_user_translators = True
		self.config.translators.ignore_document_translators = True
		self.config.translators.include_paths = [self.directory1]
		self.config.translators.image_paths = [self.directory2]
		self.repo = TranslatorRepository(self.config)
		self.runner = TranslatorRunner(self.repo)

	@override
	def tearDown(self):
		if self.autodelete and self.directory1 is not None:
			shutil.rmtree(self.directory1)
			self.directory1 = None
		if self.autodelete and self.directory2 is not None:
			shutil.rmtree(self.directory2)
			self.directory2 = None

	def test_generateImages_cli_force(self):
		self.config.translators.set_included('svg2pdf_cli', TranslatorLevel.SYSTEM, True)
		self.config.translators.set_included('svg2pdf_python', TranslatorLevel.SYSTEM, False)
		self.config.translators.set_included('svg2pdf_perl', TranslatorLevel.SYSTEM, False)
		self.runner.sync()
		self.assertEqual(
				os.path.join(self.directory2, 'img1.pdf'),
				self.runner.generate_image(in_file=os.path.join(self.directory2, 'img1.svg'), only_more_recent=False))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))

	def test_generateImages_python_force(self):
		self.config.translators.set_included('svg2pdf_cli', TranslatorLevel.SYSTEM, False)
		self.config.translators.set_included('svg2pdf_python', TranslatorLevel.SYSTEM, True)
		self.config.translators.set_included('svg2pdf_perl', TranslatorLevel.SYSTEM, False)
		self.runner.sync()
		self.assertEqual(
				os.path.join(self.directory2, 'img1.pdf'),
				self.runner.generate_image(in_file=os.path.join(self.directory2, 'img1.svg'), only_more_recent=False))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))

	def test_generateImages_perl_force(self):
		self.config.translators.set_included('svg2pdf_cli', TranslatorLevel.SYSTEM, False)
		self.config.translators.set_included('svg2pdf_python', TranslatorLevel.SYSTEM, False)
		self.config.translators.set_included('svg2pdf_perl', TranslatorLevel.SYSTEM, True)
		self.runner.sync()
		self.assertEqual(
				os.path.join(self.directory2, 'img1.pdf'),
				self.runner.generate_image(in_file=os.path.join(self.directory2, 'img1.svg'), only_more_recent=False))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))

	def test_generateImages_cli_noForce(self):
		self.config.translators.set_included('svg2pdf_cli', TranslatorLevel.SYSTEM, True)
		self.config.translators.set_included('svg2pdf_python', TranslatorLevel.SYSTEM, False)
		self.config.translators.set_included('svg2pdf_perl', TranslatorLevel.SYSTEM, False)
		self.runner.sync()
		self.runner.generate_image(in_file=os.path.join(self.directory2, 'img1.svg'), only_more_recent=False)
		last_change = genutils.get_file_last_change(os.path.join(self.directory2, 'img1.pdf'))
		time.sleep(1)
		self.assertIsNone(
				self.runner.generate_image(in_file=os.path.join(self.directory2, 'img1.svg')))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))
		last_change2 = genutils.get_file_last_change(os.path.join(self.directory2, 'img1.pdf'))
		self.assertEqual(last_change, last_change2)

	def test_generateImages_python_noForce(self):
		self.config.translators.set_included('svg2pdf_cli', TranslatorLevel.SYSTEM, False)
		self.config.translators.set_included('svg2pdf_python', TranslatorLevel.SYSTEM, True)
		self.config.translators.set_included('svg2pdf_perl', TranslatorLevel.SYSTEM, False)
		self.runner.sync()
		self.runner.generate_image(in_file=os.path.join(self.directory2, 'img1.svg'), only_more_recent=False)
		last_change = genutils.get_file_last_change(os.path.join(self.directory2, 'img1.pdf'))
		time.sleep(1)
		self.assertIsNone(
				self.runner.generate_image(in_file=os.path.join(self.directory2, 'img1.svg')))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))
		last_change2 = genutils.get_file_last_change(os.path.join(self.directory2, 'img1.pdf'))
		self.assertEqual(last_change, last_change2)

	def test_generateImages_perl_noForce(self):
		self.config.translators.set_included('svg2pdf_cli', TranslatorLevel.SYSTEM, False)
		self.config.translators.set_included('svg2pdf_python', TranslatorLevel.SYSTEM, False)
		self.config.translators.set_included('svg2pdf_perl', TranslatorLevel.SYSTEM, True)
		self.runner.sync()
		self.runner.generate_image(in_file=os.path.join(self.directory2, 'img1.svg'), only_more_recent=False)
		last_change = genutils.get_file_last_change(os.path.join(self.directory2, 'img1.pdf'))
		time.sleep(1)
		self.assertIsNone(
				self.runner.generate_image(in_file=os.path.join(self.directory2, 'img1.svg')))
		self.assertTrue(os.path.isfile(os.path.join(self.directory2, 'img1.pdf')))
		last_change2 = genutils.get_file_last_change(os.path.join(self.directory2, 'img1.pdf'))
		self.assertEqual(last_change, last_change2)


if __name__ == '__main__':
	unittest.main()

