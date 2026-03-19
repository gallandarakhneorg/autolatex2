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

import argparse
import logging
import unittest
from argparse import Namespace
from typing import Any, override

from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.cli.autolatexcommands import AutolatexCommand
from autolatex2.config.configobj import Config
from autolatex2tests.abstract_base_test import AbstractBaseTest


class TestAbstractMakerAction(AbstractBaseTest):

	class InternalActionMock(AbstractMakerAction):
		def __init__(self):
			super().__init__()
			self.data = dict()
			
		def _add_command_cli_arguments(self, command_name, command_help, command_aliases):
			self.data['command-name'] = command_name
			self.data['command-help'] = command_help
			self.data['command-aliases'] = command_aliases

		def run(self, cli_arguments : Namespace) -> bool:
			self.data['command-run'] = True
			return super().run(cli_arguments)

	class ParserCliMock(argparse.ArgumentParser):
		def __init__(self):
			super().__init__()
			self.data = "xyz"
		def set_defaults(self, **kwargs):
			pass

	class ArgumentParserMock:
		def __init__(self):
			self.data = "xyz"
		def add_parser(self, name : str, help : str, aliases : list[str]) -> Any:
			return TestAbstractMakerAction.ParserCliMock()

	class InternalCommandMock:
		def __init__(self):
			self.data = "xyz"


	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__obj = TestAbstractMakerAction.InternalActionMock()


	def test_configuration_wo_register(self):
		self.assertIsNone(self.__obj.configuration)
		
	def test_run(self):
		self.assertTrue(self.__obj.run(None))
		self.assertTrue(self.__obj.data['command-run'])

	def test_register_command(self):
		action_parser = TestAbstractMakerAction.ArgumentParserMock()
		command = AutolatexCommand('my_name',
								   TestAbstractMakerAction.InternalCommandMock,
								   'my_help',
								   ['alias1'],
								   [])
		config = Config()
		
		self.__obj.register_command(action_parser, command.name, command.help, command.aliases, config)

		self.assertEqual(config, self.__obj.configuration)
		self.assertEqual("my_name", self.__obj.data['command-name'])
		self.assertEqual("my_help", self.__obj.data['command-help'])
		self.assertEqual(["alias1"], self.__obj.data['command-aliases'])



if __name__ == '__main__':
	unittest.main()

