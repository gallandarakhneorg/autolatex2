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
from argparse import Namespace
from typing import override

from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.config.configwriter import OldStyleConfigWriter
import autolatex2.utils.utilfunctions as genutils
from autolatex2.utils.i18n import T

class MakerAction(AbstractMakerAction):

	id : str = 'createconfig'

	help : str = T('Create a configuration file. The configuration file is \'.autolatex_project.cfg\' on Unix and \'autolatex_project.cfg\' on other platforms. '
		'The content of the configuration file depends on the current state of the configuration')

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
			help = T('Force to overwrite the configuration file if it exists'))


	@override
	def run(self, cli_arguments : Namespace) -> bool:
		"""
		Callback for running the command.
		:param cli_arguments: the succssfully parsed CLI arguments.
		:type cli_arguments: Namespace
		:return: True if the process could continue. False if an error occurred and the process should stop.
		:rtype: bool
		"""
		out_directory = self.configuration.document_directory
		out_file = self.configuration.make_document_config_filename(out_directory)
		if os.path.isfile(out_file) and not cli_arguments.force:
			logging.error(T("File already exists: %s") % out_file)
			return False
		writer = OldStyleConfigWriter()
		try:
			logging.info(T("Creating configuration file %s") % out_file)
			genutils.unlink(out_file)
			os.makedirs(out_directory, exist_ok=True)
			writer.write(out_file, self.configuration)
			return True
		except BaseException as ex:
			logging.error(str(ex))
			return False
