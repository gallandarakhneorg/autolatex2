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

import os
from argparse import Namespace
from typing import override

import autolatex2.utils.utilfunctions as genutils
import autolatex2.tex.utils as texutils
from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.utils.i18n import T
from autolatex2.utils import extlogging

class MakerAction(AbstractMakerAction):

	id : str = 'index'

	alias : str = 'makeindex'

	help : str = T('Performs all processing that permits to generate the index (makeindex)')

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
		self.parse_cli.add_argument('--nochdir',
			action = 'store_true', 
			help = T('Don\'t set the current directory of the application to document\'s root directory before the launch of the building process'))

	@override
	def run(self, cli_arguments : Namespace) -> bool:
		"""
		Callback for running the command.
		:param cli_arguments: the successfully parsed CLI arguments.
		:type cli_arguments: Namespace
		:return: True if the process could continue. False if an error occurred and the process should stop.
		:rtype: bool
		"""
		old_dir = os.getcwd()
		try:
			ddir = self.configuration.document_directory
			if ddir and not cli_arguments.nochdir:
				os.chdir(ddir)
			maker = self._internal_create_maker()
			idx_ext = texutils.get_index_file_extensions()[0]
			for root_file in maker.root_files:
				idx_file = genutils.basename2(root_file,  *texutils.get_tex_file_extensions()) + idx_ext
				result = maker.run_makeindex(idx_file)
				if result is not None:
					exit_code, sout, serr = result
					if exit_code != 0:
						message = (sout or '') + (serr or '')
						extlogging.multiline_error(T("Error when running the indexing tool: %s") % message)
						return False
		finally:
			os.chdir(old_dir)
		return True
