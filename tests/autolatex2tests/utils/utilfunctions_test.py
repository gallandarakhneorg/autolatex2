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

import os
import unittest
import logging
from typing import override

import autolatex2.utils.utilfunctions as genutils
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestUtils(AbstractBaseTest):

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)



	def test_first_of(self):
		self.assertEqual('a', genutils.first_of('a', 'b', 'c'))
		self.assertEqual('a', genutils.first_of(None, 'a', 'b', 'c'))
		self.assertEqual('a', genutils.first_of(None, 'a', None, 'b', 'c'))
		self.assertEqual('a', genutils.first_of(None, None, 'a', None, 'b', 'c'))

	def test_basename_inline_a(self):
		self.assertEqual('name', genutils.simple_basename('name.ext', '.ext'))
		self.assertEqual('name', genutils.simple_basename('name.ext', '.ext', '.a'))
		self.assertEqual('name', genutils.simple_basename('name.ext', '.a', '.ext'))
		self.assertEqual('name.ext', genutils.simple_basename('name.ext', '.a'))
		self.assertEqual('name.ext', genutils.simple_basename('name.ext'))

	def test_basename_inline_b(self):
		d = os.path.join('a',  'b', 'c')
		act = os.path.join(d,  'name.ext')
		exp = 'name'
		exp2 = 'name.ext'
		self.assertEqual(exp, genutils.simple_basename(act, '.ext'))
		self.assertEqual(exp, genutils.simple_basename(act, '.ext', '.a'))
		self.assertEqual(exp, genutils.simple_basename(act, '.a', '.ext'))
		self.assertEqual(exp2, genutils.simple_basename(act, '.a'))
		self.assertEqual(exp2, genutils.simple_basename(act))

	def test_basename_texfilename(self):
		d = os.path.join('a', 'b', 'c')
		act = os.path.join(d, 'name+endname+tex.plot')
		exp = 'name+endname'
		self.assertEqual(exp, genutils.simple_basename(act, '.plott', '.plot_tex', '.plottex', '.plot+tex',
												'.tex.plot', '+tex.plot', '.gnut', '.gnu_tex', '.gnutex',
												'.gnu+tex', '.tex.gnu', '+tex.gnu'))

	def test_basename_with_path_inline_a(self):
		self.assertEqual('name', genutils.basename_with_path('name.ext', '.ext'))
		self.assertEqual('name', genutils.basename_with_path('name.ext', '.ext', '.a'))
		self.assertEqual('name', genutils.basename_with_path('name.ext', '.a', '.ext'))
		self.assertEqual('name.ext', genutils.basename_with_path('name.ext', '.a'))
		self.assertEqual('name.ext', genutils.basename_with_path('name.ext'))

	def test_basename_with_path_inline_b(self):
		d = os.path.join('a',  'b', 'c')
		act = os.path.join(d,  'name.ext')
		exp = os.path.join(d,  'name')
		exp2 = os.path.join(d,  'name.ext')
		self.assertEqual(exp, genutils.basename_with_path(act, '.ext'))
		self.assertEqual(exp, genutils.basename_with_path(act, '.ext', '.a'))
		self.assertEqual(exp, genutils.basename_with_path(act, '.a', '.ext'))
		self.assertEqual(exp2, genutils.basename_with_path(act, '.a'))
		self.assertEqual(exp2, genutils.basename_with_path(act))

	def test_basename_with_path_texfilename(self):
		d = os.path.join('a',  'b', 'c')
		act = os.path.join(d,  'name+endname+tex.plot')
		exp = os.path.join(d, 'name+endname')
		self.assertEqual(exp, genutils.basename_with_path(act, '.plott', '.plot_tex', '.plottex', '.plot+tex',
												 '.tex.plot', '+tex.plot', '.gnut', '.gnu_tex', '.gnutex',
												 '.gnu+tex', '.tex.gnu', '+tex.gnu'))

	def test_parse_cli_noException(self):
		environment = { 'a': 'va', 'b': 'vb', 'c': 'vc' }
		self.assertListEqual([], genutils.parse_cli('', environment))
		self.assertListEqual([ 'abc', '--def', 'ghi' ], genutils.parse_cli('abc --def ghi', environment))
		self.assertListEqual([ 'abc', '--def', 'ghi' ], genutils.parse_cli('abc --def ${z} ghi', environment))
		self.assertListEqual([ 'abc', '--def', 'va', 'ghi' ], genutils.parse_cli('abc --def $a ghi', environment))
		self.assertListEqual([ 'abc', '--def', 'vbbc', 'ghi' ], genutils.parse_cli('abc --def ${b}bc ghi', environment))
		self.assertListEqual([ 'abc', os.path.expanduser('~') ], genutils.parse_cli('abc $HOME', environment))

	def test_parse_cli_exception(self):
		environment = { 'a': 'va', 'b': 'vb', 'c': 'vc' }
		exception = { 'b' }
		self.assertListEqual([], genutils.parse_cli('', environment, exception))
		self.assertListEqual([ 'abc', '--def', 'ghi' ], genutils.parse_cli('abc --def ghi', environment, exception))
		self.assertListEqual([ 'abc', '--def', 'ghi' ], genutils.parse_cli('abc --def ${z} ghi', environment, exception))
		self.assertListEqual([ 'abc', '--def', 'va', 'ghi' ], genutils.parse_cli('abc --def $a ghi', environment, exception))
		self.assertListEqual([ 'abc', '--def', '${b}bc', 'ghi' ], genutils.parse_cli('abc --def ${b}bc ghi', environment, exception))
		self.assertListEqual([ 'abc', os.path.expanduser('~') ], genutils.parse_cli('abc $HOME', environment, exception))

	def test_get_filename_extension_from_w_ext_w_exts(self):
		self.assertEqual(".tex", genutils.get_filename_extension_from('the_filename.tex', 'ltx', '.tex'))

	def test_get_filename_extension_from_w_otherext_w_exts(self):
		self.assertIsNone(genutils.get_filename_extension_from('the_filename.txt', 'ltx', '.tex'))

	def test_get_filename_extension_from_wo_ext_w_exts(self):
		self.assertIsNone(genutils.get_filename_extension_from('the_filename', 'ltx', '.tex'))

	def test_get_filename_extension_from_w_ext_wo_exts(self):
		self.assertIsNone(genutils.get_filename_extension_from('the_filename.tex'))

	def test_get_filename_extension_from_w_otherext_wo_exts(self):
		self.assertIsNone(genutils.get_filename_extension_from('the_filename.txt'))

	def test_get_filename_extension_from_wo_ext_wo_exts(self):
		self.assertIsNone(genutils.get_filename_extension_from('the_filename'))

	def test_ensure_filename_extension_oneext_exist(self):
		self.assertEqual('the_filename.myext', genutils.ensure_filename_extension('the_filename.myext', '.myext'))

	def test_ensure_filename_extension_oneext_noexist(self):
		self.assertEqual('the_filename.myext', genutils.ensure_filename_extension('the_filename', '.myext'))

	def test_ensure_filename_extension_oneext_otherext(self):
		self.assertEqual('the_filename.myext', genutils.ensure_filename_extension('the_filename.jpg', '.myext'))



if __name__ == '__main__':
	unittest.main()

