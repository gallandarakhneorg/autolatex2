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

from typing import override

from autolatex2.utils import extlogging

from autolatex2.make.abstractbuilder import Builder
from autolatex2.make.filedescription import FileDescription
from autolatex2.make.abstractmaker import TeXMaker
import autolatex2.utils.utilfunctions as genutils
from autolatex2.tex.utils import FileType
from autolatex2.utils.i18n import T


class DynamicBuilder(Builder):
	"""
	Build the index IND file.
	"""

	output = FileType.ind

	# noinspection PyBroadException
	@override
	def build(self, root_file : str, input_file : FileDescription, maker : TeXMaker) -> bool:
		"""
		Generate IND (index) file. This function invokes run_latex() (without loop support) if xindyis used or
		if the idx file is less recent than the input TeX file. Then, the function calls run_makeindex().
		:param root_file: Name of the root file (tex document).
		:type root_file: str
		:param input_file: Description of the input TeX file.
		:type input_file: FileDescription
		:param maker: reference to the general maker instance that provides general building tools.
		:type maker: TeXMaker
		:return: The continuation status, i.e. True if the build could continue.
		:rtype: bool
		"""
		if maker.configuration.generation.is_index_enable:
			# Ensure texindy configuration
			maker.configuration.generation.is_xindy_index = input_file.use_xindy

			is_run_latex = False
			if maker.configuration.generation.is_xindy_index:
				# Special case: TeX should be launched before running texindy
				is_run_latex = True
			else:
				tex_wo_ext = genutils.basename_with_path(input_file.input_filename, *FileType.tex_extensions())
				idx_file = tex_wo_ext + FileType.idx.extension()
				input_change = input_file.change
				idx_change = genutils.get_file_last_change(idx_file)
				if maker.is_obsolete_timestamp(idx_change, input_change):
					is_run_latex = True
			if is_run_latex:
				try:
					maker.run_latex(filename=input_file.input_filename, loop=False)
				except:
					return False
			result = maker.run_makeindex(input_file.input_filename)
			if result is not None:
				exit_code, sout, serr = result
				if exit_code != 0:
					message = (sout or '') + (serr or '')
					extlogging.multiline_error(T("Error when running the indexing tool: %s") % message)
					return False
		return True

	@override
	def consider_dependencies(self) -> bool:
		"""
		Replies if this builder must test the need of rebuild for each file in the dependencies of the current file.
		If the function replies True, the function need_rebuild() will be invoked on each file in the dependencies;
		Otherwise, the function need_rebuild() will be invoked once with the argument dependency_file to None.
		:return: True to invoke need_rebuild() for each dependency.
		:rtype: bool
		"""
		return False

	@override
	def need_rebuild_without_dependency(self, current_file: FileDescription,
										root_tex_file: str, maker: TeXMaker) -> bool:
		"""
		Test if a rebuild is needed for the given files. The default implementation is testing the
		file timestamps of the two provided files.
		:param current_file: The description of the current file that is under analysis.
		:type current_file: FileDescription
		:param root_tex_file: Name of the main TeX file.
		:type root_tex_file: str
		:param maker: reference to the general maker instance that provides general building tools.
		:type maker: TeXMaker
		:return: True if the current file needs to be rebuilt.
		:rtype: bool
		"""
		# Parse the IDX file to detect the index definitions
		old_md5 = maker.stamp_manager.get_index_stamp(current_file.output_filename)
		current_md5 = maker.stamp_manager.parse_index(current_file.output_filename, update_stamps=False)
		if current_md5 != old_md5:
			maker.stamp_manager.set_index_stamp(current_file.output_filename, current_md5)
			return True
		return False
