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

from autolatex2.config import scm
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestScmConfig(AbstractBaseTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = None

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__config = scm.ScmConfig()

	@property
	def config(self) -> scm.ScmConfig:
		return self.__config

	def test_get_commitCLI(self):
		self.assertEqual(list(), self.config.commit_cli)

	def test_set_commitCLI(self):
		self.config.commit_cli = None
		self.assertEqual([], self.config.commit_cli)
		self.config.commit_cli = list(['a', 'b'])
		self.assertEqual(list(['a',  'b']), self.config.commit_cli)
		self.config.commit_cli = 'a b'
		self.assertEqual(list(['a',  'b']), self.config.commit_cli)

	def test_get_updateCLI(self):
		self.assertEqual(list(), self.config.update_cli)

	def test_set_updateCLI(self):
		self.config.update_cli = None
		self.assertEqual([], self.config.update_cli)
		self.config.update_cli = list(['a', 'b'])
		self.assertEqual(list(['a',  'b']), self.config.update_cli)
		self.config.update_cli = 'a b'
		self.assertEqual(list(['a',  'b']), self.config.update_cli)


if __name__ == '__main__':
	unittest.main()

