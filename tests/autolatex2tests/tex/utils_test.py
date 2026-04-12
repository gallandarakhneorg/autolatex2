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
from typing import override

from autolatex2.tex.utils import *

import autolatex2.utils.utilfunctions as genutils
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestUtils(AbstractBaseTest):

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)


	def test_extract_tex_warning_from_line_00(self):
		wset = set()
		self.assertTrue(extract_tex_warning_from_line('\n\nWarning: There were undefined references. re-run the LaTeX compiler', wset))
		self.assertEqual(set(), wset)
	
	def test_extract_tex_warning_from_line_01(self):
		wset = set()
		self.assertFalse(extract_tex_warning_from_line('\n\nWarning: There were undefined references', wset))
		self.assertEqual({TeXWarnings.undefined_reference}, wset)

	def test_extract_tex_warning_from_line_02(self):
		wset = set()
		self.assertFalse(extract_tex_warning_from_line('\n\nWarning: Citation XYZ undefined', wset))
		self.assertEqual({TeXWarnings.undefined_citation}, wset)

	def test_extract_tex_warning_from_line_03(self):
		wset = set()
		self.assertFalse(extract_tex_warning_from_line('\n\nWarning: There were multiply-defined labels', wset))
		self.assertEqual({TeXWarnings.multiple_definition}, wset)

	def test_extract_tex_warning_from_line_04(self):
		wset = set()
		self.assertFalse(extract_tex_warning_from_line('\n\nWarning: This is a warning', wset))
		self.assertEqual({TeXWarnings.other_warning}, wset)

	def test_parse_tex_log_file_noFatal(self):
		filename = genutils.find_file_in_path("test1.txt")
		if filename:
			filename = genutils.find_file_in_path("test1.txt", use_environment_variable=True)
		self.assertIsNotNone(filename)
		assert filename is not None
		fatal_error, blocks = parse_tex_log_file(filename)
		self.assertEqual('', fatal_error)
		self.assertEqual(164, len(blocks))

	def test_parse_tex_log_file_fatal(self):
		filename = genutils.find_file_in_path("test2.txt")
		if filename:
			filename = genutils.find_file_in_path("test2.txt", use_environment_variable=True)
		self.assertIsNotNone(filename)
		assert filename is not None
		fatal_error, blocks = parse_tex_log_file(filename)
		self.assertTrue(fatal_error.startswith("Undefined control sequence."))
		self.assertEqual(42, len(blocks))

	def test_find_aux_files_1_file_wo_subfolder_wo_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0)
			self.assertIsNotNone(aux_files)
			self.assertEqual(1, len(aux_files))
			self.assertTrue(aux_file_0 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_2_files_wo_subfolder_wo_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			aux_file_1 = os.path.join(folder.name, "root_file_0.aux")
			with open(aux_file_1, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0)
			self.assertIsNotNone(aux_files)
			self.assertEqual(2, len(aux_files))
			self.assertTrue(aux_file_0 in aux_files)
			self.assertTrue(aux_file_1 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_3_files_wo_subfolder_wo_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			aux_file_1 = os.path.join(folder.name, "root_file_0.aux")
			with open(aux_file_1, 'w') as f:
				f.write("xyz")
			aux_file_2 = os.path.join(folder.name, "bu1.aux")
			with open(aux_file_2, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0)
			self.assertIsNotNone(aux_files)
			self.assertEqual(3, len(aux_files))
			self.assertTrue(aux_file_0 in aux_files)
			self.assertTrue(aux_file_1 in aux_files)
			self.assertTrue(aux_file_2 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_1_file_w_subfolder_wo_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			subfolder_0 = os.path.join(folder.name, "sub0")
			os.makedirs(subfolder_0)
			aux_sfile_1 = os.path.join(subfolder_0, "sub0.aux")
			with open(aux_sfile_1, 'w') as f:
				f.write("xyz")
			subfolder_1 = os.path.join(folder.name, "sub1")
			os.makedirs(subfolder_1)
			aux_sfile_2 = os.path.join(subfolder_1, "sub1.aux")
			with open(aux_sfile_2, 'w') as f:
				f.write("xyz")
			tex_file_1 = os.path.join(subfolder_1, "sub1.tex")
			with open(tex_file_1, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0)
			self.assertIsNotNone(aux_files)
			self.assertEqual(2, len(aux_files))
			self.assertTrue(aux_file_0 in aux_files)
			self.assertFalse(aux_sfile_1 in aux_files)
			self.assertTrue(aux_sfile_2 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_2_files_w_subfolder_wo_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			aux_file_1 = os.path.join(folder.name, "root_file_0.aux")
			with open(aux_file_1, 'w') as f:
				f.write("xyz")
			subfolder_0 = os.path.join(folder.name, "sub0")
			os.makedirs(subfolder_0)
			aux_sfile_1 = os.path.join(subfolder_0, "sub0.aux")
			with open(aux_sfile_1, 'w') as f:
				f.write("xyz")
			subfolder_1 = os.path.join(folder.name, "sub1")
			os.makedirs(subfolder_1)
			aux_sfile_2 = os.path.join(subfolder_1, "sub1.aux")
			with open(aux_sfile_2, 'w') as f:
				f.write("xyz")
			tex_file_1 = os.path.join(subfolder_1, "sub1.tex")
			with open(tex_file_1, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0)
			self.assertIsNotNone(aux_files)
			self.assertEqual(3, len(aux_files))
			self.assertTrue(aux_file_0 in aux_files)
			self.assertTrue(aux_file_1 in aux_files)
			self.assertFalse(aux_sfile_1 in aux_files)
			self.assertTrue(aux_sfile_2 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_3_files_w_subfolder_wo_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			aux_file_1 = os.path.join(folder.name, "root_file_0.aux")
			with open(aux_file_1, 'w') as f:
				f.write("xyz")
			aux_file_2 = os.path.join(folder.name, "bu1.aux")
			with open(aux_file_2, 'w') as f:
				f.write("xyz")
			subfolder_0 = os.path.join(folder.name, "sub0")
			os.makedirs(subfolder_0)
			aux_sfile_1 = os.path.join(subfolder_0, "sub0.aux")
			with open(aux_sfile_1, 'w') as f:
				f.write("xyz")
			subfolder_1 = os.path.join(folder.name, "sub1")
			os.makedirs(subfolder_1)
			aux_sfile_2 = os.path.join(subfolder_1, "sub1.aux")
			with open(aux_sfile_2, 'w') as f:
				f.write("xyz")
			tex_file_1 = os.path.join(subfolder_1, "sub1.tex")
			with open(tex_file_1, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0)
			self.assertIsNotNone(aux_files)
			self.assertEqual(4, len(aux_files))
			self.assertTrue(aux_file_0 in aux_files)
			self.assertTrue(aux_file_1 in aux_files)
			self.assertTrue(aux_file_2 in aux_files)
			self.assertFalse(aux_sfile_1 in aux_files)
			self.assertTrue(aux_sfile_2 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_1_file_wo_subfolder_w_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0, lambda x: '1' in os.path.basename(x))
			self.assertIsNotNone(aux_files)
			self.assertEqual(0, len(aux_files))
		finally:
			folder.cleanup()

	def test_find_aux_files_2_files_wo_subfolder_w_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			aux_file_1 = os.path.join(folder.name, "root_file_0.aux")
			with open(aux_file_1, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0, lambda x: '1' in os.path.basename(x))
			self.assertIsNotNone(aux_files)
			self.assertEqual(0, len(aux_files))
		finally:
			folder.cleanup()

	def test_find_aux_files_3_files_wo_subfolder_w_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			aux_file_1 = os.path.join(folder.name, "root_file_0.aux")
			with open(aux_file_1, 'w') as f:
				f.write("xyz")
			aux_file_2 = os.path.join(folder.name, "bu1.aux")
			with open(aux_file_2, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0, lambda x: '1' in os.path.basename(x))
			self.assertIsNotNone(aux_files)
			self.assertEqual(1, len(aux_files))
			self.assertFalse(aux_file_0 in aux_files)
			self.assertFalse(aux_file_1 in aux_files)
			self.assertTrue(aux_file_2 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_1_file_w_subfolder_w_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			subfolder_0 = os.path.join(folder.name, "sub0")
			os.makedirs(subfolder_0)
			aux_sfile_1 = os.path.join(subfolder_0, "sub0.aux")
			with open(aux_sfile_1, 'w') as f:
				f.write("xyz")
			subfolder_1 = os.path.join(folder.name, "sub1")
			os.makedirs(subfolder_1)
			aux_sfile_2 = os.path.join(subfolder_1, "sub1.aux")
			with open(aux_sfile_2, 'w') as f:
				f.write("xyz")
			tex_file_1 = os.path.join(subfolder_1, "sub1.tex")
			with open(tex_file_1, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0, lambda x: '1' in os.path.basename(x))
			self.assertIsNotNone(aux_files)
			self.assertEqual(1, len(aux_files))
			self.assertFalse(aux_file_0 in aux_files)
			self.assertFalse(aux_sfile_1 in aux_files)
			self.assertTrue(aux_sfile_2 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_2_files_w_subfolder_w_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			aux_file_1 = os.path.join(folder.name, "root_file_0.aux")
			with open(aux_file_1, 'w') as f:
				f.write("xyz")
			subfolder_0 = os.path.join(folder.name, "sub0")
			os.makedirs(subfolder_0)
			aux_sfile_1 = os.path.join(subfolder_0, "sub0.aux")
			with open(aux_sfile_1, 'w') as f:
				f.write("xyz")
			subfolder_1 = os.path.join(folder.name, "sub1")
			os.makedirs(subfolder_1)
			aux_sfile_2 = os.path.join(subfolder_1, "sub1.aux")
			with open(aux_sfile_2, 'w') as f:
				f.write("xyz")
			tex_file_1 = os.path.join(subfolder_1, "sub1.tex")
			with open(tex_file_1, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0, lambda x: '1' in os.path.basename(x))
			self.assertIsNotNone(aux_files)
			self.assertEqual(1, len(aux_files))
			self.assertFalse(aux_file_0 in aux_files)
			self.assertFalse(aux_file_1 in aux_files)
			self.assertFalse(aux_sfile_1 in aux_files)
			self.assertTrue(aux_sfile_2 in aux_files)
		finally:
			folder.cleanup()

	def test_find_aux_files_3_files_w_subfolder_w_selector(self):
		folder = tempfile.TemporaryDirectory(delete=False)
		assert folder is not None
		try:
			tex_file_0 = os.path.join(folder.name, "root_file.tex")
			with open(tex_file_0, 'w') as f:
				f.write("xyz")
			aux_file_0 = os.path.join(folder.name, "root_file.aux")
			with open(aux_file_0, 'w') as f:
				f.write("xyz")
			aux_file_1 = os.path.join(folder.name, "root_file_0.aux")
			with open(aux_file_1, 'w') as f:
				f.write("xyz")
			aux_file_2 = os.path.join(folder.name, "bu1.aux")
			with open(aux_file_2, 'w') as f:
				f.write("xyz")
			subfolder_0 = os.path.join(folder.name, "sub0")
			os.makedirs(subfolder_0)
			aux_sfile_1 = os.path.join(subfolder_0, "sub0.aux")
			with open(aux_sfile_1, 'w') as f:
				f.write("xyz")
			subfolder_1 = os.path.join(folder.name, "sub1")
			os.makedirs(subfolder_1)
			aux_sfile_2 = os.path.join(subfolder_1, "sub1.aux")
			with open(aux_sfile_2, 'w') as f:
				f.write("xyz")
			tex_file_1 = os.path.join(subfolder_1, "sub1.tex")
			with open(tex_file_1, 'w') as f:
				f.write("xyz")

			aux_files = find_aux_files(tex_file_0, lambda x: '1' in os.path.basename(x))
			self.assertIsNotNone(aux_files)
			self.assertEqual(2, len(aux_files))
			self.assertFalse(aux_file_0 in aux_files)
			self.assertFalse(aux_file_1 in aux_files)
			self.assertTrue(aux_file_2 in aux_files)
			self.assertFalse(aux_sfile_1 in aux_files)
			self.assertTrue(aux_sfile_2 in aux_files)
		finally:
			folder.cleanup()

	def test_create_extended_tex_filename_w_ext(self):
		self.assertEqual("xxxx_autolatex_autogenerated.ltx", create_extended_tex_filename('xxxx.ltx'))

	def test_create_extended_tex_filename_w_otherext(self):
		self.assertEqual("xxxx.txt_autolatex_autogenerated", create_extended_tex_filename('xxxx.txt'))

	def test_create_extended_tex_filename_wo_ext(self):
		self.assertEqual("xxxx_autolatex_autogenerated", create_extended_tex_filename('xxxx'))

	def test_get_original_tex_filename_w_postfix_w_ext(self):
		self.assertEqual("xxxx.ltx", get_original_tex_filename('xxxx_autolatex_autogenerated.ltx'))

	def test_get_original_tex_filename_w_postfix_w_otherext(self):
		self.assertEqual("xxxx_autolatex_autogenerated.txt", get_original_tex_filename('xxxx_autolatex_autogenerated.txt'))

	def test_get_original_tex_filename_w_postfix_wo_ext(self):
		self.assertEqual("xxxx", get_original_tex_filename('xxxx_autolatex_autogenerated'))

	def assertTeXMessageFormat(self, e : str, i : str):
		self.assertEqual(e, fix_tex_message_format(i))

	def test_fix_tex_message_format_1(self):
		self.assertTeXMessageFormat(
			"hyperref.sty:6576: Package hyperref Message: Stopped early.",
			"hyperref.sty:6576: Package hyperref Message: Stopped early.")

	def test_fix_tex_message_format_2(self):
		self.assertTeXMessageFormat(
			"beamerbasethemeCIAD.sty:479: Package pgf Warning: File \"ciad-title-background-left9\" not found when defining image \"ciad-title-background-left9\". Tried all extensions in \".pdf:.jpg:.jpeg:.png:\" on input line 479.",
			"beamerbasethemeCIAD.sty:479: Package pgf Warning: File \"ciad\n-title-background-left9\" not found when defining image \"ciad-title-background-l\neft9\". Tried all extensions in \".pdf:.jpg:.jpeg:.png:\" on input line 479.")

	def test_fix_tex_message_format_3(self):
			self.assertTeXMessageFormat(
				"beamerbasethemeCIAD.sty:479: Package pgf Warning: Missing width for image \"ciad-title-background-left9\" (\"ciad-title-background-left9\") in draft mode. Using 1cm instead on input line 479.",
				"beamerbasethemeCIAD.sty:479: Package pgf Warning: Missing wi\ndth for image \"ciad-title-background-left9\" (\"ciad-title-background-left9\") in \ndraft mode. Using 1cm instead on input line 479.")

	def test_fix_tex_message_format_4(self):
		self.assertTeXMessageFormat(
			"beamerbasethemeCIAD.sty:856: Package pgf Warning: File \"ciadgraylogo\" not found when defining image \"ciadgraylogoinpartners\". Tried all extensions in \".pdf:.jpg:.jpeg:.png:\" on input line 856.",
			"beamerbasethemeCIAD.sty:856: Package pgf Warning: File \"ciad\ngraylogo\" not found when defining image \"ciadgraylogoinpartners\". Tried all ext\nensions in \".pdf:.jpg:.jpeg:.png:\" on input line 856.")

	def test_fix_tex_message_format_5(self):
		self.assertTeXMessageFormat(
			"beamerbasethemeCIAD.sty:856: Package pgf Warning: Missing width for image \"ciadgraylogoinpartners\" (\"ciadgraylogo\") in draft mode. Using 1cm instead on input line 856.",
			"beamerbasethemeCIAD.sty:856: Package pgf Warning: Missing wi\ndth for image \"ciadgraylogoinpartners\" (\"ciadgraylogo\") in draft mode. Using 1c\nm instead on input line 856.")

	def test_fix_tex_message_format_6(self):
		self.assertTeXMessageFormat(
			"beamerbasethemeCIAD.sty:2443: Package pgf Warning: File \"ciad-bg1\" not found when defining image \"CIADtitlebackground1\". Tried all extensions in \".pdf:.jpg:.jpeg:.png:\" on input line 2443.",
			"beamerbasethemeCIAD.sty:2443: Package pgf Warning: File \"cia\nd-bg1\" not found when defining image \"CIADtitlebackground1\". Tried all extensio\nns in \".pdf:.jpg:.jpeg:.png:\" on input line 2443.")

	def test_fix_tex_message_format_7(self):
		self.assertTeXMessageFormat(
			"talks/utseus/preamble:3: Package hyperref Warning: Token not allowed in a PDF string (Unicode):",
			"talks/utseus/preamble:3: Package hyperref Warning: Token\n not allowed in a PDF string (Unicode):")

	def test_fix_tex_message_format_8(self):
		self.assertTeXMessageFormat(
			"(hyperref) removing `math shift' on input line 3.",
			"\n(hyperref)                removing `math shift' on input line 3.")

	def test_fix_tex_message_format_9(self):
		self.assertTeXMessageFormat(
			"talks/utseus/preamble:3: Package hyperref Warning: Token not allowed in a PDF string (Unicode): removing `\\@@underline' on input line 3.",
			"talks/utseus/preamble:3: Package hyperref Warning: Token\n not allowed in a PDF string (Unicode):\n(hyperref)                removing `\\@@underline' on input line 3.")

	def test_fix_tex_message_format_10(self):
		self.assertTeXMessageFormat(
			"TALK.vrb:5: LaTeX Font Warning: Font shape `OMS/cmss/m/n' undefined using `OMS/cmsy/m/n' instead for symbol `textbraceleft' on input line 5.",
			"TALK.vrb:5: LaTeX Font Warning: Font shape `OMS/cmss/m/n' un\ndefined\n(Font)              using `OMS/cmsy/m/n' instead\n(Font)              for symbol `textbraceleft' on input line 5.")

	def test_fix_tex_message_format_11(self):
		self.assertTeXMessageFormat(
			"TALK.vrb:82: LaTeX Font Warning: Font shape `OML/cmss/m/n' undefined using `OML/cmm/m/it' instead for symbol `textgreater' on input line 82.",
			"TALK.vrb:82: LaTeX Font Warning: Font shape `OML/cmss/m/n' u\nndefined\n(Font)              using `OML/cmm/m/it' instead\n(Font)              for symbol `textgreater' on input line 82.")



if __name__ == '__main__':
	unittest.main()

