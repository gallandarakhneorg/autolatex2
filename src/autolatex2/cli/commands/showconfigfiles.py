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
import logging
from argparse import Namespace
from typing import override

from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.utils.extprint import eprint
from autolatex2.utils.i18n import T


class MakerAction(AbstractMakerAction):

	id : str = 'showconfigfiles'

	help : str = T('Display the list of the detected configuration files that will be read by autolatex')

	@override
	def run(self, cli_arguments : Namespace) -> bool:
		"""
		Callback for running the command.
		:param cli_arguments: the succssfully parsed CLI arguments.
		:type cli_arguments: Namespace
		:return: True if the process could continue. False if an error occurred and the process should stop.
		:rtype: bool
		"""
		# noinspection DuplicatedCode
		system_path = self.configuration.system_config_file
		if system_path is not None:
			if os.path.isfile(system_path):
				if os.access(system_path, os.R_OK):
					eprint(system_path)
				else:
					logging.error(T("%s (unreadable)") % system_path)
			else:
				logging.error(T("%s (not found)") % system_path)

		#noinspection DuplicatedCode
		user_path = self.configuration.user_config_file
		if user_path is not None:
			if os.path.isfile(user_path):
				if os.access(user_path, os.R_OK):
					eprint(user_path)
				else:
					logging.error(T("%s (unreadable)") % user_path)
			else:
				logging.error(T("%s (not found)") % user_path)

		document_directory = self.configuration.document_directory
		if document_directory is None:
			logging.error(T("Cannot detect document directory"))
		else:
			doc_path = self.configuration.make_document_config_filename(document_directory)
			if doc_path is not None:
				if os.path.isfile(doc_path):
					if os.access(doc_path, os.R_OK):
						eprint(doc_path)
					else:
						logging.error(T("%s (unreadable)") % doc_path)
				else:
					logging.error(T("%s (not found)") % doc_path)

		return True
