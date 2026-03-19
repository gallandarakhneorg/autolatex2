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

from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.tex.flattener import Flattener
import autolatex2.utils.utilfunctions as genutils

import gettext
_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id : str = 'makeflat'
	
	alias : str = 'preparepublish'

	help : str = _T('Create a version of the document inside the specified directory (by default \'flat_version\') in which there is a single TeX file, and '
					+ 'all the other files are inside the same directory of the TeX file. This action is helpful to create a version of the document that may '
					+ 'be directly upload on online publisher sites (such as Elsevier). This command runs \'document\' before creating the new version of the '
					+ 'document. Also, the bibliography entries are extracted from the BibTeX files to be inlined into the generated TeX file')

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
		self.parse_cli.add_argument('--externalbiblio',
			action='store_true', 
			help=_T('Force the use of an external BibTeX file (i.e. \'.bib\' file) instead of inlining the bibliography database inside the TeX file'))

		self.parse_cli.add_argument('--out',
			default='flat_version', 
			metavar=('DIRECTORY'), 
			help=_T('Specify the output directory in which the flat version is created. By default, the name of the directory is \'flat_version\''))


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

		for root_file in maker.root_files:
			root_dir = os.path.dirname(root_file)
			# Output
			output_dir = genutils.abs_path(cli_arguments.out, root_dir)
			
			logging.debug(_T("Generating flat version into: %s") % output_dir)

			# Delete the output directory
			try:
				if os.path.isdir(output_dir):
					shutil.rmtree(output_dir)
			except BaseException as ex:
				logging.error(_T("Unable to delete the output folder %s: %s") % (output_dir, str(ex)))
				return False

			# Create the flattening tool
			flattener = Flattener(filename=root_file, output_directory=output_dir)
			flattener.use_biblio = cli_arguments.externalbiblio
			if not flattener.run():
				return False

		return True
