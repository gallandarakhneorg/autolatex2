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

from autolatex2.config.configobj import Config
from autolatex2.translator.interpreters.abstractinterpreter import AbstractTranslatorInterpreter
from autolatex2tests.abstract_base_test import AbstractBaseTest



class AbstractTranslatorInterpreterMock(AbstractTranslatorInterpreter):
	def __init__(self, configuration : Config):
		super().__init__(configuration)

	@override
	def run(self, code: str):
		raise NotImplementedError

	@override
	def filter_variable_name(self, name: str) -> str:
		raise NotImplementedError


class TestAbstractTranslatorInterpreter(AbstractBaseTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__interpreter = None
		self.__config = Config()

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__interpreter = AbstractTranslatorInterpreterMock(self.__config)

	@property
	def interpreter(self):
		return self.__interpreter




	def test_parent_getter(self):
		self.assertIsNone(self.interpreter.parent)

	def test_parent_setter(self):
		p = AbstractTranslatorInterpreterMock(self.__config)
		self.interpreter.parent = p
		self.assertEqual(p, self.interpreter.parent)



	def test_globalVariables(self):
		self.assertFalse('foo' in self.interpreter.global_variables)
		self.interpreter.global_variables['foo'] = 'abc'
		self.assertEqual('abc', self.interpreter.global_variables['foo'])
		self.interpreter.global_variables['foo'] = ''
		self.assertEqual('', self.interpreter.global_variables['foo'])
		self.interpreter.global_variables['foo'] = None
		self.assertIsNone(self.interpreter.global_variables['foo'])




	def test_runnable(self):
		with self.assertRaises(NotImplementedError):
			x = self.interpreter.runnable
			self.assertTrue(x)



	def test_run(self):
		with self.assertRaises(NotImplementedError):
			self.interpreter.run('abc')




	def test_toPython_scalar(self):
		self.assertEqual('1', self.interpreter.to_python(1))
		self.assertEqual('\'abc\'', self.interpreter.to_python('abc'))
		self.assertEqual('"abc\'def"', self.interpreter.to_python('abc\'def'))
		self.assertEqual('\'abc"def\'', self.interpreter.to_python('abc"def'))
		self.assertEqual('\'abc"def\\\'ghi\'', self.interpreter.to_python('abc"def\'ghi'))

	def test_toPython_list(self):
		self.assertEqual('[1, 2, 3]', self.interpreter.to_python([1, 2, 3]))
		self.assertEqual('[1, 2, [3, 4, 5, 6]]', self.interpreter.to_python([1, 2, [3, 4, 5, 6]]))

	def test_toPython_set(self):
		self.assertEqual('{1, 2, 3}', self.interpreter.to_python({1, 2, 3}))

	def test_toPython_dict(self):
		self.assertEqual('{1: 2, 3: 4}', self.interpreter.to_python({1:2, 3:4}))



if __name__ == '__main__':
	unittest.main()

