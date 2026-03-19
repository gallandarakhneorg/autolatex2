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

import gettext
_T = gettext.gettext

# Extends MakerAction from images modules (alias extended_maker_action) in order
# to inherit the optional command line arguments from this super action.
class MakerAction(AbstractMakerAction):

	id : str = 'document'

	alias : str = 'gen_doc'

	help : str = _T('Performs all processing actions that are required to produce the PDF, DVI or Postscript. The actions set includes LaTeX, BibTeX, Makeindex, Dvips, etc. This action does not includes the generated of images.')

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
		super()._add_command_cli_arguments(command_name, command_help, command_aliases)

		self.parse_cli.add_argument('--nochdir', 
			action = 'store_true', 
			help=_T('Don\'t set the current directory of the application to document\'s root directory before the launch of the building process'))

	@override
	def run(self, cli_arguments : Namespace) -> bool:
		"""
		Callback for running the command.
		:param cli_arguments: the successfully parsed CLI arguments.
		:type cli_arguments: Namespace
		:return: True if the process could continue. False if an error occurred and the process should stop.
		:rtype: bool
		"""
		#
		# DANGER: Do not call the super.run() function because it has not the expected behavior for the current command.
		#
		# Create the maker
		maker = self._internal_create_maker()
		return self._internal_run_build(maker,  cli_arguments)

