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
from abc import ABC
from argparse import Namespace
from typing import override

from autolatex2.cli.abstract_main import AbstractAutoLaTeXMain
from autolatex2.cli.autolatexcommands import AutolatexCommand
from autolatex2.cli.exiters import AutoLaTeXExceptionExiter
from autolatex2.config.configobj import Config
from autolatex2.utils import extprint
from autolatex2tests.abstract_base_test import AbstractBaseTest


class AbstractCommandTest(AbstractBaseTest,ABC):

	class InternalMainMock(AbstractAutoLaTeXMain):

		def __init__(self, names : list[str], actions : list[AutolatexCommand], args : list[str], commands : dict[str, AutolatexCommand]):
			super().__init__(args = names + args)
			self.__name = names[-1]
			self.__actions = actions
			self.__commands = commands

		@override
		def add_cli_positional_arguments(self, parser: argparse.ArgumentParser):
			self._create_cli_arguments_for_commands(self.__commands,  self.__name, '')

		@override
		def _run_program(self, cli_arguments : Namespace, positional_arguments: list[str], unknown_arguments: list[str]):
			for action in self.__actions:
				result = action.instance.run(cli_arguments)
				if not result:
					raise Exception("Failing command")

	COMMANDS : dict[str, AutolatexCommand] = AbstractAutoLaTeXMain.build_command_dict('autolatex2.cli.commands')

	def __init__(self, x, name : str):
		super().__init__(x)
		self.__command_name = name

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		extprint.IS_ACTIVATED = False

	def do_test(self, *args : str, config : Config | None = None, prefix_actions : list[str] | None = None):
		if prefix_actions:
			actions = prefix_actions + [self.__command_name]
		else:
			actions = [self.__command_name]
		actionnables = list()
		for action in actions:
			self.assertIn(action, AbstractCommandTest.COMMANDS, "Command not found for %s" % action)
			command = AbstractCommandTest.COMMANDS[action]
			self.assertIsNotNone(command, "Undefined command for %s" % action)
			actionnables.append(command)

		self.__main = AbstractCommandTest.InternalMainMock(actions, actionnables, list(args), AbstractCommandTest.COMMANDS)
		self.__main.exiter = AutoLaTeXExceptionExiter()
		if config is not None:
			self.__main.configuration = config
		self.__main.run()



if __name__ == '__main__':
	unittest.main()

