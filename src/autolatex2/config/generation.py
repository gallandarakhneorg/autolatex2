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
Configuration for the generation.
"""

import autolatex2.utils.utilfunctions as genutils

class GenerationConfig:
	"""
	Configuration of a AutoLaTeX instance.
	"""

	def __init__(self):
		self.__is_pdf_mode : bool = True
		self.__extended_warnings : bool = True
		self.__makeindex : bool = True
		self.__biblio : bool = True
		self.__synctex : bool = False
		self.__latex_compiler : str | None = None
		self.__latex_cli : list[str] = list()
		self.__latex_flags : list[str] = list()
		self.__bibtex_cli : list[str] = list()
		self.__bibtex_flags : list[str] = list()
		self.__biber_cli : list[str] = list()
		self.__biber_flags : list[str] = list()
		self.__makeindex_cli : list[str] = list()
		self.__makeindex_flags : list[str] = list()
		self.__makeindex_style_filename : str | None = None
		self.__texindy_cli : list[str] = list()
		self.__texindy_flags : list[str] = list()
		self.__makeglossary_cli : list[str] = list()
		self.__makeglossary_flags : list[str] = list()
		self.__dvips_cli : list[str] = list()
		self.__dvips_flags : list[str] = list()
		self.__use_biber : bool = False
		self.__use_biblatex : bool = False
		self.__use_makeindex : bool = False
		self.__use_texindy : bool = False
		self.__use_multibib : bool = False
		self.__enable_biblio : bool = True
		self.__enable_index : bool = True
		self.__enable_glossary : bool = True

	def reset_internal_attributes(self):
		"""
		Reset the internal attributes.
		"""
		self.__is_pdf_mode = True
		self.__extended_warnings = True
		self.__makeindex = True
		self.__biblio = True
		self.__synctex = False
		self.__latex_compiler = None
		self.__latex_cli = list()
		self.__latex_flags = list()
		self.__bibtex_cli = list()
		self.__bibtex_flags = list()
		self.__biber_cli = list()
		self.__biber_flags = list()
		self.__makeindex_cli = list()
		self.__makeindex_flags = list()
		self.__makeindex_style_filename = None
		self.__texindy_cli = list()
		self.__texindy_flags = list()
		self.__makeglossary_cli = list()
		self.__makeglossary_flags = list()
		self.__dvips_cli = list()
		self.__dvips_flags = list()
		self.__use_biber = False
		self.__use_biblatex = False
		self.__use_makeindex = False
		self.__use_texindy = False
		self.__use_multibib = False
		self.__enable_biblio = True
		self.__enable_index = True
		self.__enable_glossary = True

	@property
	def pdf_mode(self) -> bool:
		"""
		Replies if the generation is in PDF mode.
		:return: True if the generated file is PDF. False if it is Postscript.
		:rtype: bool
		"""
		return self.__is_pdf_mode

	@pdf_mode.setter
	def pdf_mode(self, mode : bool):
		"""
		Set if the generation is in PDF mode.
		:param mode: True if the generated file is PDF. False if it is Postscript.
		:type mode: bool
		"""
		self.__is_pdf_mode = mode

	@property
	def extended_warnings(self) -> bool:
		"""
		Replies if the extended warning feature is enabled.
		:return: True if the extended warning feature is used.
		:rtype: bool
		"""
		return self.__extended_warnings

	@extended_warnings.setter
	def extended_warnings(self, enable : bool):
		"""
		Change if the extended warning feature is enabled.
		:param enable: True if the extended warning feature is used.
		:type enable: bool
		"""
		self.__extended_warnings = enable

	@property
	def makeindex(self) -> bool:
		"""
		Replies if the 'makeindex' tools is enabled during the generation.
		:return: True if 'makeindex' should be invoked when necessary.
		:rtype: bool
		"""
		return self.__makeindex

	@makeindex.setter
	def makeindex(self, enable : bool):
		"""
		Set if the 'makeindex' tools is enabled during the generation.
		:param enable: True if 'makeindex' should be invoked when necessary.
		:type enable: bool
		"""
		self.__makeindex = enable

	@property
	def biblio(self) -> bool:
		"""
		Replies if the 'bibliography' tools is enabled during the generation.
		:return: True if 'bibliography' should be invoked when necessary.
		:rtype: bool
		"""
		return self.__biblio

	@biblio.setter
	def biblio(self, enable : bool):
		"""
		Set if the 'bibliography' tools is enabled during the generation.
		:param enable: True if 'bibliography' should be invoked when necessary.
		:type enable: bool
		"""
		self.__biblio = enable

	@property
	def synctex(self) -> bool:
		"""
		Replies if the synctex feature is enabled.
		:return: True if synctex enabled.
		:rtype: bool
		"""
		return self.__synctex

	@synctex.setter
	def synctex(self, enable : bool):
		"""
		Set if the synctex feature is enabled.
		:param enable: True if synctex enabled.
		:type enable: bool
		"""
		self.__synctex = enable

	@property
	def latex_compiler(self) -> str | None:
		"""
		Replies the name of the latex compiler to use. If None, the latex compiler will be determined later.
		:return: pdflatex, latex, xelatex, lualatex. Or None if undefined.
		:rtype: str | None
		"""
		return self.__latex_compiler

	@latex_compiler.setter
	def latex_compiler(self, name : str | None):
		"""
		Set the name of the latex compiler to use.
		:param name: Must be one of pdflatex, latex, xelatex, lualatex.  If None, the latex compiler will be determined later.
		:type name: str | None
		"""
		self.__latex_compiler = name

	@property
	def latex_cli(self) -> list[str]:
		"""
		Replies the command-line for latex.
		:rtype: list[str]
		"""
		return self.__latex_cli

	@latex_cli.setter
	def latex_cli(self, cli : list[str] | str | None):
		"""
		Set the command-line for latex.
		:param cli: The CLI. If it is None, the CLI is set to empty. If it is a single string, then this string is
		parsed using the genutils.parse_cli() method.
		:type cli: list[str] | str | None
		"""
		if cli is None:
			self.__latex_cli = list()
		elif isinstance(cli, list):
			self.__latex_cli = cli
		else:
			self.__latex_cli = genutils.parse_cli(cli)

	@property
	def latex_flags(self) -> list[str]:
		"""
		Replies additional flags for the latex compiler.
		:rtype: list[str]
		"""
		return self.__latex_flags

	@latex_flags.setter
	def latex_flags(self, flags : list[str] | str | None):
		"""
		Set additional flags for the latex compiler.
		:param flags: The CLI. If it is None, the CLI is set to empty. If it is a single string, then this string is
		parsed using the genutils.parse_cli() method.
		:type flags: list[str] | str | None
		"""
		if flags is None:
			self.__latex_flags = list()
		elif isinstance(flags, list):
			self.__latex_flags = flags
		else:
			self.__latex_flags = genutils.parse_cli(flags)

	@property
	def bibtex_cli(self) -> list[str]:
		"""
		Replies the command-line for bibtex.
		:rtype: list[str]
		"""
		return self.__bibtex_cli

	@bibtex_cli.setter
	def bibtex_cli(self, cli : list[str] | str | None):
		"""
		Set the command-line for bibtex.
		:param cli: The CLI. If it is None, the CLI is set to empty. If it is a single string, then this string is
		parsed using the genutils.parse_cli() method.
		:type cli: list[str] | str | None
		"""
		if cli is None:
			self.__bibtex_cli = list()
		elif isinstance(cli, list):
			self.__bibtex_cli = cli
		else:
			self.__bibtex_cli = genutils.parse_cli(cli)

	@property
	def bibtex_flags(self) -> list[str]:
		"""
		Replies additional flags for the bibtex compiler.
		:rtype: list[str]
		"""
		return self.__bibtex_flags

	@bibtex_flags.setter
	def bibtex_flags(self, flags : list[str] | str | None):
		"""
		Set additional flags for the bibtex compiler.
		:param flags: The CLI. If it is None, the CLI is set to empty. If it is a single string, then this string is
		parsed using the genutils.parse_cli() method.
		:type flags: list[str] | str | None
		"""
		if flags is None:
			self.__bibtex_flags = list()
		elif isinstance(flags, list):
			self.__bibtex_flags = flags
		else:
			self.__bibtex_flags = genutils.parse_cli(flags)

	@property
	def biber_cli(self) -> list[str]:
		"""
		Replies the command-line for biber.
		:rtype: list[str]
		"""
		return self.__biber_cli

	@biber_cli.setter
	def biber_cli(self, cli : list[str] | str | None):
		"""
		Set the command-line for biber.
		:param cli: The CLI. If it is None, the CLI is set to empty. If it is a single string, then this string is
		parsed using the genutils.parse_cli() method.
		:type cli: list[str] | str | None
		"""
		if cli is None:
			self.__biber_cli = list()
		elif isinstance(cli, list):
			self.__biber_cli = cli
		else:
			self.__biber_cli = genutils.parse_cli(cli)

	@property
	def biber_flags(self) -> list[str]:
		"""
		Replies additional flags for the biber compiler.
		:rtype: list[str]
		"""
		return self.__biber_flags

	@biber_flags.setter
	def biber_flags(self, flags : list[str] | str | None):
		"""
		Set additional flags for the biber compiler.
		:param flags: The CLI. If it is None, the CLI is set to empty. If it is a single string, then this string is
		parsed using the genutils.parse_cli() method.
		:type flags: list[str] | str | None
		"""
		if flags is None:
			self.__biber_flags = list()
		elif isinstance(flags, list):
			self.__biber_flags = flags
		else:
			self.__biber_flags = genutils.parse_cli(flags)

	@property
	def is_biber(self) -> bool:
		"""
		Replies if the Biber tool must be used instead of the standard bibtex.
		:rtype: bool
		"""
		return self.__use_biber

	@is_biber.setter
	def is_biber(self, enable : bool):
		"""
		Change the flag that indicates if the Biber tool must be used instead of the standard bibtex.
		:type enable: bool
		"""
		self.__use_biber = enable

	@property
	def is_biblatex(self) -> bool:
		"""
		Replies if the biblatex tool must be used.
		:rtype: bool
		"""
		return self.__use_biblatex

	@is_biblatex.setter
	def is_biblatex(self, enable : bool):
		"""
		Change the flag that indicates if the biblatex tool must be used.
		:type enable: bool
		"""
		self.__use_biblatex = enable
	
	@property
	def is_makeindex(self) -> bool:
		"""
		Replies if the makeindex tool must be used.
		:rtype: bool
		"""
		return self.__use_makeindex

	@is_makeindex.setter
	def is_makeindex(self, enable : bool):
		"""
		Change the flag that indicates if the makeindex tool must be used.
		:type enable: bool
		"""
		self.__use_makeindex = enable

	@property
	def is_xindy_index(self) -> bool:
		"""
		Replies if the texindy tool must be used.
		:rtype: bool
		"""
		return self.__use_texindy

	@is_xindy_index.setter
	def is_xindy_index(self, enable : bool):
		"""
		Change the flag that indicates if the texindy tool must be used.
		:type enable: bool
		"""
		self.__use_texindy = enable

	@property
	def is_multibib(self) -> bool:
		"""
		Replies if the multibib tool must be used.
		:rtype: bool
		"""
		return self.__use_multibib

	@is_multibib.setter
	def is_multibib(self, enable : bool):
		"""
		Change the flag that indicates if the multibib tool must be used.
		:type enable: bool
		"""
		self.__use_multibib = enable

	@property
	def is_biblio_enable(self) -> bool:
		"""
		Replies if the bibliography generation is activated.
		:rtype: bool
		"""
		return self.__enable_biblio

	@is_biblio_enable.setter
	def is_biblio_enable(self, enable : bool):
		"""
		Change the activation flag for the bibliography generation.
		:type enable: bool
		"""
		self.__enable_biblio = enable

	@property
	def is_index_enable(self) -> bool:
		"""
		Replies if the index generation is activated.
		:rtype: bool
		"""
		return self.__enable_index

	@is_index_enable.setter
	def is_index_enable(self, enable : bool):
		"""
		Change the activation flag for the index generation.
		:type enable: bool
		"""
		self.__enable_index = enable

	@property
	def is_glossary_enable(self) -> bool:
		"""
		Replies if the glossary generation is activated.
		:rtype: bool
		"""
		return self.__enable_glossary

	@is_glossary_enable.setter
	def is_glossary_enable(self, enable : bool):
		"""
		Change the activation flag for the glossary generation.
		:type enable: bool
		"""
		self.__enable_glossary = enable

	@property
	def makeglossary_cli(self) -> list[str]:
		"""
		Replies the command-line for makeglossary.
		:rtype: list[str]
		"""
		return self.__makeglossary_cli

	@makeglossary_cli.setter
	def makeglossary_cli(self, cli : list[str] | str | None):
		"""
		Set the command-line for makeglossary.
		:param cli: The CLI. If it is None, the CLI is set to empty. If it is a single string, then this string is
		parsed using the genutils.parse_cli() method.
		:type cli: list[str] | str | None
		"""
		if cli is None:
			self.__makeglossary_cli = list()
		elif isinstance(cli, list):
			self.__makeglossary_cli = cli
		else:
			self.__makeglossary_cli = genutils.parse_cli(cli)

	@property
	def makeglossary_flags(self) -> list[str]:
		"""
		Replies additional flags for the makeglossary compiler.
		:rtype: list[str]
		"""
		return self.__makeglossary_flags

	@makeglossary_flags.setter
	def makeglossary_flags(self, flags : list[str] | str | None):
		"""
		Set additional flags for the makeglossary compiler.
		:param flags: The CLI. If it is None, the CLI is set to empty. If it is a single string, then this string is
		parsed using the genutils.parse_cli() method.
		:type flags: list[str] | str | None
		"""
		if flags is None:
			self.__makeglossary_flags = list()
		elif isinstance(flags, list):
				self.__makeglossary_flags = flags
		else:
			self.__makeglossary_flags = genutils.parse_cli(flags)

	@property
	def makeindex_cli(self) -> list[str]:
		"""
		Replies the command-line for makeindex.
		:rtype: list[str]
		"""
		return self.__makeindex_cli

	@makeindex_cli.setter
	def makeindex_cli(self, cli : list[str] | str | None):
		"""
		Set the command-line for makeindex.
		:param cli: The CLI. If it is None, the CLI is set to empty. If it is a single string, then this string is
		parsed using the genutils.parse_cli() method.
		:type cli: list[str] | str | None
		"""
		if cli is None:
			self.__makeindex_cli = list()
		elif isinstance(cli, list):
			self.__makeindex_cli = cli
		else:
			self.__makeindex_cli = genutils.parse_cli(cli)

	@property
	def makeindex_flags(self) -> list[str]:
		"""
		Replies additional flags for the makeindex compiler.
		:rtype: list[str]
		"""
		return self.__makeindex_flags

	@makeindex_flags.setter
	def makeindex_flags(self, flags : list[str] | str | None):
		"""
		Set additional flags for the makeindex compiler.
		:param flags: The CLI. If it is None, the CLI is set to empty. If it is a single string, then this string is
		parsed using the genutils.parse_cli() method.
		:type flags: list[str] | str | None
		"""
		if flags is None:
			self.__makeindex_flags = list()
		elif isinstance(flags, list):
			self.__makeindex_flags = flags
		else:
			self.__makeindex_flags = genutils.parse_cli(flags)

	@property
	def texindy_cli(self) -> list[str]:
		"""
		Replies the command-line for texindy.
		:rtype: list[str]
		"""
		return self.__texindy_cli

	@texindy_cli.setter
	def texindy_cli(self, cli : list[str] | str | None):
		"""
		Set the command-line for texindy.
		:param cli: The CLI. If it is None, the CLI is set to empty. If it is a single string, then this string is
		parsed using the genutils.parse_cli() method.
		:type cli: list[str] | str | None
		"""
		if cli is None:
			self.__texindy_cli = list()
		elif isinstance(cli, list):
			self.__texindy_cli = cli
		else:
			self.__texindy_cli = genutils.parse_cli(cli)

	@property
	def texindy_flags(self) -> list[str]:
		"""
		Replies additional flags for the texindy compiler.
		:rtype: list[str]
		"""
		return self.__texindy_flags

	@texindy_flags.setter
	def texindy_flags(self, flags : list[str] | str | None):
		"""
		Set additional flags for the texindy compiler.
		:param flags: The CLI. If it is None, the CLI is set to empty. If it is a single string, then this string is
		parsed using the genutils.parse_cli() method.
		:type flags: list[str] | str | None
		"""
		if flags is None:
			self.__texindy_flags = list()
		elif isinstance(flags, list):
			self.__texindy_flags = flags
		else:
			self.__texindy_flags = genutils.parse_cli(flags)

	@property
	def makeindex_style_filename(self) -> str:
		"""
		Replies filename that is the MakeIndex style to be used.
		:rtype: str
		"""
		return self.__makeindex_style_filename or ''

	@makeindex_style_filename.setter
	def makeindex_style_filename(self, filename : str):
		"""
		Set the filename that is the MakeIndex style to be used.
		:type filename: str
		"""
		self.__makeindex_style_filename = filename

	@property
	def dvips_cli(self) -> list[str]:
		"""
		Replies the command-line for dvi2ps.
		:rtype: list[str]
		"""
		return self.__dvips_cli

	@dvips_cli.setter
	def dvips_cli(self, cli : list[str] | str | None):
		"""
		Set the command-line for dvips.
		:param cli: The CLI. If it is None, the CLI is set to empty. If it is a single string, then this string is
		parsed using the genutils.parse_cli() method.
		:type cli: list[str] | str | None
		"""
		if cli is None:
			self.__dvips_cli = list()
		elif isinstance(cli, list):
			self.__dvips_cli = cli
		else:
			self.__dvips_cli = genutils.parse_cli(cli)

	@property
	def dvips_flags(self) -> list[str]:
		"""
		Replies additional flags for the dvips compiler.
		:rtype: list[str]
		"""
		return self.__dvips_flags

	@dvips_flags.setter
	def dvips_flags(self, flags : list[str] | str | None):
		"""
		Set additional flags for the dvips compiler.
		:param flags: The CLI. If it is None, the CLI is set to empty. If it is a single string, then this string is
		parsed using the genutils.parse_cli() method.
		:type flags: list[str] | str | None
		"""
		if flags is None:
			self.__dvips_flags = list()
		elif isinstance(flags, list):
			self.__dvips_flags = flags
		else:
			self.__dvips_flags = genutils.parse_cli(flags)

