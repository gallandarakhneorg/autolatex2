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
from logging import Handler
from typing import override

from autolatex2.utils import extlogging

from autolatex2.tex import citationanalyzer
from autolatex2tests.abstract_base_test import AbstractBaseTest


class TestIssue00001(AbstractBaseTest):
	"""
	Issue #1: Too restrictive definition of the \\gdef and \\def macros.
	"""

	AUXFILE: str = """
\\relax 
\\providecommand\\hyper@newdestlabel[2]{}
\\providecommand\\HyField@AuxAddToFields[1]{}
\\providecommand\\HyField@AuxAddToCoFields[2]{}
\\providecommand\\babel@aux[2]{}
\\@nameuse{bbl@beforestart}
\\providecommand \\oddpage@label [2]{}
\\babel@aux{english}{}
\\@writefile{nav}{\\headcommand {\\slideentry {0}{0}{1}{1/1}{}{0}}}
\\@writefile{nav}{\\headcommand {\\beamer@framepages {1}{1}}}
\\@writefile{nav}{\\headcommand {\\slideentry {0}{0}{2}{2/2}{}{0}}}
\\@writefile{nav}{\\headcommand {\\beamer@framepages {2}{2}}}
\\@writefile{nav}{\\headcommand {\\slideentry {0}{0}{3}{3/3}{}{0}}}
\\@writefile{nav}{\\headcommand {\\beamer@framepages {3}{3}}}
\\newlabel{frame3<1>}{{4}{4}{}{Doc-Start}{}}
\\@writefile{snm}{\\beamer@slide {frame3<1>}{4}}
\\newlabel{frame3}{{4}{4}{}{Doc-Start}{}}
\\@writefile{snm}{\\beamer@slide {frame3}{4}}
\\@writefile{nav}{\\headcommand {\\slideentry {0}{0}{4}{4/4}{}{0}}}
\\@writefile{nav}{\\headcommand {\\beamer@framepages {4}{4}}}
\\@writefile{nav}{\\headcommand {\\slideentry {0}{0}{5}{5/5}{}{0}}}
\\@writefile{nav}{\\headcommand {\\beamer@framepages {5}{5}}}
\\@writefile{nav}{\\headcommand {\\partentry {Appendix}{8}}}
\\@writefile{nav}{\\headcommand {\\beamer@partpages {509}{537}}}
\\@writefile{nav}{\\headcommand {\\beamer@sectionpages {509}{537}}}
\\@writefile{nav}{\\headcommand {\\beamer@subsectionpages {509}{537}}}
\\@writefile{nav}{\\headcommand {\\slideentry {0}{0}{13}{538/538}{}{8}}}
\\@writefile{nav}{\\headcommand {\\beamer@framepages {538}{538}}}
\\@writefile{nav}{\\headcommand {\\gdef \\insertmainframenumber {454}}}
\\@writefile{nav}{\\headcommand{\\beamer@theme@ciad@definesectionframenumber{8}{0}{1}}}
\\@writefile{nav}{\\headcommand {\\beamer@appendixpages {539}}}
\\@writefile{toc}{\\beamer@sectionintoc {1}{Document License}{539}{8}{1}}
\\@writefile{nav}{\\headcommand {\\beamer@sectionpages {538}{538}}}
\\@writefile{nav}{\\headcommand {\\beamer@subsectionpages {538}{538}}}
\\@writefile{nav}{\\headcommand {\\sectionentry {1}{Document License}{539}{Document License}{8}}}
\\@writefile{nav}{\\headcommand {\\slideentry {1}{0}{1}{539/539}{}{8}}}
\\@writefile{nav}{\\headcommand {\\beamer@framepages {539}{539}}}
\\@writefile{nav}{\\headcommand {\\slideentry {1}{0}{2}{540/540}{}{8}}}
\\@writefile{nav}{\\headcommand {\\beamer@framepages {540}{540}}}
\\@writefile{nav}{\\headcommand{\\beamer@theme@ciad@definesectionframenumber{8}{1}{2}}}
\\@writefile{nav}{\\headcommand {\\slideentry {3}{0}{2}{560/560}{}{8}}}
\\@writefile{nav}{\\headcommand {\\beamer@framepages {560}{560}}}
\\@writefile{nav}{\\headcommand {\\beamer@partpages {538}{560}}}
\\@writefile{nav}{\\headcommand {\\beamer@subsectionpages {559}{560}}}
\\@writefile{nav}{\\headcommand {\\beamer@sectionpages {559}{560}}}
\\@writefile{nav}{\\headcommand {\\beamer@documentpages {560}}}
\\@writefile{nav}{\\headcommand {\\gdef    \\inserttotalframenumber {476}}}
\\@writefile{nav}{\\headcommand{\\beamer@theme@ciad@definesectionframenumber{8}{3}{2}}}
\\@writefile{nav}{\\headcommand {\\def \n   \\inserttotalcoreframenumber {452}}}
\\gdef \\@abspage@last{560}
				"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__last_filename = None

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__temporary_file = tempfile.NamedTemporaryFile(delete=False)
		name = self.__temporary_file.name
		self.__last_filename = name
		self.__temporary_file.file.write(bytes(self.AUXFILE, 'UTF-8'))
		self.__temporary_file.seek(0)
		self.__temporary_file.close()

		class TestMessageHandler(Handler):
			def __init__(self):
				super().__init__(logging.DEBUG)
				self.messages : dict[int,list[str]] = dict()

			@override
			def filter(self, record):
				return record

			@override
			def emit(self, record : logging.LogRecord):
				msg = record.msg
				level = record.levelno
				if level not in self.messages:
					self.messages[level] = list()
				self.messages[level].append(msg)

		self.__message_handler = TestMessageHandler()
		logging.root.addHandler(self.__message_handler)
		logging.root.setLevel(extlogging.LogLevel.FINE_WARNING)

	@override
	def tearDown(self):
		if self.__temporary_file is not None:
			os.unlink(self.__last_filename)

	def test_no_warning(self):
		"""
		Check no warning
		"""
		analyzer = citationanalyzer.AuxiliaryCitationAnalyzer(self.__last_filename)
		analyzer.run()

		if extlogging.LogLevel.FINE_WARNING in self.__message_handler.messages:
			fine_warnings = self.__message_handler.messages[extlogging.LogLevel.FINE_WARNING]
			if fine_warnings is not None:
				self.assertEqual(0, len(fine_warnings), "Unexpected value: " + str(fine_warnings))


if __name__ == '__main__':
	unittest.main()

