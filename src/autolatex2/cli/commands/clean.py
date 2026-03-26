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
import re
import fnmatch
from argparse import Namespace
from typing import override

from autolatex2.cli.abstract_actions import AbstractMakerAction
import autolatex2.utils.utilfunctions as genutils
import autolatex2.tex.utils as texutils
from autolatex2.translator.translatorrepository import TranslatorRepository
from autolatex2.translator.translatorrunner import TranslatorRunner
from autolatex2.utils.i18n import T, TT

class MakerAction(AbstractMakerAction):

	id : str = 'clean'

	help : str = T('Clean the current working directory by removing all LaTeX temp files and other temp files that are created during the processing of the document')

	CLEANABLE_FILE_EXTENSIONS : list[str] = [
		'.aux',
		'.bcf',
		'.bbl',
		'.blg',
		'.bmt',
		'.brf',
		'.cb', 
		'.fls',
		'.glg',
		'.glo',
		'.gls',
		'.idx',
		'.ilg',
		'.ind', 
		'.lbl',
		'.loa',
		'.loc',
		'.loe',
		'.lof', 
		'.log', 
		'.lom', 
		'.los', 
		'.lot',
		'.maf',
		'.mtc',
		'.mtf',
		'.mtl',
		'.nav',
		'.out', 
		'.run.xml', 
		'.snm',
		'.soc',
		'.spl',
		'.thlodef',
		'.tmp', 
		'.toc', 
		'.vrb',
		'.xdy', 
	]

	CLEANABLE_FILE_PATTERNS : list[str] = [
		'\\.goutputstream-.+',
		'\\.mtc[0-9]+',
		'\\.mtf[0-9]+',
		'\\.mtl[0-9]+',
	]

	ANYWHERE_CLEANABLE_FILE_EXTENSIONS : list[str] = [
		'~',
		'.back',
		'.backup',
		'.bak',
	]

	def __init__(self):
		super().__init__()
		self.__nb_deletions = 0

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
		self.parse_cli.add_argument('--nochdir',
			action = 'store_true', 
			help = T('Don\'t set the current directory of the application to document\'s root directory before the launch of the building process'))

		self.parse_cli.add_argument('--norecursive',
			action = 'store_true', 
			help = T('Disable cleaning of the subfolders'))

		self.parse_cli.add_argument('--simulate',
			action = 'store_true', 
			help = T('Simulate the removal of the files, i.e. the files are not removed from the disk'))

		if command_name == 'clean':
			self.parse_cli.add_argument('--all',
				action = 'store_true', 
				help = T('If specified, the cleaning command behaves as the command \'cleanall\''))


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
		if cli_arguments.all:
			if not self.run_cleanall_command(cli_arguments):
				return False
		self._show_deletions_message(cli_arguments)
		return True


	def _delete_file(self,  filename : str,  simulate : bool):
		if simulate:
			msg = T("Selecting: %s") % filename
		else:
			msg = T("Deleting: %s") % filename
		logging.info(msg)
		if not simulate:
			genutils.unlink(filename)
		self.__nb_deletions = self.__nb_deletions + 1


	def run_clean_command(self, cli_arguments : Namespace) -> bool:
		"""
		Run the command 'clean'.
		:param cli_arguments: the arguments.
		:return: True if the process could continue. False if an error occurred and the process should stop.
		"""
		old_dir = os.getcwd()
		try:
			ddir = self.configuration.document_directory
			if ddir and not cli_arguments.nochdir:
				os.chdir(ddir)
			maker = self._internal_create_maker()
			# Prepare used-defined list of deletable files
			clean_files = self.configuration.clean.clean_files
			abs_clean_files = list()
			bn_clean_files = list()
			for file in clean_files:
				if os.sep in file:
					abs_clean_files.append(file)
				else:
					bn_clean_files.append(file)
			for root_file in maker.root_files:
				root_dir = os.path.dirname(root_file)
				if cli_arguments.norecursive:
					root = os.path.dirname(root_file)
					for filename in os.listdir(root):
						abs_filename = os.path.normpath(os.path.join(root, filename))
						if self._is_deletable_in_root_folder_only(root, root_file, abs_filename)\
								or self._is_deletable_from_constants(abs_filename)\
								or self._is_deletable_shell(abs_filename, filename, abs_clean_files, bn_clean_files):
							self._delete_file(abs_filename, cli_arguments.simulate)
				else:
					for root, dirs, files in os.walk(os.path.dirname(root_file)):
						for filename in files:
							abs_filename = os.path.normpath(os.path.join(root,  filename))
							if (root == root_dir and self._is_deletable_in_root_folder_only(root, root_file, abs_filename))\
									or self._is_deletable_from_constants(abs_filename)\
									or self._is_deletable_shell(abs_filename, filename, abs_clean_files, bn_clean_files):
								self._delete_file(abs_filename, cli_arguments.simulate)
		finally:
			os.chdir(old_dir)
		return True

	# noinspection PyMethodMayBeStatic
	def _is_deletable_anywhere(self, filename : str) -> bool:
		"""
		Replies if the given filename is for a deletable file anywhere.
		"""
		fnl = filename.lower() if os.name == 'nt' else filename
		for ext in MakerAction.ANYWHERE_CLEANABLE_FILE_EXTENSIONS:
			if fnl.endswith(ext):
				return True
		return False


	# noinspection PyMethodMayBeStatic
	def _is_deletable_in_root_folder_only(self,  root_dir : str,  tex_filename : str,  filename : str) -> bool:
		"""
		Replies if the given filename is for a deletable file in the root folder.
		"""
		basename = genutils.basename2(os.path.join(root_dir,  tex_filename), *texutils.get_tex_file_extensions())
		candidates = [
			os.path.normpath(os.path.join(root_dir, '.autolatex_stamp')),
			os.path.normpath(os.path.join(root_dir, 'autolatex_stamp')),
			os.path.normpath(os.path.join(root_dir, 'autolatex_exec_stderr.log')),  # For old version of AutoLaTeX
			os.path.normpath(os.path.join(root_dir, 'autolatex_exec_stdout.log')), # For old version of AutoLaTeX
			os.path.normpath(os.path.join(root_dir, 'autolatex_exec_stdin.log')), # For old version of AutoLaTeX
			os.path.normpath(os.path.join(root_dir, 'autolatex_autogenerated.tex')),
			basename + ".pdf",
			basename + ".dvi",
			basename + ".xdvi",
			basename + ".xdv",
			basename + ".ps",
			basename + ".synctex.gz",
			basename + ".synctex",
		]
		return filename in candidates


	# noinspection PyMethodMayBeStatic
	def _is_deletable_from_constants(self, filename : str) -> bool:
		"""
		Replies if the given filename is for a deletable file anywhere.
		"""
		fnl = filename.lower() if os.name == 'nt' else filename
		for ext in MakerAction.CLEANABLE_FILE_EXTENSIONS:
			if fnl.endswith(ext):
				return True
		for ext in MakerAction.CLEANABLE_FILE_EXTENSIONS:
			if re.match(ext + '$',  fnl):
				return True
		return False


	# noinspection PyMethodMayBeStatic
	def _is_deletable_shell(self,
							filename : str,
							basename : str,
							absolute_shell_patterns : list[str],
							basename_shell_patterns : list[str]) -> bool:
		"""
		Replies if the given filename shell pattern is for a deletable file anywhere.
		"""
		for pattern in absolute_shell_patterns:
			if fnmatch.fnmatch(filename,  pattern):
				return True
		for pattern in basename_shell_patterns:
			if fnmatch.fnmatch(basename,  pattern):
				return True
		return False


	def _get_generated_images(self) -> list[str]:
		repository = TranslatorRepository(self.configuration)
		runner = TranslatorRunner(repository)
		runner.sync()
		images = runner.get_source_images()
		ddir = self.configuration.document_directory
		image_list : list[str] = list()
		for image in images:
			for target in runner.get_target_files(in_file=image):
				if ddir:
					abspath = genutils.abs_path(target, ddir)
				else:
					abspath = os.path.abspath(target)
				image_list.append(abspath)
		return image_list


	def run_cleanall_command(self, cli_arguments : Namespace) -> bool:
		"""
		Run the command 'cleanall' or '--all' optional argument.
		:param cli_arguments: the arguments.
		:return: True if the process could continue. False if an error occurred and the process should stop.
		"""
		# Remove additional files
		# noinspection DuplicatedCode
		maker = self._internal_create_maker()
		# Prepare used-defined list of deletable files
		clean_files = self.configuration.clean.cleanall_files
		abs_clean_files = list()
		bn_clean_files = list()
		for file in clean_files:
			if os.sep in file:
				abs_clean_files.append(file)
			else:
				bn_clean_files.append(file)
		for root_file in maker.root_files:
			root_dir = os.path.dirname(root_file)
			if cli_arguments.norecursive:
				root = os.path.dirname(root_file)
				for filename in os.listdir(root):
					abs_filename = os.path.normpath(os.path.join(root, filename))
					if self._is_deletable_anywhere(abs_filename)\
							or self._is_deletable_shell(abs_filename, filename, abs_clean_files, bn_clean_files):
						self._delete_file(abs_filename, cli_arguments.simulate)
			else:
				for root, dirs, files in os.walk(os.path.dirname(root_file)):
					for filename in files:
						abs_filename = os.path.normpath(os.path.join(root,  filename))
						if root == root_dir and self._is_deletable_anywhere(abs_filename)\
								or self._is_deletable_shell(abs_filename, filename, abs_clean_files, bn_clean_files):
							self._delete_file(abs_filename, cli_arguments.simulate)
		for generated_image in self._get_generated_images():
			self._delete_file(generated_image, cli_arguments.simulate)
		return True


	def _show_deletions_message(self, cli_arguments : Namespace):
		"""
		Show the conclusion message.
		:param cli_arguments: The CLI arguments.
		:type cli_arguments: argparse object
		"""
		if cli_arguments.simulate:
			msg = TT("%d file were selected as deletion candidates", "%d files were selected as deletion candidates", self.__nb_deletions)
		else:
			msg = TT("%d file was deleted", "%d files were deleted", self.__nb_deletions) % self.__nb_deletions
		logging.info(msg)
