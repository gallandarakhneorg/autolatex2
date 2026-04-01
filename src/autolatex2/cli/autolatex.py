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
from argparse import Namespace
from typing import override

from autolatex2.cli import exiters
from autolatex2.cli.abstract_main import AbstractAutoLaTeXMain
from autolatex2.utils.extlogging import ensure_autolatex_logging_levels
from autolatex2.utils.i18n import T


class AutoLaTeXMain(AbstractAutoLaTeXMain):
	"""
	Implementation of the standard autolatex tool.
	"""

	def __init__(self,  read_system_config : bool = True,  read_user_config : bool = True,
				 args : list[str] | None = None,  exiter : exiters.AutoLaTeXExiter | None = None):
		"""
		Constructor.
		:param read_system_config: Indicates if the system-level configuration must be read. Default is True.
		:type read_system_config: bool
		:param read_user_config: Indicates if the user-level configuration must be read. Default is True.
		:type read_user_config: bool
		:param args: List of command line arguments. If it is None, the system args are used.
		:type args: list
		:param exiter: The instance of the object that is called when the program should stop.
		:type exiter: exiters.AutoLaTeXExiter | None
		"""
		ensure_autolatex_logging_levels()
		super().__init__(read_system_config=read_system_config, read_user_config=read_user_config, args=args,  exiter=exiter)
		self.__commands = dict()

	@override
	def add_cli_options(self,  parser : argparse.ArgumentParser):
		"""
		Add the definition of the application CLI options.
		:param parser: the CLI parser
		:type parser: argparse.ArgumentParser
		"""
		async_group = self.cli_parser.add_argument_group(T('asynchronous behavior optional arguments'))

		outer : AutoLaTeXMain = self

		# --view
		# --noview
		class ViewAction(argparse.Action):
			@override
			def __call__(self, lparser, namespace, value, option_string=None):
				outer.configuration.view.view = self.const

		view_group = async_group.add_mutually_exclusive_group()

		view_group.add_argument('--view',
			action = ViewAction, 
			const = True,
			nargs = 0,
			help = T('Enable the document viewer at the end of the compilation'))

		view_group.add_argument('--noview',
			action = ViewAction, 
			const = False,
			nargs = 0,
			help = T('Disable the document viewer at the end of the compilation'))

		# --asyncview
		# --noasyncview
		async_view_group = async_group.add_mutually_exclusive_group()

		class AsyncViewAction(argparse.Action):
			@override
			def __call__(self, lparser, namespace, value, option_string=None):
				outer.configuration.view.async_view = self.const

		async_view_group.add_argument('--asyncview',
			action = AsyncViewAction,
			const = True,
			nargs = 0,
			help = T('Enable the asynchronous launching of the viewer'))

		async_view_group.add_argument('--noasyncview',
			action = AsyncViewAction,
			const = False,
			nargs = 0,
			help = T('Disable the asynchronous launching of the viewer'))

		# --continuous
		# --nocontinuous
		continuous_group = async_group.add_mutually_exclusive_group()

		class ContinuousAction(argparse.Action):
			# noinspection PyBroadException
			@override
			def __call__(self, lparser, namespace, value, option_string=None):
				outer.configuration.infiniteLoop = True
				if value:
					try:
						outer.configuration.infinite_loop_delay = int(value)
					except:
						pass

		continuous_group.add_argument('--continuous',
			action = ContinuousAction, 
			nargs = '?', 
			metavar = 'SECONDS',
			help = T('Do not stop AutoLaTeX, and continually do the action(s) given as parameter(s). If SECONDS is specified, it is the delay to wait for between two runs of AutoLaTeX'))

		class NoContinuousAction(argparse.Action):
			@override
			def __call__(self, lparser, namespace, value, option_string=None):
				outer.configuration.infinite_loop = False

		continuous_group.add_argument('--nocontinuous', 
			action = NoContinuousAction,
			nargs = 0, 
			help = T('Disable continuous execution of AutoLaTeX'))


	@override
	def add_cli_positional_arguments(self,  parser : argparse.ArgumentParser):
		"""
		Add the definition of the application CLI positional arguments.
		:param parser: the CLI parser
		:type parser: argparse.ArgumentParser
		"""
		self.__commands = self.build_command_dict('autolatex2.cli.commands')
		if self.__commands:
			if self.configuration.default_cli_action:
				help_msg = T('Command to be run by autolatex, by default \'%s\'. Available commands are:') % self.configuration.default_cli_action
			else:
				help_msg = T('Command to be run by autolatex. Available commands are:')
			self._create_cli_arguments_for_commands(commands=self.__commands, title=T("commands"), help_text=help_msg)



	@override
	def _pre_run_program(self, strict_arguments : bool) -> tuple[Namespace,list[str],list[str]]:
		"""
		Run the general behavior of the main program before the specific behavior related to commands.
		:param strict_arguments: Indicates if only the arguments from the main script and the associated commands are
		allowed. If True, the CLI arguments are parsed strictly and if an argument is not known, there is a failure.
		If False, the function doers not fail if it is encountering an unknown argument.
		:type strict_arguments: bool
		:return: the tuple with as first element the parsed CLI arguments (argparse namespace), the actions , and the second element the list of unknown arguments.
		:rtype: tuple[Namespace,list[str],list[str]]
		"""
		cli_arguments, positional_arguments, unknown_arguments = super()._pre_run_program(strict_arguments)

		if not self.configuration.document_filename:
			self.configuration.document_filename = AbstractAutoLaTeXMain._detect_tex_file(self.configuration.document_directory)
		
		return cli_arguments, positional_arguments, unknown_arguments

	@override
	def _run_program(self, cli_arguments : Namespace, positional_arguments: list[str], unknown_arguments: list[str]):
		"""
		Run the specific behavior.
		:param cli_arguments: the argparse object that contains the CLI arguments successfully parsed.
		:type cli_arguments: Namespace
		:param positional_arguments: the CLI arguments that are not consumed by the argparse library.
		:type positional_arguments: list[str]
		:param unknown_arguments: the list of the unsupported arguments.
		:type unknown_arguments: list[str]
		"""
		self._execute_commands(positional_arguments, self.__commands, cli_arguments)


def main():
	"""
	Main program for the autolatex tool.
	"""
	main_program = AutoLaTeXMain()
	main_program.run()

if __name__ == '__main__':
	main()
