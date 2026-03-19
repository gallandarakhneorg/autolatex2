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

import os
import re
from enum import IntEnum, unique

import gettext
_T = gettext.gettext

######################################################################
##
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

def get_tex_file_extensions() -> list[str]:
	"""
	Replies the supported filename extensions for TeX files.
	:return: The list of the filename extensions.
	:rtype: list
	"""
	return ['.tex', '.latex', '.ltx']

def get_index_file_extensions() -> list[str]:
	"""
	Replies the supported filename extensions for Index files.
	:return: The list of the filename extensions.
	:rtype: list
	"""
	return ['.idx',  '.ind']

def get_glossary_file_extensions() -> list[str]:
	"""
	Replies the supported filename extensions for glossary files.
	:return: The list of the filename extensions.
	:rtype: list
	"""
	return ['.glo',  '.gls',  '.acr',  '.not']

def is_tex_file_extension(ext : str) -> bool:
	"""
	Test if a given string is a standard extension for TeX document.
	The test is case-insensitive.
	:param ext: The extension to test.
	:type ext: str
	:return: True if the extension is for a TeX/LaTeX file; otherwise False.
	:rtype: bool
	"""
	ext = ext.lower()
	return ext in get_tex_file_extensions()

def is_tex_document(filename : str) -> bool:
	"""
	Replies if the given filname is a TeX document.
	The test is case-insensitive.
	:param filename: The filename to test.
	:type filename: str
	:return: True if the extension is for a TeX/LaTeX file; otherwise False.
	:rtype: bool
	"""
	if filename:
		ext = os.path.splitext(filename)[-1]
		return is_tex_file_extension(ext)
	return False

def extract_tex_warning_from_line(line : str, warnings : set[TeXWarnings]) -> bool:
	"""
	Test if the given line contains a typical TeX warning message.
	This function stores the discovered warning into this maker.
	True is replied if a new run of the TeX compiler is requested
	within the warning message. False is replied if the TeX compiler
	should not be re-run.
	:param line: The line of text to parse.
	:type line: str
	:param warnings: The list of warnings to fill.
	:type warnings: set[TeXWarnings]
	:rtype: bool
	"""
	line = re.sub(r"[^a-zA-Z:]+", '', line)
	if re.search(r'Warning.*Rerun', line, re.I):
		return True
	elif re.search(r'Warning:Therewereundefinedreferences', line, re.I):
		warnings.add(TeXWarnings.undefined_reference)
	elif re.search(r'Warning:Citation.+undefined', line, re.I):
		warnings.add(TeXWarnings.undefined_citation)
	elif re.search(r'Warning:Thereweremultiplydefinedlabels', line, re.I):
		warnings.add(TeXWarnings.multiple_definition)
	elif re.search(r'(?:\s|^)Warning', line, re.I | re.M):
		warnings.add(TeXWarnings.other_warning)
	return False


def __parse_tex_fatal_error_message(error : str) -> str:
	err0 = re.sub(r'!!!!\[BeginWarning].*?!!!!\[EndWarning].*', '', error, re.S | re.I)
	m = re.match(r'^.*?:[0-9]+:\s*(.*?)\s*$', err0, re.S)
	if m:
		return m.group(1).strip()
	return ''


def parse_tex_log_file(log_filename : str) -> tuple[str,list[str]]:
	"""
	Parse the given file as a TeX log file and extract any relevant information.
	All the block of warnings or errors are detected until a fatal error or the
	end of the file is reached.
	This function replies a tuple in which the first member is the fatal error,
	if one, and the second member is the list of log blocks.
	:param log_filename: The filename of the log file.
	:type log_filename: str
	:rtype: tuple[str,list[str]]
	"""
	blocks = list()
	fatal_error = ''
	with open(log_filename, "r") as f:
		line = f.readline()
		current_block = ''
		while line is not None and line != '':
			line = line.strip()
			if line is None or line == '':
				if current_block:
					blocks.append(current_block)
					if not fatal_error:
						fatal_error = __parse_tex_fatal_error_message(current_block)
				current_block = ''
			else:
				current_block = current_block + line
			line = f.readline()
	if current_block:
		blocks.append(current_block)
		if not fatal_error:
			fatal_error = __parse_tex_fatal_error_message(current_block)
	return fatal_error, blocks
