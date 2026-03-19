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
import unittest
from typing import override

from autolatex2.cli.abstract_main import AbstractAutoLaTeXMain
from autolatex2.cli.exiters import AutoLaTeXExceptionExiter
from autolatex2tests.abstract_base_test import AbstractBaseTest


class TestAbstractMain(AbstractBaseTest):

	class InternalMainMock(AbstractAutoLaTeXMain):
		def __init__(self):
			super().__init__()

		@override
		def _run_program(self, positional_arguments : list[str], unknown_arguments: list[str]):
			raise NotImplementedError


	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__obj = TestAbstractMain.InternalMainMock()


	def test_configuration(self):
		self.assertIsNotNone(self.__obj.configuration)

	def test_cli_parser(self):
		self.assertIsNotNone(self.__obj.cli_parser)

	def test_exiter(self):
		self.assertIsNotNone(self.__obj.exiter)

	def test_exiter_none(self):
		self.__obj.exiter = None
		self.assertIsNotNone(self.__obj.exiter)

	def test_exiter_obj(self):
		self.__obj.exiter = AutoLaTeXExceptionExiter()
		self.assertIsNotNone(self.__obj.exiter)


if __name__ == '__main__':
	unittest.main()

