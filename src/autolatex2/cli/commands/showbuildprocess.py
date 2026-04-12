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
from argparse import Namespace
from typing import override

from autolatex2.utils import extprint

from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.make.filedescription import FileDescription
from autolatex2.utils.i18n import T


class MakerAction(AbstractMakerAction):

	id : str = 'showbuildprocess'

	alias : list[str] = [ 'buildprocess', 'process' ]

	help : str = T('Show the list of actions that will be applied by AutoLaTeX for building. This command does not start the process')

	@override
	def run(self, cli_arguments : Namespace) -> bool:
		"""
		Callback for running the command.
		:param cli_arguments: the successfully parsed CLI arguments.
		:type cli_arguments: Namespace
		:return: True if the process could continue. False if an error occurred and the process should stop.
		:rtype: bool
		"""
		try:
			maker = self._internal_create_maker()
			for root_file in maker.root_files:
				logging.debug(T("Computing the file dependencies"))
				root_dep_file, dependencies = maker.compute_dependencies(root_file)
				logging.debug(T("Building the execution list"))
				build_list = maker.build_internal_execution_list(root_file=root_file,
																 root_pdf_file=root_dep_file,
																 dependencies=dependencies)
				self._show_build_list(build_list)
		except BaseException as ex:
			logging.error(str(ex))
			return False
		return True

	# noinspection PyMethodMayBeStatic
	def _show_build_list(self, build_list : list[FileDescription]):
		"""
		Show the build list.
		"""
		for build_file in build_list:
			extprint.eprint(f"[{build_file.file_type.name}] {build_file.input_filename} -> {build_file.output_filename}")
