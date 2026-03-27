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
Definition of the enumeration types for the AutoLaTeX Maker.
"""

from enum import IntEnum, unique

@unique
class TeXTools(IntEnum):
	"""
	Type of TeX tools supported by AutoLaTeX.
	"""
	bibtex = 0
	biber = 1
	makeindex = 2
	texindy = 3
	makeglossaries = 4
	dvips = 5
	pdflatex = 6
	latex = 7
	xelatex = 8
	lualatex = 9



@unique
class TeXCompiler(IntEnum):
	"""
	Type of LaTeX compilers supported by AutoLaTeX.
	"""
	pdflatex = TeXTools.pdflatex
	latex = TeXTools.latex
	xelatex = TeXTools.xelatex
	lualatex = TeXTools.lualatex



@unique
class BibCompiler(IntEnum):
	"""
	Type of bibliography compilers supported by AutoLaTeX.
	"""
	bibtex = TeXTools.bibtex
	biber = TeXTools.biber



@unique
class IndexCompiler(IntEnum):
	"""
	Type of index compilers supported by AutoLaTeX.
	"""
	makeindex = TeXTools.makeindex
	texindy = TeXTools.texindy



@unique
class GlossaryCompiler(IntEnum):
	"""
	Type of glossary compilers supported by AutoLaTeX.
	"""
	makeglossaries = TeXTools.makeglossaries



@unique
class FileType(IntEnum):
	"""
	Type of file in the AutoLaTeX making process.
	"""
	tex = 0
	pdf = 1
	ps = 3
	bib = 4
	bbl = 5
	bst = 6
	bbc = 7
	cbx = 8
	idx = 9
	ind = 10
	glo = 11
	gls = 12
	sty = 13
