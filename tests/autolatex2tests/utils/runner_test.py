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

from autolatex2.utils.runner import Runner, CommandExecutionError
from autolatex2tests.abstract_base_test import AbstractBaseTest


class TestRunner(AbstractBaseTest):

	PYTHON_CMD : str = 'python3'

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)



	def test_run_python_valid1(self):
		output = Runner.run_python('myvar = \'abc\'')
		self.assertEqual('', output.error_output)
		self.assertEqual('', output.standard_output)
		self.assertIsNone(output.exception)
		self.assertEqual(0, output.return_code)

	def test_run_python_valid2(self):
		output = Runner.run_python('myvar = \'abc\'\nprint(myvar)')
		self.assertEqual('', output.error_output)
		self.assertEqual('abc\n', output.standard_output)
		self.assertIsNone(output.exception)
		self.assertEqual(0, output.return_code)

	def test_run_python_valid3(self):
		output = Runner.run_python('import sys\nmyvar = \'abc\'\nsys.stderr.write(myvar)')
		self.assertEqual('abc', output.error_output)
		self.assertEqual('', output.standard_output)
		self.assertIsNone(output.exception)
		self.assertEqual(0, output.return_code)

	def test_run_python_valid4(self):
		with self.assertRaises(NotImplementedError):
			Runner.run_python('raise NotImplementedError', show_script_on_error = False)

	def test_run_python_valid5(self):
		with self.assertRaises(NotImplementedError):
			Runner.run_python('raise NotImplementedError', intercept_error = False, show_script_on_error = False)

	def test_run_python_valid6(self):
		output = Runner.run_python('raise NotImplementedError', intercept_error = True, show_script_on_error = False)
		self.assertEqual('', output.error_output)
		self.assertEqual('', output.standard_output)
		self.assertIsInstance(output.exception, NotImplementedError)
		self.assertNotEqual(0, output.return_code)

	def test_run_python_invalid1(self):
		with self.assertRaises(SyntaxError):
			Runner.run_python(script = 'print(1',  show_script_on_error = False)

	def test_run_python_invalid2(self):
		with self.assertRaises(SyntaxError):
			Runner.run_python(script = 'print(1', intercept_error = False,  show_script_on_error = False)

	def test_run_python_invalid3(self):
		output = Runner.run_python(script = 'print(1', intercept_error = True,  show_script_on_error = False)
		self.assertEqual('', output.error_output)
		self.assertEqual('', output.standard_output)
		self.assertIsInstance(output.exception, SyntaxError)
		self.assertNotEqual(0, output.return_code)



	def test_run_command_valid1(self):
		output = Runner.run_command(self.PYTHON_CMD, '-c', 'print(123)')
		self.assertEqual('', output.error_output)
		self.assertEqual('123\n', output.standard_output)
		self.assertIsNone(output.exception)
		self.assertEqual(0, output.return_code)

	def test_run_command_valid2(self):
		output = Runner.run_command(self.PYTHON_CMD, '-c', "import sys\nsys.stderr.write('123\\n')")
		self.assertEqual('123\n', output.error_output)
		self.assertEqual('', output.standard_output)
		self.assertIsNone(output.exception)
		self.assertEqual(0, output.return_code)

	def test_run_command_invalid1(self):
		output = Runner.run_command(self.PYTHON_CMD, '-c', "sys.stderr.write('123\\n')")
		self.assertIn('NameError: name \'sys\' is not defined', output.error_output)
		self.assertEqual('', output.standard_output)
		self.assertIsInstance(output.exception, CommandExecutionError)
		self.assertNotEqual(0, output.exception.errno)
		self.assertNotEqual(0, output.return_code)
		self.assertEqual(output.exception.errno, output.return_code)




	def test_run_script_valid1(self):
		script = 'print(123)'
		output = Runner.run_script(script, self.PYTHON_CMD, '-')
		self.assertEqual('', output.error_output)
		self.assertEqual('123\n', output.standard_output)
		self.assertIsNone(output.exception)
		self.assertEqual(0, output.return_code)

	def test_run_script_valid2(self):
		script = 'import sys\nsys.stderr.write(\'123\\n\')'
		output = Runner.run_script(script, self.PYTHON_CMD, '-')
		self.assertEqual('', output.standard_output)
		self.assertEqual('123\n', output.error_output)
		self.assertIsNone(output.exception)
		self.assertEqual(0, output.return_code)

	def test_run_script_invalid1(self):
		script = 'sys.stderr.write(\'123\\n\')'
		output = Runner.run_script(script, self.PYTHON_CMD, '-')
		self.assertIn('NameError: name \'sys\' is not defined', output.error_output)
		self.assertEqual('', output.standard_output)
		self.assertIsInstance(output.exception, CommandExecutionError)
		self.assertNotEqual(0, output.exception.errno)
		self.assertNotEqual(0, output.return_code)
		self.assertEqual(output.exception.errno, output.return_code)




if __name__ == '__main__':
	unittest.main()

