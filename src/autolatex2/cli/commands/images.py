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
import gettext
from argparse import Namespace
from typing import override

from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.make.maker import AutoLaTeXMaker

_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id : str = 'images'

	help : str = _T('Performs the automatic generation of the figures based on the calls to the enabled translators')


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
			help=_T('Force the generation of the images even if the source image is not more recent than the generated image'))


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
		generated_images = self._internal_run_images(maker, cli_arguments)
		# Output the result of the command
		nb = 0
		if generated_images:
			for source,  target in generated_images.items():
				if target:
					nb = nb + 1
		if nb > 0:
			logging.info(_T("%d images were generated") % nb)
		else:
			logging.info(_T("All generated images are up-to-date"))
		return True
