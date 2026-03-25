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
import textwrap
from argparse import Namespace
from typing import override

from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.config.configobj import Config
from autolatex2.config.configwriter import OldStyleConfigWriter
from autolatex2.utils.i18n import T

class MakerAction(AbstractMakerAction):

	id : str = 'init'

	help : str = T('Create an empty LaTeX document that is following a standard folder structure suitable for AutoLaTeX')

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
			help = T('Force to overwrite any existing file'))
		self.parse_cli.add_argument('--out',
			action = 'store', 
			default = None, 
			type=str, 
			help = T('Specify the output directory for creating the project structure'))


	@override
	def run(self, cli_arguments : Namespace) -> bool:
		"""
		Callback for running the command.
		:param cli_arguments: the successfully parsed CLI arguments.
		:type cli_arguments: Namespace
		:return: True if the process could continue. False if an error occurred and the process should stop.
		:rtype: bool
		"""
		if cli_arguments.out:
			out_directory = os.path.abspath(cli_arguments.out)
		else:
			out_directory = os.getcwd()

		cfg = Config()

		tex_file = os.path.join(out_directory,  'main.tex')
		if os.path.isfile(tex_file) and not cli_arguments.force:
			logging.error(T("TeX file already exists: %s") % tex_file)
			return False

		cfg.document_directory = os.path.dirname(tex_file)
		cfg.document_filename= os.path.basename(tex_file)
		tex_file_content = textwrap.dedent("""\
			\\documentclass{article}
			\\begin{document}
			\\end{document}
			""")

		local_image_directory = os.path.join('images',  'auto')
		image_directory = os.path.join(out_directory,  local_image_directory)
		cfg.translators.add_image_path(image_directory)

		cfg_file = cfg.make_document_config_filename(out_directory)
		if os.path.isfile(cfg_file) and not cli_arguments.force:
			logging.error(T("Configuration file already exists: %s") % cfg_file)
			return False
	
		gitignore_file = os.path.join(out_directory,  '.gitignore')
		if os.path.isfile(gitignore_file) and not cli_arguments.force:
			logging.error(T("Git-ignore file already exists: %s") % gitignore_file)
			return False

		excl1 = os.path.join('*',  local_image_directory,  '*.pdf')
		excl2 = os.path.join('*',  local_image_directory,  '*', '*.pdf')
		gitignore_file_content = textwrap.dedent("""\
			.autolatex_stamp
			*.aux
			*.log
			*.nav
			*.out
			*.pdf
			*.snm
			*.synctex
			*.synctex.gz
			*.toc
			*.vrb
			*.bbl
			*.blg
			%s
			%s
			*.pdftex_t
		""") % (excl1,  excl2)

		logging.info(T("Creating document structure in %s") % out_directory)
		try:
			# Create the folders
			os.makedirs(image_directory, exist_ok=True)
			# Create the TeX file
			with open(tex_file,  'w') as file:
				file.write(tex_file_content)
			# Git ignore
			if os.path.isfile(gitignore_file):
				logging.warning(T('Ignore file that already exists: %s') % gitignore_file)
			else:
				with open(gitignore_file,  'w') as file:
					file.write(gitignore_file_content)
			# Create the configuration file
			writer = OldStyleConfigWriter()
			writer.write(cfg_file,  cfg)
		except BaseException as ex:
			logging.error(str(ex))
			return False
		return True
