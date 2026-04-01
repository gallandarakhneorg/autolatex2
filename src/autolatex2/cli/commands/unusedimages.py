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
from autolatex2.tex.imageinclusions import ImageInclusions
from autolatex2.utils.extprint import eprint
import autolatex2.utils.utilfunctions as genutils
from autolatex2.utils.i18n import T


class MakerAction(AbstractMakerAction):

	id : str = 'unusedimages'

	help : str = T('Display (or remove) the figures that are inside the document folder and not included into the document')

	IMAGE_FORMATS : list[str] = ['.png', '.jpeg', '.jpg', '.eps', '.ps', '.pdf', '.gif', '.bmp', '.tiff', '.pdftex_t', '.pstex_t', '.pdf_tex', '.ps_tex']

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
		self.parse_cli.add_argument('--delete',
			action = 'store_true',
			help = T('Delete the unused figures instead of simply listing them'))


	# noinspection PyMethodMayBeStatic
	def _is_picture(self, filename : str) -> bool:
		"""
		Replies if the given filename is for an image and not compressed image.
		:param filename: the filename.
		:return: True if the filename corresponds to an image.
		"""
		lower_image = filename.lower()
		for ext in MakerAction.IMAGE_FORMATS:
			if lower_image.endswith(ext):
				return True
		return False


	def _is_auto_figure_folder(self,  name : str) -> bool:
		"""
		:param name: the filename
		:return: True if the given filename is inside the figure folder or one of its subfolders.
		"""
		# Smooth out relative path names. Note: if you are concerned about symbolic links, you should use os.path.realpath too
		simple_name = os.path.abspath(name)
		for root in self.configuration.translators.image_paths:
			parent = os.path.abspath(root)
			# Compare the common path of the parent and child path with the common path of just the parent path.
			# Using the commonpath method on just the parent path will regularize the path name in the same way
			# as the comparison that deals with both paths, removing any trailing path separator
			if os.path.commonpath([parent]) == os.path.commonpath([parent, simple_name]):
				return True
		return False


	def _get_manually_given_images(self,  auto_images : set) -> set[str]:
		"""
		Replies the list of images that are not automatically generated.
		:param auto_images: The list of images that are generated and not provided manually.
		:type auto_images: set[str]
		:return: The set of image filenames
		:rtype: set[str]
		"""
		manual_images = set()
		for root, dirs, files in os.walk(self.configuration.document_directory):
			for basename in files:
				full_name = str(os.path.join(root,  basename))
				if self._is_picture(full_name) and full_name not in auto_images:
					manual_images.add(full_name)
		return manual_images


	def _get_auto_images(self) -> set[str]:
		"""
		Replies the list of images that are automatically generated and that already exist on the file system.
		:return: The set of image filenames
		:rtype: set[str]
		"""
		# Explore the auto-generated images
		repository = TranslatorRepository(self.configuration)
		# Create the runner of translators
		runner = TranslatorRunner(repository)
		# Detect the images
		runner.sync()
		# Detect the target images
		auto_images = runner.get_source_images()
		target_images = set()
		for image in auto_images:
			targets = runner.get_target_files(in_file = image)
			target_images.update(targets)
		return target_images


	@override
	def run(self, cli_arguments : Namespace) -> bool:
		"""
		Callback for running the command.
		:param cli_arguments: the successfully parsed CLI arguments.
		:type cli_arguments: Namespace
		:return: True if the process could continue. False if an error occurred and the process should stop.
		:rtype: bool
		"""
		# Explore the auto-generated images
		auto_images = self._get_auto_images()

		# Explore the folders
		manual_images = self._get_manually_given_images(auto_images)
		
		# Parse the TeX
		maker = self._internal_create_maker()

		included_images = set()
		for root_file in maker.root_files:
			parser = ImageInclusions(filename=root_file,
									 include_extra_macros=self.configuration.generation.include_extra_macros)
			if not parser.run():
				return False
			images = parser.get_included_figures()
			included_images.update(images)
		
		# Compute the not-included figures
		not_included_images = manual_images.difference(included_images)
		
		# Do the action
		ddir = self.configuration.document_directory
		for image_file in not_included_images:
			relpath = os.path.relpath(image_file,  ddir)
			abspath = genutils.abs_path(image_file,  ddir)
			eprint(relpath)
			if cli_arguments.delete:
				#eprint("> " + abspath)
				genutils.unlink(abspath)

		return True

