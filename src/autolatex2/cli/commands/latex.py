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
import logging
import os
from typing import override

from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.tex.utils import TeXWarnings, FileType
from autolatex2.utils import extlogging
import autolatex2.tex.utils as texutils
import autolatex2.utils.utilfunctions as genutils
from autolatex2.utils.i18n import T


# Extends MakerAction from images modules (alias extended_maker_action) in order
# to inherit the optional command line arguments from this super action.
class MakerAction(AbstractMakerAction):

	id : str = 'latex'

	alias : list[str] = ['tex', 'maketex']

	help : str = T('Performs actions to produce the output file from the (La)TeX document. This command does not call the TeX command in loop')

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
			help = T('Don\'t set the current directory of the application to document\'s root directory before the launch of the building process'))

		self.parse_cli.add_argument('--showneedloop',
			action='store_true',
			help = T('Show a message that is indicating if another run or the (La)TeX text processing was detected as needed to produce the target document'))

	# noinspection PyBroadException
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
		old_dir = os.getcwd()
		try:
			ddir = self.configuration.document_directory
			if ddir and not cli_arguments.nochdir:
				os.chdir(ddir)
			maker = self._internal_create_maker()
			for root_file in maker.root_files:
				try:
					maker.run_latex(root_file, loop=False)
				except BaseException as ex:
					extlogging.multiline_error(str(ex))
					return False
				if cli_arguments.showneedloop:
					log_file = FileType.log.ensure_extension(root_file)
					valid = True
					if os.path.isfile(log_file):
						try:
							warnings = set()
							with open(log_file, "r") as input_log:
								log_content = input_log.readline()
								while log_content:
									texutils.extract_tex_warning_from_line(log_content, warnings)
									log_content = input_log.readline()
							if warnings:
								all_msgs = ''
								for warning in warnings:
									if warning == TeXWarnings.undefined_reference:
										msg = T("a reference is undefined")
									elif warning == TeXWarnings.undefined_citation:
										msg = T("a citation is undefined")
									elif warning == TeXWarnings.multiple_definition:
										msg = T("multiple definition of the same reference")
									elif warning == TeXWarnings.multiple_definition:
										msg = T("a general warning leading to rebuild")
									else:
										raise Exception(T("Unexpected state detected from the log file"))
									if all_msgs:
										all_msgs = T("%s; %s") % (all_msgs, msg)
									else:
										all_msgs = msg
								logging.info(T("Rebuild is needed because: %s") % all_msgs)
							else:
								logging.info(T("Output file is up-to-date; No rebuild is needed"))
						except:
							valid = False
					else:
						valid = False
					if not valid:
						logging.error(T("Cannot determine if a rebuild is needed"))
						logging.error(T("File not found: %s") % log_file)
						return False
		finally:
			os.chdir(old_dir)
		return True

