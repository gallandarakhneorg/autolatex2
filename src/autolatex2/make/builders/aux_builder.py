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

from autolatex2.make.abstractbuilder import Builder
from autolatex2.make.filedescription import FileDescription
from autolatex2.make.abstractmaker import TeXMaker
from autolatex2.tex.utils import FileType


class DynamicBuilder(Builder):
	"""
	Build the auxiliary AUX file.
	"""

	output = FileType.aux

	# noinspection PyBroadException
	@override
	def build(self, root_file : str, input_file : FileDescription, maker : TeXMaker) -> bool:
		"""
		Generate initial AUX auxiliary file. This function invokes run_latex() with loop support disabled.
		:param root_file: Name of the root file (tex document).
		:type root_file: str
		:param input_file: Description of the input TeX file.
		:type input_file: FileDescription
		:param maker: reference to the general maker instance that provides general building tools.
		:type maker: TeXMaker
		:return: The continuation status, i.e. True if the build could continue.
		:rtype: bool
		"""
		try:
			maker.run_latex(filename=input_file.input_filename,
							loop=False,
							extra_run_support=input_file.use_multibib)
		except:
			return False
		return True
