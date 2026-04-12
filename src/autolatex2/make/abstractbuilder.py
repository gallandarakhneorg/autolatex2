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

from abc import ABC, abstractmethod

from autolatex2.make.filedescription import FileDescription
from autolatex2.make.abstractmaker import TeXMaker

class Builder(ABC):
	"""
	Build a part of the document using a specific tool.
	"""

	@abstractmethod
	def build(self, root_file : str, input_file : FileDescription, maker : TeXMaker) -> bool:
		"""
		Build the document with this tool.
		:param root_file: Name of the root file (tex document).
		:type root_file: str
		:param input_file: Description of the input TeX file.
		:type input_file: FileDescription
		:param maker: reference to the general maker instance that provides general building tools.
		:type maker: TeXMaker
		:return: The continuation status, i.e. True if the build could continue.
		:rtype: bool
		"""
		raise NotImplementedError()

	# noinspection PyMethodMayBeStatic
	def consider_dependencies(self) -> bool:
		"""
		Replies if this builder must test the need of rebuild for each file in the dependencies of the current file.
		If the function replies True, the function need_rebuild() will be invoked on each file in the dependencies;
		Otherwise, the function need_rebuild() will be invoked once with the argument dependency_file to None.
		:return: True to invoke need_rebuild() for each dependency.
		:rtype: bool
		"""
		raise NotImplementedError()

	# noinspection PyMethodMayBeStatic
	def need_rebuild(self, current_file : FileDescription, dependency_file : FileDescription|None,
					 root_tex_file : str, maker : TeXMaker) -> bool:
		"""
		Test if a rebuild is needed for the given files. The default implementation is testing the
		file timestamps of the two provided files.
		:param current_file: The description of the current file that is under analysis.
		:type current_file: FileDescription
		:param dependency_file: The description of the file that is a dependency, if provided
		:type dependency_file: FileDescription|None
		:param root_tex_file: Name of the main TeX file.
		:type root_tex_file: str
		:param maker: reference to the general maker instance that provides general building tools.
		:type maker: TeXMaker
		:return: True if the current file needs to be rebuilt.
		:rtype: bool
		"""
		if dependency_file:
			return maker.is_obsolete_timestamp(current_file.change, dependency_file.change)
		return False
