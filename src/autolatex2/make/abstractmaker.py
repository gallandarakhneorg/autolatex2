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
from typing import Any

from autolatex2.config.configobj import Config
from autolatex2.make.stamps import StampManager
from autolatex2.utils.runner import Runner, ScriptOutput

# noinspection DuplicatedCode
class TeXMaker(Runner, ABC):
	"""
	Abstract implementation of a TeX Maker
	"""

	def reset_file_change_for(self, filename : str):
		"""
		Reset the buffered last-changed date for the given filename, if it is known.
		If the filename is not known, this function does nothing.
		:param filename: The name of the file for which the last-change date should be reset.
		:type filename: str
		"""
		raise NotImplementedError()

	@property
	def stamp_manager(self) -> StampManager:
		"""
		Replies the manager of internal stamps.
		:rtype: StampManager
		"""
		raise NotImplementedError()

	@property
	def configuration(self) -> Config:
		"""
		Replies the current configuration.
		:return: the configuration.
		:rtype: Config
		"""
		raise NotImplementedError()

	@abstractmethod
	def is_obsolete_timestamp(self, parent_timestamp : float | None, child_timestamp : float | None) -> bool:
		"""
		Determine if the two given timestamps correspond to an obsolete parent time stamp compared to the child one.
		A parent time stamp is obsolete when it is undefined or its value is older than the one of the child.
		:param parent_timestamp: The timestamp of the parent file.
		:type parent_timestamp: float | None
		:param child_timestamp: The timestamp of the child file.
		:type child_timestamp: float | None
		:return: True if the parent file is considered as obsolete.
		:rtype: bool
		"""
		raise NotImplementedError()

	@abstractmethod
	def run_latex(self, filename : str, loop : bool = False, extra_run_support : bool = False) -> int:
		"""
		Launch the LaTeX tool and return the number of times the
		tool was launched.
		:param filename: The name TeX file to compile.
		:type filename: str
		:param loop: Indicates if this function may loop on the LaTeX compilation when it is requested by the LaTeX tool. Default value: False.
		:type loop: bool
		:param extra_run_support: Indicates if this function may apply an additional run of LaTeX tool because a tool used in TeX file does
		not provide accurate log message, and needs to have an extra LaTeX run to solves the problem. This is the case of Multibib for example.
		This argument is considered only if the argument "loop" is True; Otherwise, it is ignored.
		Default is False.
		:type extra_run_support: bool
		:return: The number of times the latex tool was run.
		:rtype: int
		"""
		raise NotImplementedError()

	@abstractmethod
	def run_bibtex(self, filename : str, check_aux_content : bool = True) -> dict[str,Any] | None:
		"""
		Launch the BibTeX tool (BibTeX, Biber, etc.) once time and replies a dictionary that describes any error.
		The returned dictionary has the keys: filename, lineno and message.
		This function also supports the document with zro, one or more bibliography sections, such a those
		introduced by the LaTeX package 'bibunits'.
		:param filename: The name of the auxiliary file or the root TeX file to use as input for the bibliography tool.
		:type filename: str
		:param check_aux_content: Indicates if this function has to read the auxiliary files to determine if a citation is inside.
		Then, if it is the case, the auxiliary file is passed to the bibliography tool; Otherwise it is ignored. Default is: True.
		:type check_aux_content: bool
		:return: the error result, or None if there is no error.
		:rtype: dict[str,Any] | None
		"""
		raise NotImplementedError()

	@abstractmethod
	def run_makeindex(self, filename : str) -> ScriptOutput | None:
		"""
		Launch the MakeIndex tool once time.
		The success status if the run of MakeIndex is replied.
		:param filename: The filename of the index file to compile.
		:type filename: str
		:return: None on success; Otherwise a tuple with the exit code and the standard and error outputs from the Makeindex tool.
		:rtype: tuple[int,str,str] | None
		"""
		raise NotImplementedError()

	@abstractmethod
	def run_makeglossaries(self, filename : str) -> bool:
		"""
		Launch the MakeGlossaries tool once time.
		The success status if the run of MakeGlossaries is replied.
		:param filename: The filename of the TeX file to compile.
		:type filename: str
		:return: True to continue the process. False to stop.
		:rtype: bool
		"""
		raise NotImplementedError()

	@abstractmethod
	def extract_info_from_tex_log_file(self, log_file : str, loop : bool) -> bool:
		"""
		Parse the TeX log in order to extract warnings and replies if another TeX compilation is needed.
		:param log_file: The filename of the log file that is used for detecting the compilation loop.
		:type log_file: str
		:param loop: Indicates if the compilation loop is enabled.
		:type loop: bool
		:return: True if another compilation is needed; Otherwise returns False
		:rtype: bool
		"""
		raise NotImplementedError()
