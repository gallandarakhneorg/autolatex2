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
Readers of "transdef" files.
"""

import re
import logging
from typing import override

from autolatex2.config.configobj import Config
from autolatex2.translator.readers.abstractreader import AbstractTransdefReader
from autolatex2.translator.readers.transdefline import TransdefLine
import autolatex2.utils.utilfunctions as genutils
from autolatex2.utils.i18n import T

class PerlTransdefReader(AbstractTransdefReader):
	"""
	Reader for the version 1 (original) transdef format (for the Perl version of the program).
	"""

	def __init__(self, configuration : Config):
		"""
		Constructor.
		:param configuration: the global configuration.
		:type configuration: Config
		"""
		super().__init__(configuration)

	@override
	def read_translator_file(self, filename : str) -> dict[str,TransdefLine]:
		"""
		Read the translator file. The replied value is the set of keys read from the transdef file.
		:param filename: the name of the file to read.
		:type filename: str
		:return: the content of the translator file
		:rtype: dict[str,TransdefLine]
		"""
		content : dict[str,TransdefLine] = dict()
		with open(filename) as f:
			lineno = 0
			eol = None
			curvar = None
			for line in f.readlines():
				lineno = lineno + 1
				if eol:
					if line.startswith(eol):
						eol = None
						curvar = None
					elif curvar:
						# Append to current entry
						content[curvar].value += line
				elif not re.match(r'^\s*[#;]', line):
					m = re.match(r'^\s*([azA-Z0-9_]+)(?:\s+with\s+(.*?))?(?:\s+for\s+(pdf|eps))?\s*=<<([a-zA-Z0-9_]+)\s*(.*?)\s*$', line, re.I)
					if m:
						curvar = m.group(1)
						interpreter = m.group(2)
						mode = m.group(3)
						eol = m.group(4)
						value = m.group(5)
						if (not mode) or (self.configuration.generation.pdf_mode and mode.lower() == 'pdf') or (not self.configuration.generation.pdf_mode and mode.lower() == 'eps'):
							curvar = curvar.upper()
							content[curvar] = TransdefLine(curvar,  lineno,  value, interpreter.lower() if interpreter else None)
						else:
							curvar = None
					else:
						m = re.match(r'^\s*([azA-Z0-9_]+)(?:\s+with\s+(.*?))?(?:\s+for\s+(pdf|eps))?\s*=\s*(.*?)\s*$', line, re.I)
						if m:
							var = m.group(1)
							interpreter = m.group(2)
							mode = m.group(3)
							value = m.group(4)
							if (not mode) or (self.configuration.generation.pdf_mode and mode.lower() == 'pdf') or (not self.configuration.generation.pdf_mode and mode.lower() == 'eps'):
								curvar = None
								eol = None
								content[var.upper()] = TransdefLine(var.upper(),  lineno,  value,  interpreter.lower() if interpreter else None)
						elif not re.match(r'^\s*$', line):
							logging.error(T("Line outside a definition (%s:%d).") % (filename, lineno))

		if eol:
			logging.error(T("The block for the variable '%s' is not closed. Keyword '%s' was not found (%s:%s).")
				% (curvar, eol, filename, lineno))

		# Translate the values into suitable Python objects
		if 'INPUT_EXTENSIONS' in content and content['INPUT_EXTENSIONS'] and content['INPUT_EXTENSIONS'].value:
			exts = re.split(r'\s+', content['INPUT_EXTENSIONS'].value or '')
			content['INPUT_EXTENSIONS'].value_list = list()
			for e in exts:
				if not re.match(r'^\s*$', e):
					if not re.match(r'^[.+]', e):
						e = "." + e
					content['INPUT_EXTENSIONS'].value_list.append(e)

		if 'OUTPUT_EXTENSIONS' in content and content['OUTPUT_EXTENSIONS'] and content['OUTPUT_EXTENSIONS'].value:
			exts = re.split(r'\s+', content['OUTPUT_EXTENSIONS'].value or '')
			content['OUTPUT_EXTENSIONS'].value_list = list()
			for e in exts:
				if not re.match(r'^\s*$', e):
					if not re.match(r'^\.', e):
						e = "." + e
					content['OUTPUT_EXTENSIONS'].value_list.append(e)

		if 'TRANSLATOR_PERL_DEPENDENCIES' in content and content['TRANSLATOR_PERL_DEPENDENCIES'] and content['TRANSLATOR_PERL_DEPENDENCIES'].value:
			logging.warning(T("The key 'TRANSLATOR_PERL_DEPENDENCIES' is no more supported in the translator files. Please use 'TRANSLATOR_PYTHON_DEPENDENCIES'"))

		if 'TRANSLATOR_PYTHON_DEPENDENCIES' in content and content['TRANSLATOR_PYTHON_DEPENDENCIES'] and content['TRANSLATOR_PYTHON_DEPENDENCIES'].value:
			content['TRANSLATOR_PYTHON_DEPENDENCIES'].value_list = re.split(r'\s+', content['TRANSLATOR_PYTHON_DEPENDENCIES'].value or '')

		# Ensure that the command line is a list
		if 'COMMAND_LINE' in content and content['COMMAND_LINE'] and content['COMMAND_LINE'].value:
			cli = genutils.parse_cli(command_line= str(content['COMMAND_LINE'].value), all_protect = True)
			content['COMMAND_LINE'].value = None
			content['COMMAND_LINE'].value_list = cli

		if 'FILES_TO_CLEAN' in content and content['FILES_TO_CLEAN'] and content['FILES_TO_CLEAN'].value:
			patterns = re.split(r'\s+', content['FILES_TO_CLEAN'].value or '')
			content['FILES_TO_CLEAN'].value_list = list()
			for p in patterns:
				if not re.match(r'^\s*$', p):
					content['FILES_TO_CLEAN'].value_list.append(p)

		return content
