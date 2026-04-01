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

from argparse import Namespace
from typing import override

from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.make.maker import AutoLaTeXMaker
from autolatex2.utils.i18n import T


# Extends MakerAction from view module (alias extended_maker_action) in order
# to inherit from this super action.
class MakerAction(AbstractMakerAction):

	id : str = 'build'

	alias : list[str] = [ 'default', 'all' ]

	help : str = T('Performs all processing actions that are required to produce the PDF, DVI or Postscript and to view it with the specified PDF viewer if this option was enabled')

	@override
	def _add_command_cli_arguments(self, command_name : str, command_help : str | None,
								   command_aliases : list[str] | None):
		"""
		Callback for creating the CLI arguments (positional and optional).
		:param command_name: The name of the command.
		:type command_name: str
		:param command_help: The help text for the command.
		:type command_help: str | None
		"""
		self.parse_cli.add_argument('--force',
			action = 'store_true',
			help = T('Force the generation of the images even if the source image is not more recent than the generated image'))

		self.parse_cli.add_argument('--nochdir',
			action = 'store_true',
			help = T('Don\'t set the current directory of the application to document\'s root directory before the launch of the building process'))

		self.parse_cli.add_argument('--noauxfileread',
			action='store_true',
			help=T('Don\'t read the content of the auxiliary files for determining if they contain bibliography citations'))


	@override
	def run(self, cli_arguments : Namespace) -> bool:
		"""
		Callback for running the command.
		:param cli_arguments: the successfully parsed CLI arguments.
		:type cli_arguments: Namespace
		:return: True if the process could continue. False if an error occurred and the process should stop.
		:rtype: bool
		"""
		maker = self._internal_create_maker()
		self._internal_run_images(maker, cli_arguments)
		if self._internal_run_build(maker, cli_arguments):
			return self._internal_run_viewer(maker, cli_arguments)
		return False


	def _internal_run_viewer(self, maker : AutoLaTeXMaker, cli_arguments : Namespace) -> bool:
		"""
		Run the internal behavior of the 'view' command.
		:param maker: the maker.
		:param cli_arguments: the arguments.
		:return: True to continue process. False to stop the process.
		"""
		if self.configuration.view.view:
			return super()._internal_run_viewer(maker,  cli_arguments)
		return True
