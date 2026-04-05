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
import glob
from argparse import Namespace
from typing import override

from autolatex2.tex.citationanalyzer import BiblatexCitationAnalyzer, AuxiliaryCitationAnalyzer
from autolatex2.tex.glossaryanalyzer import GlossaryAnalyzer
from autolatex2.tex.indexanalyzer import IndexAnalyzer
from autolatex2.tex.utils import FileType
from autolatex2.utils import extprint
from autolatex2.make.maker import AutoLaTeXMaker
from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.utils.i18n import T


class MakerAction(AbstractMakerAction):

	id : str = 'stamps'

	help : str = T('Show or update the list of stamps saved by AutoLaTeX')

	# noinspection DuplicatedCode
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
		super()._add_command_cli_arguments(command_name, command_help, command_aliases)

		self.parse_cli.add_argument('--reset',
			action='store_true',
			help=T('Reset the stamps'))

		self.parse_cli.add_argument('--update',
			action='store_true',
			help=T('Compute and save the stamps according to the current content of the auxiliary files'))


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
				root_dir = os.path.dirname(root_file)

				if cli_arguments.reset:
					self._reset_stamps(maker, root_dir)
				else:
					if cli_arguments.update:
						stamps = self._update_stamps(maker, root_dir)
					else:
						stamps = maker.stamp_manager.read_build_stamps(root_dir)
					self._show_stamps(stamps)
		except BaseException as ex:
			logging.error(str(ex))
			return False
		return True

	# noinspection PyMethodMayBeStatic
	def _update_biber(self, root_dir : str, stamps : dict[str,dict[str,str]]):
		"""
		Update the stamps from the Biber/BibLaTeX auxiliary files.
		:param root_dir: the root directory of the auxiliary files.
		:type root_dir: str
		:param stamps: the stamp dictionary.
		:type stamps: dict[str,dict[str,str]]
		"""
		file_list = glob.glob('*' + FileType.bcf.extension(), root_dir=root_dir, recursive=False)
		if file_list:
			for bcf_file in file_list:
				bcf_analyzer = BiblatexCitationAnalyzer(bcf_file)
				current_md5: str = bcf_analyzer.md5 or ''
				if current_md5:
					if 'bib' not in stamps:
						stamps['bib'] = dict()
					stamps['bib'][bcf_file] = current_md5


	# noinspection PyMethodMayBeStatic
	def _update_bibtex(self, root_dir : str, stamps : dict[str,dict[str,str]]):
		"""
		Update the stamps from the BibTeX auxiliary files.
		:param root_dir: the root directory of the auxiliary files.
		:type root_dir: str
		:param stamps: the stamp dictionary.
		:type stamps: dict[str,dict[str,str]]
		"""
		file_list = glob.glob('*' + FileType.aux.extension(), root_dir=root_dir, recursive=False)
		if file_list:
			for aux_file in file_list:
				aux_analyzer = AuxiliaryCitationAnalyzer(aux_file)
				current_md5 = aux_analyzer.md5 or ''
				if current_md5:
					if 'bib' not in stamps:
						stamps['bib'] = dict()
					stamps['bib'][aux_file] = current_md5


	# noinspection PyMethodMayBeStatic
	def _update_index(self, root_dir : str, stamps : dict[str,dict[str,str]]):
		"""
		Update the stamps from the index IDX files.
		:param root_dir: the root directory of the auxiliary files.
		:type root_dir: str
		:param stamps: the stamp dictionary.
		:type stamps: dict[str,dict[str,str]]
		"""
		file_list = glob.glob('*' + FileType.idx.extension(), root_dir=root_dir, recursive=False)
		if file_list:
			for idx_file in file_list:
				idx_analyzer = IndexAnalyzer(idx_file)
				current_md5 = idx_analyzer.md5 or ''
				if current_md5:
					if 'idx' not in stamps:
						stamps['idx'] = dict()
					stamps['idx'][idx_file] = current_md5


	# noinspection PyMethodMayBeStatic
	def _update_glossary(self, root_dir : str, stamps : dict[str,dict[str,str]]):
		"""
		Update the stamps from the glossary files.
		:param root_dir: the root directory of the auxiliary files.
		:type root_dir: str
		:param stamps: the stamp dictionary.
		:type stamps: dict[str,dict[str,str]]
		"""
		file_list = glob.glob('*' + FileType.gls.extension(), root_dir=root_dir, recursive=False)
		if file_list:
			for gls_file in file_list:
				gls_analyzer = GlossaryAnalyzer(gls_file)
				current_md5 = gls_analyzer.md5 or ''
				if current_md5:
					if 'gls' not in stamps:
						stamps['bib'] = dict()
					stamps['gls'][gls_file] = current_md5


	# noinspection PyMethodMayBeStatic
	def _update_stamps(self, maker : AutoLaTeXMaker, root_dir : str) -> dict[str,dict[str,str]]:
		"""
		Update the stamps.
		:param maker: the maker instance.
		:type maker: AutoLaTeXMaker
		:param root_dir: the root directory of the auxiliary files.
		:type root_dir: str
		:return: the new stamp dictionary.
		:rtype: dict[str,dict[str,str]]
		"""
		stamps = dict()
		self._update_biber(root_dir, stamps)
		self._update_bibtex(root_dir, stamps)
		self._update_index(root_dir, stamps)
		self._update_glossary(root_dir, stamps)
		maker.stamp_manager.write_build_stamps(folder=root_dir, stamps=stamps)
		return stamps


	# noinspection PyMethodMayBeStatic
	def _reset_stamps(self, maker : AutoLaTeXMaker, root_dir : str):
		"""
		Reset the stamps.
		:param maker: the maker instance.
		:type maker: AutoLaTeXMaker
		:param root_dir: the root directory of the auxiliary files.
		:type root_dir: str
		"""
		stamps = dict()
		maker.stamp_manager.write_build_stamps(folder=root_dir, stamps=stamps)

	# noinspection PyMethodMayBeStatic
	def _show_stamps(self, stamps : dict[str,dict[str,str]]):
		"""
		Show the stamps.
		:param stamps: the stamp dictionary.
		:type stamps: dict[str,dict[str,str]]
		"""
		if stamps:
			for section, section_stamps in stamps.items():
				if section_stamps:
					for filename, key in section_stamps.items():
						extprint.eprint(f"[{section}] {filename} -> {key}")
