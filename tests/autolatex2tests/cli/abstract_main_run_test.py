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
import unittest
from argparse import Namespace
from typing import override

from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.cli.abstract_main import AbstractAutoLaTeXMain
from autolatex2.cli.autolatexcommands import AutolatexCommand
from autolatex2.cli.exiters import AutoLaTeXExiter, AutoLaTeXExceptionExiter
from autolatex2.utils.extlogging import LogLevel
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestAbstractMainRun(AbstractBaseTest):

	class InternalMainMock(AbstractAutoLaTeXMain):
		def __init__(self):
			super().__init__(args = ['clean', '--unknown-opt-debug', 'xyz', '--debug'])

		@override
		def _run_program(self, cli_arguments : Namespace, positional_arguments : list[str], unknown_arguments: list[str]):
			raise NotImplementedError

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__resource_directory = os.path.normpath(os.path.join(os.path.dirname(__file__),  '..', 'dev-resources'))
		self.__translator_resource_directory = os.path.normpath(os.path.join(self.__resource_directory,  'translators'))
		self.__resource_file = os.path.normpath(os.path.join(self.__resource_directory,  'test1.tex'))
		self.__obj = TestAbstractMainRun.InternalMainMock()

	def assertIsRegisteredCommand(self, commands : dict[str,AutolatexCommand], name : str):
		self.assertIsNotNone(commands[name])
		self.assertIsNotNone(commands[name].name)
		self.assertIsNotNone(commands[name].creator_type)

	def test__pre_run_program(self):
		self.assertFalse(self.__obj.configuration.document_directory)

		cli_parser, commands, arguments = self.__obj._pre_run_program(False)

		self.assertTrue(self.__obj.configuration.document_directory)
		self.assertEqual(LogLevel.DEBUG, logging.getLogger().level)

		self.assertEqual([], commands)
		self.assertEqual(['clean', '--unknown-opt-debug', 'xyz'], arguments)


	def test__post_run_program(self):
		class ExisterMock(AutoLaTeXExiter):
			def __init__(self):
				self.on_failure = False
				self.on_exception = False
				self.exception = None
				self.on_success = False

			@override
			def exit_on_failure(self):
				self.on_failure = True

			@override
			def exit_on_exception(self, exception: BaseException):
				self.on_exception = True
				self.exception = exception

			@override
			def exit_on_success(self):
				self.on_success = True

		exister_mock = ExisterMock()
		self.__obj.exiter = exister_mock
		cli_parser, commands, arguments = self.__obj._pre_run_program(False)

		self.__obj._post_run_program(cli_parser, commands, arguments)

		self.assertFalse(exister_mock.on_failure)
		self.assertFalse(exister_mock.on_exception)
		self.assertIsNone( exister_mock.exception)
		self.assertTrue(exister_mock.on_success)


	def test_build_command_dict(self):
		commands = self.__obj.build_command_dict('autolatex2tests.cli.commandmocks')

		self.assertEqual(1, len(commands))
		self.assertIsRegisteredCommand(commands, 'command_mock')


	def test__create_cli_arguments_for_commands(self):
		commands = self.__obj.build_command_dict('autolatex2tests.cli.commandmocks')

		cmd = commands['command_mock']
		self.assertIsNotNone(cmd)

		self.__obj._create_cli_arguments_for_commands(commands=commands, title="the title", help_text="the help")

		cmd_instance = cmd.instance
		self.assertIsNotNone(cmd_instance)
		self.assertIsNotNone(cmd_instance.configuration)
		self.assertFalse(cmd_instance.is_run)

		a, b = cmd_instance.parse_cli.parse_known_intermixed_args(['abc', '--not-opt-debug', 'xyz', '--commandopt'])
		self.assertIsNotNone(a)
		self.assertEqual(['abc', '--not-opt-debug', 'xyz'], b)

		a, b = cmd_instance.parse_cli.parse_known_intermixed_args(['abc', '--not-opt-debug', 'xyz', '--commandopt', '--version'])
		self.assertIsNotNone(a)
		self.assertEqual(['abc', '--not-opt-debug', 'xyz', '--version'], b)


	def test__execute_commands_1(self):
		self.__obj.exiter = AutoLaTeXExceptionExiter()
		commands = self.__obj.build_command_dict('autolatex2tests.cli.commandmocks')
		cmd = commands['command_mock']
		self.assertIsNotNone(cmd)
		self.__obj._create_cli_arguments_for_commands(commands=commands, title="the title", help_text="the help")

		self.__obj._execute_commands(['command_mock'], commands, None)
		self.assertIsNotNone(cmd.instance.configuration)
		self.assertTrue(cmd.instance.is_run)


	def test__execute_commands_2(self):
		self.__obj.exiter = AutoLaTeXExceptionExiter()
		commands = self.__obj.build_command_dict('autolatex2tests.cli.commandmocks')
		cmd = commands['command_mock']
		self.assertIsNotNone(cmd)
		self.__obj._create_cli_arguments_for_commands(commands=commands, title="the title", help_text="the help")

		with self.assertRaises(Exception):
			self.__obj._execute_commands(['command_mock', 'unknown_command_mock'], commands, None)


	def test__execute_commands_3(self):
		self.__obj.exiter = AutoLaTeXExceptionExiter()
		commands = self.__obj.build_command_dict('autolatex2tests.cli.commandmocks')
		cmd = commands['command_mock']
		self.assertIsNotNone(cmd)
		self.__obj._create_cli_arguments_for_commands(commands=commands, title="the title", help_text="the help")

		with self.assertRaises(Exception):
			self.__obj._execute_commands(['unknown_command_mock', 'command_mock'], commands)


	def test__execute_commands_4(self):
		self.__obj.exiter = AutoLaTeXExceptionExiter()
		commands = self.__obj.build_command_dict('autolatex2tests.cli.commandmocks')
		cmd = commands['command_mock']
		self.assertIsNotNone(cmd)
		self.__obj._create_cli_arguments_for_commands(commands=commands, title="the title", help_text="the help")

		self.__obj._execute_commands(['command_mock', 'command_mock'], commands, None)
		self.assertIsNotNone(cmd.instance.configuration)
		self.assertTrue(cmd.instance.is_run)


	def test_build_command_list_from_prerequisites_wo_loop1(self):
		self.__obj.exiter = AutoLaTeXExceptionExiter()
		all_commands = dict({
			'a': AutolatexCommand('a', AbstractMakerAction, 'help a', [], []),
			'b': AutolatexCommand('b', AbstractMakerAction, 'help b', [], ['a']),
			'c': AutolatexCommand('c', AbstractMakerAction, 'help c', [], []),
			'd': AutolatexCommand('d', AbstractMakerAction, 'help d', [], ['b', 'c']),
			'e': AutolatexCommand('e', AbstractMakerAction, 'help e', [], ['c']),
		})
		results = self.__obj.build_command_list_from_prerequisites(['b', 'd', 'c'], all_commands)
		if results[0] == 'c':
			self.assertEqual(['c', 'a', 'b', 'd'], results)
		else:
			self.assertEqual(['a', 'c', 'b', 'd'], results)

	def test_build_command_list_from_prerequisites_wo_loop2(self):
		self.__obj.exiter = AutoLaTeXExceptionExiter()
		all_commands = dict({
			'a': AutolatexCommand('a', AbstractMakerAction, 'help a', [], ['e']),
			'b': AutolatexCommand('b', AbstractMakerAction, 'help b', [], ['a']),
			'c': AutolatexCommand('c', AbstractMakerAction, 'help c', [], []),
			'd': AutolatexCommand('d', AbstractMakerAction, 'help d', [], ['b', 'c']),
			'e': AutolatexCommand('e', AbstractMakerAction, 'help e', [], ['c']),
		})
		results = self.__obj.build_command_list_from_prerequisites(['b', 'd', 'c'], all_commands)
		self.assertEqual(['c', 'e', 'a', 'b', 'd'], results)

	def test_build_command_list_from_prerequisites_wo_loop3(self):
		self.__obj.exiter = AutoLaTeXExceptionExiter()
		all_commands = dict({
			'a': AutolatexCommand('a', AbstractMakerAction, 'help a', [], ['e']),
			'b': AutolatexCommand('b', AbstractMakerAction, 'help b', [], ['a']),
			'c': AutolatexCommand('c', AbstractMakerAction, 'help c', [], []),
			'd': AutolatexCommand('d', AbstractMakerAction, 'help d', [], ['b', 'c']),
			'e': AutolatexCommand('e', AbstractMakerAction, 'help e', [], ['c']),
		})
		results = self.__obj.build_command_list_from_prerequisites(['b', 'c', 'd', 'c', 'e'], all_commands)
		self.assertEqual(['c', 'e', 'a', 'b', 'd'], results)

	def test_build_command_list_from_prerequisites_w_loop1(self):
		self.__obj.exiter = AutoLaTeXExceptionExiter()
		all_commands = dict({
			'a': AutolatexCommand('a', AbstractMakerAction, 'help a', [], []),
			'b': AutolatexCommand('b', AbstractMakerAction, 'help b', [], ['a']),
			'c': AutolatexCommand('c', AbstractMakerAction, 'help c', [], ['d']),
			'd': AutolatexCommand('d', AbstractMakerAction, 'help d', [], ['b', 'c']),
			'e': AutolatexCommand('e', AbstractMakerAction, 'help e', [], ['c']),
		})
		with self.assertRaises(Exception):
			results = self.__obj.build_command_list_from_prerequisites(['b', 'd', 'c'], all_commands)


	def test_build_command_list_from_prerequisites_w_loop2(self):
		self.__obj.exiter = AutoLaTeXExceptionExiter()
		all_commands = dict({
			'a': AutolatexCommand('a', AbstractMakerAction, 'help a', [], ['e']),
			'b': AutolatexCommand('b', AbstractMakerAction, 'help b', [], ['a']),
			'c': AutolatexCommand('c', AbstractMakerAction, 'help c', [], ['e']),
			'd': AutolatexCommand('d', AbstractMakerAction, 'help d', [], ['b', 'c']),
			'e': AutolatexCommand('e', AbstractMakerAction, 'help e', [], ['c']),
		})
		with self.assertRaises(Exception):
			results = self.__obj.build_command_list_from_prerequisites(['b', 'd', 'c'], all_commands)


if __name__ == '__main__':
	unittest.main()

