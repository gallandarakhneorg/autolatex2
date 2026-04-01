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

"""
Abstract implementation of actions.
"""

from abc import ABC
import argparse
from argparse import Namespace
import logging
import os

from autolatex2.config.configobj import Config
from autolatex2.make.maker import AutoLaTeXMaker
import autolatex2.utils.utilfunctions as genutils
from autolatex2.tex.utils import FileType
from autolatex2.utils.runner import Runner
from autolatex2.utils.i18n import T


class AbstractMakerAction(ABC):
	"""
	Abstract implementation of a maker action/command.
	"""

	def __init__(self):
		self.__configuration = None
		self.__parse_cli = None

	@property
	def configuration(self) -> Config:
		"""
		Replies the configuration used by this action.
		:return: the configuration object.
		:rtype: Config
		"""
		return self.__configuration

	@property
	def parse_cli(self) -> argparse.ArgumentParser:
		"""
		Replies the tool for parsing the CLI arguments.
		:return: the CLI parser.
		:rtype: argparse.ArgumentParser
		"""
		return self.__parse_cli

	def _add_command_cli_arguments(self,  command_name : str, command_help : str | None,
								   command_aliases : list[str] | None):
		"""
		Callback for creating the CLI arguments (positional and optional).
		:param command_name: The name of the command.
		:type command_name: str
		:param command_help: The help text for the command.
		:type command_help: str | None
		"""
		pass

	def register_command(self,  sub_parsers : argparse._SubParsersAction, command_name : str,
						 command_help : str | None, command_aliases : list[str] | None, configuration : Config):
		"""
		Callback for creating the CLI arguments (positional and optional).
		:param sub_parsers: The argparse object container for the command
		:type sub_parsers: argparse.ArgumentParser
		:param command_name: The name of the command.
		:type command_name: str
		:param command_help: The help text for the command.
		:type command_help: str | None
		:param command_aliases: The list of alias for the command.
		:type command_aliases: list[str] | None
		:param configuration: The configuration instance.
		:type configuration: Config
		"""
		self.__configuration = configuration

		if command_aliases:
			cli = sub_parsers.add_parser(name=command_name, help=command_help,  aliases=command_aliases)
		else:
			cli = sub_parsers.add_parser(name=command_name, help=command_help)

		self.__parse_cli = cli
		self._add_command_cli_arguments(command_name, command_help, command_aliases)

	def run(self, cli_arguments : Namespace) -> bool:
		"""
		Callback for running the command.
		:param cli_arguments: the successfully parsed CLI arguments.
		:type cli_arguments: Namespace
		:return: True if the process could continue. False if an error occurred and the process should stop.
		:rtype: bool
		"""
		return True


	def _internal_create_maker(self) -> AutoLaTeXMaker:
		"""
		Create the maker.
		:return: the maker
		:rtype: AutoLaTeXMaker
		"""
		return AutoLaTeXMaker.create(self.configuration)


	# noinspection PyMethodMayBeStatic
	def _internal_run_images(self,  maker : AutoLaTeXMaker,  cli_arguments : Namespace) -> dict[str,str]:
		"""
		Run the internal behavior of the 'images' command.
		:param maker: the maker.
		:param cli_arguments: the arguments.
		:type cli_arguments: Namespace
		:return: the dictionary that maps the source image's filename to the generated image's filename.
		:rtype: dict[str,str]
		"""
		forced = cli_arguments.force if hasattr(cli_arguments, 'force') else False
		return maker.run_translators(force_generation=forced)


	def _internal_run_build(self, maker : AutoLaTeXMaker, cli_arguments : Namespace) -> bool:
		"""
		Run the internal behavior of the 'document' command.
		:param maker: the maker.
		:param cli_arguments: the arguments.
		:return: True to continue process. False to stop the process.
		"""
		old_dir = os.getcwd()
		try:
			ddir = self.configuration.document_directory
			nochdir = cli_arguments.nochdir if hasattr(cli_arguments, 'nochdir') else False
			if ddir and not nochdir:
				os.chdir(ddir)
			return maker.build()
		finally:
			os.chdir(old_dir)


	def _internal_run_viewer(self, maker : AutoLaTeXMaker, cli_arguments : Namespace) -> bool:
		"""
		Run the internal behavior of the 'view' command.
		:param maker: the maker.
		:param cli_arguments: the arguments.
		:return: True to continue process. False to stop the process.
		"""
		files = maker.root_files
		if not files:
			logging.error(T("Unable to find the name of the generated file for the viewer"))
			return False

		for input_file in files:
			if not input_file:
				logging.error(T("Unable to find the name of the generated file for the viewer"))
				return False

			out_file = genutils.basename2(input_file, *FileType.tex_extensions())
			if self.configuration.generation.pdf_mode:
				out_file += '.pdf'
			else:
				out_file += '.ps'
			logging.debug(T("VIEWER: %s") % out_file)

			cli = self.configuration.view.viewer_cli
			if not cli:
				logging.error(T("Unable to find the command-line for the viewing action. Did you set the configuration?"))
				return False

			cmd = list(cli)
			cmd.append(out_file)
			cmd = Runner.normalize_command(*cmd)
			if self.configuration.view.async_view:
				if not Runner.start_command_without_redirect(*cmd):
					return False
			else:
				if Runner.run_command_without_redirect(*cmd) != 0:
					return False
		return True
