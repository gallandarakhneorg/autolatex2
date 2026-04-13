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

"""
General utilities for TeX.
"""
import logging
import os
import re
from dataclasses import dataclass
from enum import IntEnum, unique
from typing import Any

from autolatex2.utils.i18n import T


@unique
class TeXWarnings(IntEnum):
	"""
	List of LaTeX warnings supported by TeX maker
	"""
	done = 0
	undefined_reference = 1
	undefined_citation = 2
	multiple_definition = 3
	other_warning = 4


@dataclass
class DetailedTeXWarning:
	filename : str
	extension : str
	lineno : int
	message : str


class TeXLogParser:
	"""
	Parser of the TeX log file.
	"""

	def __init__(self, log_file : str = None):
		"""
		Construct the log parser.
		:param log_file: the path to the log file.
		:type log_file:	str
		"""
		self.__log_file : str | None = log_file

	@property
	def log_file(self) -> str | None:
		"""
		Replies the filename of the log file that is used by this parser.
		:return: the log filename
		:rtype: str | None
		"""
		return self.__log_file

	@log_file.setter
	def log_file(self, filename : str):
		"""
		Change the filename of the log file that is used by this parser.
		:param filename: the log filename
		:type filename: str
		"""
		self.__log_file = filename

	def extract_warnings(self, enable_loop : bool,
	                     enable_detailed_warnings : bool,
	                     standards_warnings : set[TeXWarnings] | None,
	                     detailed_warnings : list[DetailedTeXWarning] | None) -> bool:
		"""
		Parse the TeX log in order to extract warnings and replies if another TeX compilation is needed.
		:param enable_loop: Indicates if the compilation loop is enabled.
		:type enable_loop: bool
		:param enable_detailed_warnings: Indicates if the extended warnings should be also extracted.
		:type enable_detailed_warnings: bool
		:param standards_warnings: The list of standard warnings to fill up.
		:type standards_warnings: set[TeXWarnings] | None
		:param detailed_warnings: The list of extended warnings to fill up.
		:type detailed_warnings: list[DetailedTeXWarning] | None
		:return: True if another compilation is needed; Otherwise returns False
		:rtype: bool
		"""
		log_filename = self.log_file
		assert log_filename, 'No log filename provided'
		logging.debug(T("Reading log file: %s") % os.path.basename(log_filename))
		if os.path.exists(log_filename):
			with open(log_filename, 'r') as f:
				content = f.read()
			log_parser = TeXLogParser()
			if standards_warnings is None:
				standards_warnings = set()
			assert standards_warnings is not None, "standard_warnings is None"
			rerun = log_parser.extract_warning_from_str(content, standards_warnings)
			if rerun and enable_loop:
				return True
			if enable_detailed_warnings and detailed_warnings is not None:
				warns = re.findall(re.escape('!!!![BeginWarning]')+'(.*?)'+ re.escape('!!!![EndWarning]'), content, re.S)
				for warn in warns:
					m = re.search(r'^(.*?):([^:]*):([0-9]+):\s*(.*?)\s*$', warn, re.S)
					if m is not None:
						warn_details = DetailedTeXWarning(
							filename = m.group(1),
							extension = m.group(2),
							lineno = int(m.group(3)),
							message = self.fix_tex_message_format(m.group(4)))
						detailed_warnings.append(warn_details)
		return False

	# noinspection PyMethodMayBeStatic
	def extract_warning_from_str(self, content : str, warnings : set[TeXWarnings]) -> bool:
		"""
		Test if the given content contains a typical TeX warning message.
		This function stores the discovered warning into this maker.
		True is replied if a new run of the TeX compiler is requested
		within the warning message. False is replied if the TeX compiler
		should not be re-run.
		:param content: The line of text to parse.
		:type content: str
		:param warnings: The list of warnings to fill up.
		:type warnings: set[TeXWarnings]
		:rtype: bool
		"""
		content = re.sub(r"[^a-zA-Z:]+", '', content)
		if re.search(r'Warning.*Rerun(?:thelatexcompiler|togetcrossreferencesright|togetoutlinesright)', content, re.I):
			return True
		if re.search(r'Warning:Therewereundefinedreferences', content, re.I):
			warnings.add(TeXWarnings.undefined_reference)
		if re.search(r'Warning:Citation.+undefined', content, re.I):
			warnings.add(TeXWarnings.undefined_citation)
		if re.search(r'Warning:Thereweremultiplydefinedlabels', content, re.I):
			warnings.add(TeXWarnings.multiple_definition)
		if re.search(r'(?:\s|^)Warning', content, re.I | re.M):
			warnings.add(TeXWarnings.other_warning)
		return False


	def __analyze_log_block(self, block_text : str) -> tuple[int,Any]:
		"""
		Analyze the given block of text from the log file and determines if it
		is a fatal error (value: 1), a warning (value: 2), an irrelevant text (value: 0).
		The second parameter of the tuple depends on the type of the block.
		:param block_text: the text to analyze.
		:return: the state of the block, that is a tuple with the type of block and the
		associated information.
		"""
		m = re.search(r'(LaTeX\s+Error:.+)$', block_text, re.S | re.I)
		if m:
			return 1, m.group(1).strip()
		m = re.search(r'(Undefined\s+control\s+sequence.+)$', block_text, re.S | re.I)
		if m:
			return 1, m.group(1).strip()
		if re.search(r'Fatal\s+error\s+occurred', block_text, re.S | re.I):
			return 1, 'Fatal error occurred, no output PDF file produced!'
		m = re.search(re.escape('!!!![BeginWarning]') + '(.*?)' + re.escape('!!!![EndWarning]'), block_text, re.S)
		if m:
			return 2, m.group(1).strip()
		return 0, None


	# noinspection PyMethodMayBeStatic
	def extract_failure(self) -> tuple[str,list[str]] | str:
		"""
		Parse the given file as a TeX log file and extract any relevant information related
		to a failure.
		All the block of warnings or errors are detected until a fatal error or the
		end of the file is reached.
		This function replies a tuple in which the first member is the fatal error,
		if one, and the second member is the list of log blocks.
		:return: If blocks must be extracted, a tuple with the fatal error, followed by a list of log blocks.
		If blocks must not be extracted, the fatal error if any.
		:rtype: tuple[str,list[str]] | str
		"""
		log_filename = self.log_file
		assert log_filename, 'No log filename provided'
		blocks = list()
		if os.path.exists(log_filename):
			with open(log_filename, "r") as f:
				current_block = ''
				for line in f:
					line0 = line.strip()
					if line0 == '':
						if current_block:
							block_text = self.fix_tex_message_format(current_block)
							block_type, block_info = self.__analyze_log_block(block_text)
							if block_type == 1:
								return str(block_info), blocks
							elif block_type == 2:
								blocks.append(str(block_info))
							current_block = ''
					else:
						current_block = current_block + line
			if current_block:
				block_text = self.fix_tex_message_format(current_block)
				block_type, block_info = self.__analyze_log_block(block_text)
				if block_type == 1:
					return str(block_info), blocks
				elif block_type == 2:
					blocks.append(str(block_info))
		return '', blocks


	# noinspection PyMethodMayBeStatic
	def fix_tex_message_format(self, text : str) -> str:
		"""
		Reformat the TeX message in order to remove improper carriage returns.
		:param text: the original TeX message.
		:return: the fixed message.
		"""
		text0 = re.sub(r'[\r\n]\([^)]*\)', '', text.strip())
		text0 = re.sub(r'[\n\r]', '', text0)
		text0 = re.sub(r'\s+', ' ', text0)
		return text0
