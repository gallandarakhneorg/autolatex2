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
import shutil
from typing import override

from autolatex2.translator.interpreters.perlinterpreter import TranslatorInterpreter
from autolatex2.config.configobj import Config
from autolatex2.utils.runner import CommandExecutionError
from autolatex2tests.abstract_base_test import AbstractBaseTest


class TestTranslatorInterpreter(AbstractBaseTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__interpreter = None
		self.__config = Config()

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__interpreter = TranslatorInterpreter(self.__config)

	@property
	def interpreter(self):
		return self.__interpreter


	def test_runnable(self):
		if shutil.which('perl') is not None:
			self.assertTrue(self.interpreter.runnable)
		else:
			self.assertFalse(self.interpreter.runnable)

	@unittest.skipUnless(shutil.which('perl') is not None, "Perl interpreter not installed")
	def test_run_valid1(self):
		output = self.interpreter.run('my $myvar = \'abc\';')
		self.assertEqual('', output.standard_output)
		self.assertEqual('', output.error_output)
		self.assertIsNone(output.exception)
		self.assertEqual(0, output.return_code)

	@unittest.skipUnless(shutil.which('perl') is not None, "Perl interpreter not installed")
	def test_run_valid2(self):
		output = self.interpreter.run('my $myvar = \'abc\'; print "$myvar\\n";')
		self.assertEqual('abc\n', output.standard_output)
		self.assertEqual('', output.error_output)
		self.assertIsNone(output.exception)
		self.assertEqual(0, output.return_code)

	@unittest.skipUnless(shutil.which('perl') is not None, "Perl interpreter not installed")
	def test_run_valid3(self):
		output = self.interpreter.run('my $myvar = \'abc\'; print STDERR $myvar;')
		self.assertEqual('', output.standard_output)
		self.assertEqual('abc', output.error_output)
		self.assertIsNone(output.exception)
		self.assertEqual(0, output.return_code)

	@unittest.skipUnless(shutil.which('perl') is not None, "Perl interpreter not installed")
	def test_run_valid4(self):
		output = self.interpreter.run('die "error";')
		self.assertEqual('', output.standard_output)
		self.assertEqual('error at - line 5.\n', output.error_output)
		self.assertIsInstance(output.exception, CommandExecutionError)
		self.assertNotEqual(0, output.exception.errno)
		self.assertNotEqual(0, output.return_code)
		self.assertEqual(output.exception.errno, output.return_code)

	@unittest.skipUnless(shutil.which('perl') is not None, "Perl interpreter not installed")
	def test_run_invalid1(self):
		output = self.interpreter.run('print (1')
		self.assertEqual('', output.standard_output)
		self.assertEqual('syntax error at - line 5, at EOF\nExecution of - aborted due to compilation errors.\n', output.error_output)
		self.assertIsInstance(output.exception, CommandExecutionError)
		self.assertNotEqual(0, output.exception.errno)
		self.assertNotEqual(0, output.return_code)
		self.assertEqual(output.exception.errno, output.return_code)


if __name__ == '__main__':
	unittest.main()

