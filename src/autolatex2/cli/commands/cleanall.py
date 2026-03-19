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

from autolatex2.cli.commands.clean import MakerAction as CleanMakerAction

import gettext
_T = gettext.gettext

class MakerAction(CleanMakerAction):

	id : str = 'cleanall'
	
	alias : list[str] = ['mrproper']

	help : str = _T('Extend the \'clean\' command by removing the backup files and the automatically generated images')

	@override
	def run(self, cli_arguments : Namespace) -> bool:
		"""
		Callback for running the command.
		:param cli_arguments: the successfully parsed CLI arguments.
		:type cli_arguments: Namespace
		:return: True if the process could continue. False if an error occurred and the process should stop.
		:rtype: bool
		"""
		self.__nb_deletions = 0
		if not self.run_clean_command(cli_arguments):
			return False
		if not self.run_cleanall_command(cli_arguments):
			return False
		self._show_deletions_message(cli_arguments)
		return True
