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

from autolatex2.config.translator import TranslatorLevel
from autolatex2.config import translator
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestTranslatorConfig(AbstractBaseTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = None

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__config = translator.TranslatorConfig()

	@property
	def config(self) -> translator.TranslatorConfig:
		return self.__config

	def assertFalseNotNone(self, v):
		self.assertIsNotNone(v)
		self.assertFalse(v)




	def test_includePaths_getter(self):
		self.assertListEqual([], self.config.include_paths)

	def test_includePaths_setter(self):
		self.config.include_paths = ['a', 'b', 'c']
		self.assertListEqual([ 'a', 'b', 'c' ], self.config.include_paths)



	def test_imagePaths_getter(self):
		self.assertListEqual([], self.config.image_paths)

	def test_imagePaths_setter(self):
		self.config.image_paths = ['a', 'b', 'c']
		self.assertListEqual([ 'a', 'b', 'c' ], self.config.image_paths)



	def test_imagesToConvert_getter(self):
		self.assertSetEqual(set(), self.config.images_to_convert)

	def test_imagesToConvert_setter(self):
		self.config.images_to_convert = {'a', 'b', 'c'}
		self.assertSetEqual({ 'a', 'b', 'c' }, self.config.images_to_convert)



	def test_setIncluded(self):
		self.config.set_included('a', TranslatorLevel.SYSTEM, False)
		self.config.set_included('a', TranslatorLevel.USER, None)
		self.config.set_included('a', TranslatorLevel.DOCUMENT, True)
		self.config.set_included('b', TranslatorLevel.DOCUMENT, False)

		self.assertListEqual(
			[	{ 'a': False},
				{},
				{ 'a': True, 'b': False},
			], self.config.inclusions)


	def test_included_inheriting(self):
		self.config.set_included('a', TranslatorLevel.SYSTEM, False)
		self.config.set_included('a', TranslatorLevel.USER, None)
		self.config.set_included('a', TranslatorLevel.DOCUMENT, True)
		self.config.set_included('b', TranslatorLevel.DOCUMENT, False)

		self.assertFalseNotNone(self.config.included('a', TranslatorLevel.SYSTEM))
		self.assertFalseNotNone(self.config.included('a', TranslatorLevel.USER))
		self.assertTrue(self.config.included('a', TranslatorLevel.DOCUMENT))
		self.assertIsNone(self.config.included('b', TranslatorLevel.SYSTEM))
		self.assertIsNone(self.config.included('b', TranslatorLevel.USER))
		self.assertFalseNotNone(self.config.included('b', TranslatorLevel.DOCUMENT))
		self.assertIsNone(self.config.included('c', TranslatorLevel.SYSTEM))
		self.assertIsNone(self.config.included('c', TranslatorLevel.USER))
		self.assertIsNone(self.config.included('c', TranslatorLevel.DOCUMENT))

	def test_included_notInheriting(self):
		self.config.set_included('a', TranslatorLevel.SYSTEM, False)
		self.config.set_included('a', TranslatorLevel.USER, None)
		self.config.set_included('a', TranslatorLevel.DOCUMENT, True)
		self.config.set_included('b', TranslatorLevel.DOCUMENT, False)

		self.assertFalseNotNone(self.config.included('a', TranslatorLevel.SYSTEM, inherit=False))
		self.assertIsNone(self.config.included('a', TranslatorLevel.USER, inherit=False))
		self.assertTrue(self.config.included('a', TranslatorLevel.DOCUMENT, inherit=False))
		self.assertIsNone(self.config.included('b', TranslatorLevel.SYSTEM, inherit=False))
		self.assertIsNone(self.config.included('b', TranslatorLevel.USER, inherit=False))
		self.assertFalseNotNone(self.config.included('b', TranslatorLevel.DOCUMENT, inherit=False))
		self.assertIsNone(self.config.included('c', TranslatorLevel.SYSTEM, inherit=False))
		self.assertIsNone(self.config.included('c', TranslatorLevel.USER, inherit=False))
		self.assertIsNone(self.config.included('c', TranslatorLevel.DOCUMENT, inherit=False))


	def test_inclusionLevel_1(self):
		self.config.set_included('a', TranslatorLevel.SYSTEM, False)
		self.config.set_included('a', TranslatorLevel.USER, None)
		self.config.set_included('a', TranslatorLevel.DOCUMENT, True)
		self.config.set_included('b', TranslatorLevel.DOCUMENT, False)

		self.assertEqual(TranslatorLevel.DOCUMENT, self.config.inclusion_level('a'))
		self.assertEqual(TranslatorLevel.NEVER, self.config.inclusion_level('b'))
		self.assertIsNone(self.config.inclusion_level('c'))

	def test_inclusionLevel_2(self):
		self.config.set_included('a', TranslatorLevel.SYSTEM, False)
		self.config.set_included('a', TranslatorLevel.USER, None)
		self.config.set_included('a', TranslatorLevel.DOCUMENT, True)
		self.config.set_included('b', TranslatorLevel.SYSTEM, False)
		self.config.set_included('b', TranslatorLevel.USER, True)

		self.assertEqual(TranslatorLevel.DOCUMENT, self.config.inclusion_level('a'))
		self.assertEqual(TranslatorLevel.USER, self.config.inclusion_level('b'))
		self.assertIsNone(self.config.inclusion_level('c'))



	def test_translators_1(self):
		self.config.set_included('a', TranslatorLevel.SYSTEM, False)
		self.config.set_included('a', TranslatorLevel.USER, None)
		self.config.set_included('a', TranslatorLevel.DOCUMENT, True)
		self.config.set_included('b', TranslatorLevel.DOCUMENT, False)

		tr = self.config.translators()
		self.assertEqual(2,  len(tr))
		self.assertTrue('a' in tr)
		self.assertTrue(tr['a'])
		self.assertTrue('b' in tr)
		self.assertFalse(tr['b'])

	def test_translators_2(self):
		self.config.set_included('a', TranslatorLevel.SYSTEM, False)
		self.config.set_included('a', TranslatorLevel.USER, None)
		self.config.set_included('a', TranslatorLevel.DOCUMENT, True)
		self.config.set_included('b', TranslatorLevel.SYSTEM, False)
		self.config.set_included('b', TranslatorLevel.USER, True)

		tr = self.config.translators()
		self.assertEqual(2,  len(tr))
		self.assertTrue('a' in tr)
		self.assertTrue(tr['a'])
		self.assertTrue('b' in tr)
		self.assertTrue(tr['b'])


if __name__ == '__main__':
	unittest.main()

