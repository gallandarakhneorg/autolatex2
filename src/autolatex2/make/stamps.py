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

import os
import re

from autolatex2.tex.citationanalyzer import AuxiliaryCitationAnalyzer
from autolatex2.tex.citationanalyzer import BiblatexCitationAnalyzer
from autolatex2.tex.glossaryanalyzer import GlossaryAnalyzer
from autolatex2.tex.indexanalyzer import IndexAnalyzer
from autolatex2.tex.utils import FileType
import autolatex2.utils.utilfunctions as genutils


# noinspection DuplicatedCode
class StampManager:
	"""
	Manager of the stamps used by AutoLaTeX.
	"""

	def __init__(self):
		self.__stamps : dict[str,dict[str,str]] = dict()
		self.__stamps['bib'] = dict()
		self.__stamps['idx'] = dict()
		self.__stamps['gls'] = dict()

	def reset(self):
		"""
		Reset the stamps in memory.
		"""
		self.__stamps = dict()
		self.__stamps['bib'] = dict()
		self.__stamps['idx'] = dict()
		self.__stamps['gls'] = dict()


	def read_build_stamps(self, folder : str, basename : str = ".autolatex_stamp"):
		"""
		Read the build stamps. There stamps are used to memorize the building dates of each element (LaTeX, BibTeX, etc.).
		Fill up the "__stamps" fields and reply them.
		:param folder: name of the folder in which the stamps file is located.
		:type folder: str
		:param basename: name of the temporary file. Default is: ".autolatex_stamp".
		:type basename: str
		"""
		stamp_file = os.path.join(folder, basename)
		self.reset()
		if os.access(stamp_file, os.R_OK):
			with open(stamp_file, 'r') as sf:
				line = sf.readline()
				while line:
					m = re.match(r'^(BIB|IDX|GLS)\(([^)]+?)\):(.+)$', line)
					if m:
						s = m.group(1)
						k = m.group(2)
						n = m.group(3)
						section = s.lower()
						if section not in self.__stamps:
							self.__stamps[section] = dict()
						self.__stamps[section][n] = k
					line = sf.readline()


	def write_build_stamps(self, folder : str, basename : str = ".autolatex_stamp", stamps : dict[str,dict[str,str]] = None):
		"""
		Write the build stamps. There stamps are used to memorize the building dates of each element (LaTeX, BibTeX, etc.).
		:param folder: name of the folder in which the stamps file is located.
		:type folder: str
		:param basename: name of the temporary file. Default is: ".autolatex_stamp".
		:type basename: str
		:param stamps: Stamps to write
		:type stamps: dict[str,dict[str,str]]
		"""
		stamp_file = os.path.join(folder, basename)
		if stamps is None:
			s = self.__stamps
		else:
			s = stamps
		with open(stamp_file, 'w') as sf:
			if s:
				for section in ['bib', 'idx', 'gls']:
					if section in s and s[section]:
						for (k, n) in s[section].items():
							sf.write("%s(" % section.upper())
							sf.write(str(n))
							sf.write("):")
							sf.write(str(k))
							sf.write("\n")

	def get_biber_stamp(self, bibliography_file : str) -> str:
		"""
		Replies the stamp that is associated to the BCF file.
		:param bibliography_file: the path of the bibliography file (bib, bbl, etc.) that may be associated to a BCF file.
		:type bibliography_file: str:
		:return: the stamp value.
		:rtype: str
		"""
		if 'bib' in self.__stamps:
			bcf_file = FileType.bcf.ensure_extension(bibliography_file)
			if bcf_file in self.__stamps['bib']:
				return self.__stamps['bib'][bcf_file]
		return ''

	def set_biber_stamp(self, bibliography_file : str, stamp : str):
		"""
		Replies the stamp that is associated to the BCF file.
		:param bibliography_file: the path of the bibliography file (bib, bbl, etc.) that may be associated to a BCF file.
		:type bibliography_file: str:
		:param stamp: the stamp value.
		:type stamp: str
		"""
		if 'bib' not in self.__stamps:
			self.__stamps['bib'] = dict()
		bcf_file = FileType.bcf.ensure_extension(bibliography_file)
		self.__stamps['bib'][bcf_file] = stamp

	def parse_biber(self, bibliography_file : str, update_stamps : bool) -> str:
		"""
		Parse the BCF file to detect the citations.
		:param bibliography_file: the path of the bibliography file (bib, bbl, etc.) that may be associated to a BCF file.
		:type bibliography_file: str:
		:param update_stamps: Indicates if the internal stamps must be updated from the computed stamp.
		:type update_stamps: bool:
		:return: the stamp value.
		:rtype: str
		"""
		bcf_file = FileType.bcf.ensure_extension(bibliography_file)
		bcf_analyzer = BiblatexCitationAnalyzer(bcf_file)
		current_md5 = bcf_analyzer.md5
		if update_stamps:
			if 'bib' not in self.__stamps:
				self.__stamps['bib'] = dict()
			self.__stamps['bib'][bcf_file] = current_md5
		return current_md5


	def get_bibtex_stamp(self, bibliography_file : str) -> str:
		"""
		Replies the stamp that is associated to the BibTeX auxiliary file.
		:param bibliography_file: the path of the bibliography file (bib, bbl, etc.) that may be associated to an auxiliary file.
		:type bibliography_file: str:
		:return: the stamp value.
		:rtype: str
		"""
		if 'bib' in self.__stamps:
			aux_file = FileType.aux.ensure_extension(bibliography_file)
			if aux_file in self.__stamps['bib']:
				return self.__stamps['bib'][aux_file]
		return ''

	def set_bibtex_stamp(self, bibliography_file : str, stamp : str):
		"""
		Replies the stamp that is associated to the BibTeX auxiliary file.
		:param bibliography_file: the path of the bibliography file (bib, bbl, etc.) that may be associated to an auxiliary file.
		:type bibliography_file: str:
		:param stamp: the stamp value.
		:type stamp: str
		"""
		if 'bib' not in self.__stamps:
			self.__stamps['bib'] = dict()
		aux_file = FileType.aux.ensure_extension(bibliography_file)
		self.__stamps['bib'][aux_file] = stamp

	def parse_bibtex(self, bibliography_file : str, update_stamps : bool) -> str:
		"""
		Parse the BibTeX auxiliary file to detect the citations.
		:param bibliography_file: the path of the bibliography file (bib, bbl, etc.) that may be associated to an auxiliary file.
		:type bibliography_file: str:
		:param update_stamps: Indicates if the internal stamps must be updated from the computed stamp.
		:type update_stamps: bool:
		:return: the stamp value.
		:rtype: str
		"""
		aux_file = FileType.aux.ensure_extension(bibliography_file)
		aux_analyzer = AuxiliaryCitationAnalyzer(aux_file)
		current_md5 = aux_analyzer.md5
		if update_stamps:
			if 'bib' not in self.__stamps:
				self.__stamps['bib'] = dict()
			self.__stamps['bib'][aux_file] = current_md5
		return current_md5


	def get_index_stamp(self, index_file : str) -> str:
		"""
		Replies the stamp that is associated to the index file.
		:param index_file: the path of the index file (idx, ind, etc.) that may be associated to an IDX index file.
		:type index_file: str:
		:return: the stamp value.
		:rtype: str
		"""
		if 'idx' in self.__stamps:
			idx_file = FileType.idx.ensure_extension(index_file)
			if idx_file in self.__stamps['idx']:
				return self.__stamps['idx'][idx_file]
		return ''

	def set_index_stamp(self, index_file : str, stamp : str):
		"""
		Replies the stamp that is associated to the index auxiliary file.
		:param index_file: the path of the index file (idx, ind, etc.) that may be associated to an IDX index file.
		:type index_file: str:
		:param stamp: the stamp value.
		:type stamp: str
		"""
		if 'idx' not in self.__stamps:
			self.__stamps['idx'] = dict()
		idx_file = FileType.idx.ensure_extension(index_file)
		self.__stamps['idx'][idx_file] = stamp

	def parse_index(self, index_file : str, update_stamps : bool) -> str:
		"""
		Parse the index auxiliary file to detect the citations.
		:param index_file: the path of the index file (idx, ind, etc.) that may be associated to an IDX index file.
		:type index_file: str:
		:param update_stamps: Indicates if the internal stamps must be updated from the computed stamp.
		:type update_stamps: bool:
		:return: the stamp value.
		:rtype: str
		"""
		idx_file = FileType.idx.ensure_extension(index_file)
		idx_analyzer = IndexAnalyzer(idx_file)
		current_md5 = idx_analyzer.md5
		if update_stamps:
			if 'idx' not in self.__stamps:
				self.__stamps['idx'] = dict()
			self.__stamps['idx'][idx_file] = current_md5
		return current_md5


	def get_glossary_stamp(self, glossary_file : str) -> str:
		"""
		Replies the stamp that is associated to the index file.
		:param glossary_file: the path of the glossary file (gls, glo, etc.) that may be associated to an GLS glossary file.
		:type glossary_file: str:
		:return: the stamp value.
		:rtype: str
		"""
		if 'gls' in self.__stamps:
			gls_file = FileType.gls.ensure_extension(glossary_file)
			if gls_file in self.__stamps['gls']:
				return self.__stamps['gls'][gls_file]
		return ''

	def set_glossary_stamp(self, glossary_file : str, stamp : str):
		"""
		Replies the stamp that is associated to the glossary auxiliary file.
		:param glossary_file: the path of the glossary file (gls, glo, etc.) that may be associated to an GLS glossary file.
		:type glossary_file: str:
		:param stamp: the stamp value.
		:type stamp: str
		"""
		if 'gls' not in self.__stamps:
			self.__stamps['gls'] = dict()
		gls_file = FileType.gls.ensure_extension(glossary_file)
		self.__stamps['gls'][gls_file] = stamp

	def parse_glossary(self, glossary_file : str, update_stamps : bool) -> str:
		"""
		Parse the glossary auxiliary file to detect the citations.
		:param glossary_file: the path of the glossary file (gls, glo, etc.) that may be associated to an GLS glossary file.
		:type glossary_file: str:
		:param update_stamps: Indicates if the internal stamps must be updated from the computed stamp.
		:type update_stamps: bool:
		:return: the stamp value.
		:rtype: str
		"""
		gls_file = FileType.gls.ensure_extension(glossary_file)
		gls_analyzer = GlossaryAnalyzer(gls_file)
		current_md5 = gls_analyzer.md5
		if update_stamps:
			if 'gls' not in self.__stamps:
				self.__stamps['gls'] = dict()
			self.__stamps['gls'][gls_file] = current_md5
		return current_md5
