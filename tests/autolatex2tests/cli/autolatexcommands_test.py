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

from autolatex2.cli.autolatexcommands import AutolatexCommand
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestAutolatexCommand(AbstractBaseTest):

	class InternalMock:
		def __init__(self):
			self.data = "xyz"

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__obj = AutolatexCommand('my_name',
									  TestAutolatexCommand.InternalMock,
									  'my_help',
									  ['alias1', 'alias2', 'alias3'],
									  [])


	def test_name(self):
		"""
		obj.name
		"""
		self.assertEqual('my_name', self.__obj.name)

	def test_help(self):
		"""
		obj.help
		"""
		self.assertEqual('my_help', self.__obj.help)

	def test_aliases(self):
		"""
		obj.aliases
		"""
		self.assertEqual(['alias1', 'alias2', 'alias3'], self.__obj.aliases)

	def test_creator_type(self):
		"""
		obj.creator_type
		"""
		self.assertEqual(TestAutolatexCommand.InternalMock, self.__obj.creator_type)

	def test_instance(self):
		"""
		obj.instance
		"""
		instance = self.__obj.instance
		self.assertIsNotNone(instance)
		self.assertEqual("xyz", instance.data)


if __name__ == '__main__':
	unittest.main()

