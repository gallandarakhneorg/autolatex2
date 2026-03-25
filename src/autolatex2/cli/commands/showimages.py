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

from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.translator.translatorrepository import TranslatorRepository
from autolatex2.translator.translatorrunner import TranslatorRunner
from autolatex2.utils.extprint import eprint
import autolatex2.utils.utilfunctions as genutils
from autolatex2.utils.i18n import T


class MakerAction(AbstractMakerAction):

	id : str = 'showimages'

	help : str = T('Display the filenames of the figures that are automatically generated')

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
		output_group = self.parse_cli.add_mutually_exclusive_group()

		output_group.add_argument('--changed',
			action = 'store_true',
			dest = 'show_changed_images',
			help = T('Show only the images for which the generated files are not up-to-date'))

		output_group.add_argument('--translators',
			action = 'store_true',
			dest = 'show_image_translators',
			help = T('Show the names of the translators that is associated to each of the images'))

		output_group.add_argument('--valid',
			action = 'store_true',
			dest = 'show_valid_images',
			help = T('Show only the images for which the generated files are up-to-date'))


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
		# Create the runner of translators
		runner = TranslatorRunner(repository)
		# Detect the images
		runner.sync()
		images = runner.get_source_images()
		# Show detect images
		ddir = self.configuration.document_directory
		image_list : dict[str,str] = dict()
		if ddir:
			for image in images:
				relpath = os.path.relpath(image,  ddir)
				abspath = genutils.abs_path(image,  ddir)
				image_list[abspath] = relpath
		else:
			for image in images:
				relpath = os.path.relpath(image)
				abspath = os.path.abspath(image)
				image_list[abspath] = relpath
		
		if cli_arguments.show_valid_images:
			self._show_valid_images(image_list, runner)
		elif cli_arguments.show_changed_images:
			self._show_changed_images(image_list, runner)
		elif cli_arguments.show_image_translators:
			self._show_image_translators(image_list, runner)
		else:
			self._show_all_images(image_list)
		return True

	# noinspection PyMethodMayBeStatic
	def _show_all_images(self,  image_list : dict[str,str]):
		sorted_dict = {k: image_list[k] for k in sorted(image_list)}
		for abspath, relpath in sorted_dict.items():
			eprint(relpath)

	# noinspection PyMethodMayBeStatic
	def _show_image_translators(self,  image_list : dict[str,str], runner : TranslatorRunner):
		sorted_dict = {k: image_list[k] for k in sorted(image_list)}
		for abspath, relpath in sorted_dict.items():
			translator = runner.get_translator_for(abspath)
			if translator:
				eprint(T("%s => %s") % (relpath, translator.name))

	def _show_changed_images(self,  image_list : dict[str,str], runner : TranslatorRunner):
		sorted_dict = {k: image_list[k] for k in sorted(image_list)}
		for abspath, relpath in sorted_dict.items():
			if not self._is_valid_image(abspath, runner):
				eprint(relpath)

	def _show_valid_images(self,  image_list : dict[str,str], runner : TranslatorRunner):
		sorted_dict = {k: image_list[k] for k in sorted(image_list)}
		for abspath, relpath in sorted_dict.items():
			if self._is_valid_image(abspath,  runner):
				eprint(relpath)

	# noinspection PyMethodMayBeStatic
	def _is_valid_image(self,  image : str, runner : TranslatorRunner) -> bool:
			in_change = genutils.get_file_last_change(image)
			target_files = runner.get_target_files(in_file=image)
			if target_files:
				for target_file in target_files:
					out_change = genutils.get_file_last_change(target_file)
					if out_change is None or out_change < in_change:
						return False
				return True
			else:
				return False
