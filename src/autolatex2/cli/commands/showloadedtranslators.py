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
from typing import override, Callable

from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.config.translator import TranslatorLevel
from autolatex2.translator.translatorrepository import TranslatorRepository
from autolatex2.utils.extprint import eprint

import gettext
_T = gettext.gettext

class MakerAction(AbstractMakerAction):

	id : str = 'showloadedtranslators'

	alias : str = 'translators'

	help : str = _T('Display the list of the loaded translators and their highest loading levels')

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
		level_group = self.parse_cli.add_mutually_exclusive_group()

		level_group.add_argument('--level',
			action='store_true',
			default=True, 
			dest='show_activation_translator_level',
			help=_T('Show the activation level for each translator'))

		level_group.add_argument('--nolevel',
			action='store_false',
			dest='show_activation_translator_level',
			help=_T('Hide the activation level for each translator'))


	@override
	def run(self, cli_arguments : Namespace) -> bool:
		"""
		Callback for running the command.
		:param cli_arguments: the successfully parsed CLI arguments.
		:type cli_arguments: Namespace
		:return: True if the process could continue. False if an error occurred and the process should stop.
		:rtype: bool
		"""
		# Create the translator repository
		repository = TranslatorRepository(self.configuration)
		# Detect the translators
		repository.sync(False)
		# Get translator status
		inclusions = repository.get_included_translators_with_levels()
		# Show the list
		if cli_arguments.show_activation_translator_level:
			self._show_inclusions(inclusions)
		else:
			self._show_inclusion_names_only(inclusions)
		return True

	def _show_inclusions(self,  all_inclusions : dict[str,TranslatorLevel]):
		"""
		Show the included translators with the associated inclusion levels.
		:param all_inclusions: the collection of included translators
		:return: dict[str,TranslatorLevel]
		"""
		self.__show_inclusions(all_inclusions, lambda a, b: _T("%s = %s") % (a,  b))

	def _show_inclusion_names_only(self,  all_inclusions : dict[str,TranslatorLevel]):
		"""
		Show the included translators without the associated inclusion levels.
		:param all_inclusions: the collection of included translators
		:return: dict[str,TranslatorLevel]
		"""
		self.__show_inclusions(all_inclusions, lambda a, b: a)

	def __show_inclusions(self,  all_inclusions : dict[str,TranslatorLevel], label : Callable[[str,str],str]):
		"""
		Show the included translators without the associated inclusion levels.
		:param all_inclusions: the collection of included translators
		:return: dict[str,TranslatorLevel]
		:param label: the lambda for building the label to be printed out.
		:type label: Callable[[str,str],str]
		"""
		sorted_dict = {k: all_inclusions[k] for k in sorted(all_inclusions)}
		for translator_name,  level in sorted_dict.items():
			eprint(label(translator_name, str(level)))
