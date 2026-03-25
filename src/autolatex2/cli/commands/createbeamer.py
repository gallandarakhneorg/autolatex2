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
import shutil
from argparse import Namespace
from typing import override

import autolatex2.utils.utilfunctions as genutils
from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.utils.i18n import T

class MakerAction(AbstractMakerAction):

	id : str = 'createbeamer'

	help : str = T('Create LaTeX style file into the document directory that provides the standard AutoLaTeX control sequences for the LaTeX Beamer library. The created file will be named \'autolatex-beamer.sty\'. If a file with this name already exists, it may be overwritten')

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
			help=T('Force to overwrite the STY file if it exists'))

	@override
	def run(self, cli_arguments : Namespace) -> bool:
		"""
		Callback for running the command.
		:param cli_arguments: the succssfully parsed CLI arguments.
		:type cli_arguments: Namespace
		:return: True if the process could continue. False if an error occurred and the process should stop.
		:rtype: bool
		"""
		in_file = self.configuration.get_system_beamer_sty_file()
		out_directory = self.configuration.document_directory
		out_file = os.path.join(out_directory,  'autolatex-beamer.sty')
		if os.path.isfile(out_file) and not cli_arguments.force:
			logging.error(T("File already exists: %s") % out_file)
			return False
		try:
			logging.info(T("Copying %s to %s") % (in_file,  out_file))
			genutils.unlink(out_file)
			os.makedirs(out_directory, exist_ok=True)
			shutil.copyfile(in_file,  out_file)
			return True
		except object as ex:
			logging.error(str(ex))
			return False
