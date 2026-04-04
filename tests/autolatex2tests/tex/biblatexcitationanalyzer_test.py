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

import unittest
import tempfile
import os
import logging

from autolatex2.tex import citationanalyzer
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestBiblatexCitationAnalyzer(AbstractBaseTest):

	BCFFILE : str =	"""
				<bcf:citekey>Weyns2007</bcf:citekey>
				<bcf:citekey>Badeig2010</bcf:citekey>
				<bcf:citekey>GallandGaud2014_701</bcf:citekey>
				<bcf:citekey>Saunier2014</bcf:citekey>
				<bcf:citekey>Odell.aose09</bcf:citekey>
				<bcf:citekey>Dey:1999</bcf:citekey>
				<bcf:citekey>Bhouri2012</bcf:citekey>
				<bcf:citekey>CrowdSimu.Thalmann.2007</bcf:citekey>
				<bcf:citekey>Michel.aamas07</bcf:citekey>
				<bcf:citekey>Rodriguez.iat14</bcf:citekey>
				<bcf:citekey>GallandGaud2014_701</bcf:citekey>
				<bcf:citekey>Tamminga2014</bcf:citekey>
				<bcf:citekey>Ricci2003</bcf:citekey>
				<bcf:citekey>Ricci2008</bcf:citekey>
				d21054b8-ce8a-4254-a3b3-727bf08ad962
				<bcf:citekey>CrowdSimu.Thalmann.2007</bcf:citekey>
				<bcf:citekey>Michel.aamas07</bcf:citekey>
				<bcf:citekey>Viroli2005</bcf:citekey>
				<bcf:citekey>CrowdSimu.Thalmann.2007</bcf:citekey>
				<bcf:citekey>Picault_JFSMA10</bcf:citekey>
				<bcf:citekey>Badeig2010</bcf:citekey>
				<bcf:citekey>Saunier2014</bcf:citekey>
				<bcf:citekey>Zargayouna2009</bcf:citekey>
				<bcf:citekey>AGRE.05</bcf:citekey>
				<bcf:citekey>Gouaich.informatica05</bcf:citekey>
				a6993cd6-9b60-47b3-bf9f-3679c346975c
				<bcf:citekey>Piunti_IAT09</bcf:citekey>
				<bcf:citekey>Viroli2005</bcf:citekey>
				<bcf:citekey>CrowdSimu.Thalmann.2007</bcf:citekey>
				<bcf:citekey>RodriguezHilaireGaudGallandKoukam2011_84</bcf:citekey>
				<bcf:citekey>GAMA13</bcf:citekey>
				<bcf:citekey>Badeig2010</bcf:citekey>
				<bcf:citekey>Bhouri2012</bcf:citekey>
				<bcf:citekey>Dey:1999</bcf:citekey>
				<bcf:citekey>AGRE.05</bcf:citekey>
				<bcf:citekey>GallandGaud2014_701</bcf:citekey>
				<bcf:citekey>Gouaich.informatica05</bcf:citekey>
				<bcf:citekey>GAMA13</bcf:citekey>
				<bcf:citekey>Michel.aamas07</bcf:citekey>
				<bcf:citekey>Odell.aose09</bcf:citekey>
				<bcf:citekey>Picault_JFSMA10</bcf:citekey>
				<bcf:citekey>Piunti_IAT09</bcf:citekey>
				<bcf:citekey>Ricci2003</bcf:citekey>
				<bcf:citekey>Viroli2005</bcf:citekey>
				<bcf:citekey>Ricci2008</bcf:citekey>
				<bcf:citekey>Rodriguez.iat14</bcf:citekey>
				<bcf:citekey>RodriguezHilaireGaudGallandKoukam2011_84</bcf:citekey>
				<bcf:citekey>Saunier2014</bcf:citekey>
				<bcf:citekey>Tamminga2014</bcf:citekey>
				<bcf:citekey>CrowdSimu.Thalmann.2007</bcf:citekey>
				<bcf:citekey>Weyns2007</bcf:citekey>
				<bcf:citekey>Zargayouna2009</bcf:citekey>
				"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__lastDirname = None
		self.__lastBasename = None
		self.__lastFilename = None
		self.analyzer = None

	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.analyzer = self.__run()

	def __run(self):
		f = tempfile.NamedTemporaryFile(delete=False)
		name = f.name
		self.__lastFilename = name
		self.__lastDirname = os.path.dirname(name)
		self.__lastBasename = os.path.basename(name)
		f.file.write(bytes(self.BCFFILE, 'UTF-8'))
		f.seek(0)
		f.close()
		analyzer = citationanalyzer.BiblatexCitationAnalyzer(name)
		analyzer.run()
		os.remove(name)
		return analyzer

	def test_basename(self):
		self.assertEqual(self.__lastBasename, self.analyzer.basename)

	def test_filename(self):
		self.assertEqual(self.__lastFilename, self.analyzer.filename)

	def test_citations(self):
		self.assertEqual([
				'AGRE.05',
				'Badeig2010',
				'Bhouri2012',
				'CrowdSimu.Thalmann.2007',
				'Dey:1999',
				'GAMA13',
				'GallandGaud2014_701',
				'Gouaich.informatica05',
				'Michel.aamas07',
				'Odell.aose09',
				'Picault_JFSMA10',
				'Piunti_IAT09',
				'Ricci2003',
				'Ricci2008',
				'Rodriguez.iat14',
				'RodriguezHilaireGaudGallandKoukam2011_84',
				'Saunier2014',
				'Tamminga2014',
				'Viroli2005',
				'Weyns2007',
				'Zargayouna2009'], self.analyzer.citations)

	def test_md5(self):
		self.assertEqual('bbd691129292d9bf59a69cd62f4b921d', self.analyzer.md5)


if __name__ == '__main__':
	unittest.main()

