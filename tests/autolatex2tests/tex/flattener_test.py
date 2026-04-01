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
import os
import re
import logging
from typing import override

from autolatex2.tex import flattener
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestFlattener(AbstractBaseTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__inputs = None
		self.__outputs = None
		self.__flattener = None
		self.__tmpFolderName = None

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__inputs = {}
		self.__outputs = {}
		self.__flattener = None
		self.__tmpFolderName = None

	@property
	def inputs(self):
		return self.__inputs

	@inputs.setter
	def inputs(self, i):
		self.__inputs = i

	@property
	def outputs(self):
		return self.__outputs

	@outputs.setter
	def outputs(self, o):
		self.__outputs = o

	@property
	def flattener(self):
		return self.__flattener

	# noinspection PyMethodMayBeStatic
	def __normalize(self, text : str) -> str:
		content = list()
		for line in text.split('\n'):
			line = line.strip()
			if line:
				line = re.sub(r'\t+', ' ', line).strip()
			if line:
				content.append(line)
		return '\n'.join(content).strip()

	def assertFlat(self, input_file : str, use_biblio : bool = False):
		with self._create_temp_directory(delete=True) as directory:
			self.__tmpFolderName = directory
			for k, expected in self.__inputs.items():
				odir = os.path.dirname(os.path.join(directory, k))
				if not os.path.isdir(odir):
					os.makedirs(odir)
				with open(os.path.join(directory, k), 'w') as document:
					document.write(expected)
					document.flush()
			output = os.path.join(directory, 'output')
			self.__flattener = flattener.Flattener(os.path.join(directory, input_file), output,
												   include_extra_macros=True)
			self.__flattener.use_biblio = use_biblio
			self.__flattener.run()
			for k, expected in self.__outputs.items():
				expected = self.__normalize(expected)
				with open(os.path.join(output, k)) as out:
					actual = out.read()
				actual = self.__normalize(actual)
				self.assertEqual(expected, actual)
			for dirname, dirnames, filenames in os.walk(output):
				for f in filenames:
					self.assertIn(f, self.__outputs)
			


	def test_input(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\input{myfile}
			\end{document}
			''',
			'myfile.tex' : r'blablabla' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}

			%=======================================================
			%== BEGIN FILE: myfile.tex
			%=======================================================
			blablabla
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_include(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\include{myfile}
			\end{document}
			''',
			'myfile.tex' : r'blablabla' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}

			%=======================================================
			%== BEGIN FILE: myfile.tex
			%=======================================================
			blablabla
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_usepackage_standard(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{babel}
			\begin{document}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{babel}
			\begin{document}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_usepackage_local_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{mypackage}
			\begin{document}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{mypackage}
			\begin{document}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_usepackage_local_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{mypackage}
			\begin{document}
			\end{document}
			''',
			'mypackage.sty' : r'''\def\toto{}''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{filecontents}

			\begin{filecontents*}{mypackage.sty}
			\def\toto{}
			\end{filecontents*}
			\usepackage{mypackage}
			\begin{document}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_requirepackage_standard(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\RequirePackage{babel}
			\begin{document}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\RequirePackage{babel}
			\begin{document}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_requirepackage_local_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\RequirePackage{mypackage}
			\begin{document}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\RequirePackage{mypackage}
			\begin{document}
			\end{document}
			''' }
		self.assertFlat('doc.tex')


	def test_requirepackage_local_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\RequirePackage{mypackage}
			\begin{document}
			\end{document}
			''',
			'mypackage.sty' : r'''\def\toto{}''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{filecontents}

			\begin{filecontents*}{mypackage.sty}
			\def\toto{}
			\end{filecontents*}
			\RequirePackage{mypackage}
			\begin{document}
			\end{document}
			''' }
		self.assertFlat('doc.tex')


	def test_documentclass_standard(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_documentclass_local_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_documentclass_local_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\end{document}
			''',
			'myclass.cls' : r'''\def\toto{}''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\end{document}
			''',
			'myclass.cls' : r'''\def\toto{}''' }
		self.assertFlat('doc.tex')



	def test_graphicspath(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\graphicspath{{./img/},{./img/auto}}
			\begin{document}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\graphicspath{{./}}
			\begin{document}
			\end{document}
			''' }
		self.assertFlat('doc.tex')
		ref = [	os.path.join(self.__tmpFolderName, './img/auto'),
				os.path.join(self.__tmpFolderName, './img/'),
				self.__tmpFolderName ]
		self.assertListEqual(ref, self.flattener.include_paths)



	def test_includegraphics_standard(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\includegraphics{figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\includegraphics{figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includegraphics_local_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includegraphics{figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includegraphics{figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includegraphics_local_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includegraphics{figure}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includegraphics{figure.pdf}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_includegraphics_localsub1_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includegraphics{./imgs/figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includegraphics{./imgs/figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includegraphics_localsub1_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includegraphics{./imgs/figure}
			\end{document}
			''',
			'imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includegraphics{figure.pdf}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_includegraphics_localsub2_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\includegraphics{figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\includegraphics{figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includegraphics_localsub2_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\includegraphics{figure}
			\end{document}
			''',
			'imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\includegraphics{figure.pdf}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_includeanimatedfigure_standard(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\includeanimatedfigure{figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\includeanimatedfigure{figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includeanimatedfigure_local_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includeanimatedfigure{figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includeanimatedfigure{figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includeanimatedfigure_local_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includeanimatedfigure{figure}
			\end{document}
			''',
			'figure.pdf_tex' : r'''\includegraphics{figure.pdf}''',
			'figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\usepackage{filecontents}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: figure.pdf_tex
			%=======================================================
			\begin{filecontents*}{figure.pdf_tex}
			\includegraphics{figure.pdf}
			\end{filecontents*}
			%=======================================================
			\includeanimatedfigure{figure.pdf_tex}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_includeanimatedfigure_localsub1_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includeanimatedfigure{./imgs/figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includeanimatedfigure{./imgs/figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includeanimatedfigure_localsub1_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includeanimatedfigure{./imgs/figure}
			\end{document}
			''',
			'./imgs/figure.pdf_tex' : r'''\includegraphics{figure.pdf}''',
			'./imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\usepackage{filecontents}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: figure.pdf_tex
			%=======================================================
			\begin{filecontents*}{figure.pdf_tex}
			\includegraphics{figure.pdf}
			\end{filecontents*}
			%=======================================================
			\includeanimatedfigure{figure.pdf_tex}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_includeanimatedfigure_localsub2_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\includeanimatedfigure{figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\includeanimatedfigure{figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includeanimatedfigure_localsub2_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\includeanimatedfigure{figure}
			\end{document}
			''',
			'imgs/figure.pdf_tex' : r'''\includegraphics{figure.pdf}''',
			'imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\usepackage{filecontents}
			\graphicspath{{./}}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: figure.pdf_tex
			%=======================================================
			\begin{filecontents*}{figure.pdf_tex}
			\includegraphics{figure.pdf}
			\end{filecontents*}
			%=======================================================
			\includeanimatedfigure{figure.pdf_tex}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')


	def test_includeanimatedfigurewtex_standard(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\includeanimatedfigurewtex{figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\includeanimatedfigurewtex{figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includeanimatedfigurewtex_local_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includeanimatedfigurewtex{figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includeanimatedfigurewtex{figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includeanimatedfigurewtex_local_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includeanimatedfigurewtex{figure}
			\end{document}
			''',
			'figure.pdf_tex' : r'''\includegraphics{figure.pdf}''',
			'figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\usepackage{filecontents}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: figure.pdf_tex
			%=======================================================
			\begin{filecontents*}{figure.pdf_tex}
			\includegraphics{figure.pdf}
			\end{filecontents*}
			%=======================================================
			\includeanimatedfigurewtex{figure.pdf_tex}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_includeanimatedfigurewtex_localsub1_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includeanimatedfigurewtex{./imgs/figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includeanimatedfigurewtex{./imgs/figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includeanimatedfigurewtex_localsub1_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includeanimatedfigurewtex{./imgs/figure}
			\end{document}
			''',
			'./imgs/figure.pdf_tex' : r'''\includegraphics{figure.pdf}''',
			'./imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\usepackage{filecontents}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: figure.pdf_tex
			%=======================================================
			\begin{filecontents*}{figure.pdf_tex}
			\includegraphics{figure.pdf}
			\end{filecontents*}
			%=======================================================
			\includeanimatedfigurewtex{figure.pdf_tex}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_includeanimatedfigurewtex_localsub2_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\includeanimatedfigurewtex{figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\includeanimatedfigurewtex{figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includeanimatedfigurewtex_localsub2_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\includeanimatedfigurewtex{figure}
			\end{document}
			''',
			'imgs/figure.pdf_tex' : r'''\includegraphics{figure.pdf}''',
			'imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\usepackage{filecontents}
			\graphicspath{{./}}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: figure.pdf_tex
			%=======================================================
			\begin{filecontents*}{figure.pdf_tex}
			\includegraphics{figure.pdf}
			\end{filecontents*}
			%=======================================================
			\includeanimatedfigurewtex{figure.pdf_tex}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_includegraphicswtex_standard(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\includegraphicswtex{figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\includegraphicswtex{figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includegraphicswtex_local_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includegraphicswtex{figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includegraphicswtex{figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includegraphicswtex_local_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includegraphicswtex{figure}
			\end{document}
			''',
			'figure.pdf_tex' : r'''\includegraphics{figure.pdf}''',
			'figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\usepackage{filecontents}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: figure.pdf_tex
			%=======================================================
			\begin{filecontents*}{figure.pdf_tex}
			\includegraphics{figure.pdf}
			\end{filecontents*}
			%=======================================================
			\includegraphicswtex{figure.pdf_tex}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_includegraphicswtex_localsub1_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includegraphicswtex{./imgs/figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includegraphicswtex{./imgs/figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includegraphicswtex_localsub1_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includegraphicswtex{./imgs/figure}
			\end{document}
			''',
			'./imgs/figure.pdf_tex' : r'''\includegraphics{figure.pdf}''',
			'./imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\usepackage{filecontents}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: figure.pdf_tex
			%=======================================================
			\begin{filecontents*}{figure.pdf_tex}
			\includegraphics{figure.pdf}
			\end{filecontents*}
			%=======================================================
			\includegraphicswtex{figure.pdf_tex}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_includegraphicswtex_localsub2_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\includegraphicswtex{figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\includegraphicswtex{figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includegraphicswtex_localsub2_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\includegraphicswtex{figure}
			\end{document}
			''',
			'imgs/figure.pdf_tex' : r'''\includegraphics{figure.pdf}''',
			'imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\usepackage{filecontents}
			\graphicspath{{./}}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: figure.pdf_tex
			%=======================================================
			\begin{filecontents*}{figure.pdf_tex}
			\includegraphics{figure.pdf}
			\end{filecontents*}
			%=======================================================
			\includegraphicswtex{figure.pdf_tex}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_includefigurewtex_standard(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\includefigurewtex{figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\includefigurewtex{figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includefigurewtex_local_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includefigurewtex{figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includefigurewtex{figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includefigurewtex_local_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includefigurewtex{figure}
			\end{document}
			''',
			'figure.pdf_tex' : r'''\includegraphics{figure.pdf}''',
			'figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\usepackage{filecontents}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: figure.pdf_tex
			%=======================================================
			\begin{filecontents*}{figure.pdf_tex}
			\includegraphics{figure.pdf}
			\end{filecontents*}
			%=======================================================
			\includefigurewtex{figure.pdf_tex}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_includefigurewtex_localsub1_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includefigurewtex{./imgs/figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includefigurewtex{./imgs/figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includefigurewtex_localsub1_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\includefigurewtex{./imgs/figure}
			\end{document}
			''',
			'./imgs/figure.pdf_tex' : r'''\includegraphics{figure.pdf}''',
			'./imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\usepackage{filecontents}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: figure.pdf_tex
			%=======================================================
			\begin{filecontents*}{figure.pdf_tex}
			\includegraphics{figure.pdf}
			\end{filecontents*}
			%=======================================================
			\includefigurewtex{figure.pdf_tex}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_includefigurewtex_localsub2_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\includefigurewtex{figure}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\includefigurewtex{figure}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_includefigurewtex_localsub2_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\includefigurewtex{figure}
			\end{document}
			''',
			'imgs/figure.pdf_tex' : r'''\includegraphics{figure.pdf}''',
			'imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\usepackage{filecontents}
			\graphicspath{{./}}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: figure.pdf_tex
			%=======================================================
			\begin{filecontents*}{figure.pdf_tex}
			\includegraphics{figure.pdf}
			\end{filecontents*}
			%=======================================================
			\includefigurewtex{figure.pdf_tex}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_mfigure_standard(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\mfigure{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\mfigure{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_mfigure_local_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigure{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigure{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_mfigure_local_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigure{param1}{figure}{param3}{param4}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigure{param1}{figure.pdf}{param3}{param4}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_mfigure_localsub1_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigure{param1}{./imgs/figure}{param3}{param4}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigure{param1}{./imgs/figure}{param3}{param4}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_mfigure_localsub1_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigure{param1}{./imgs/figure}{param3}{param4}
			\end{document}
			''',
			'./imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigure{param1}{figure.pdf}{param3}{param4}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_mfigure_localsub2_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\mfigure{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\mfigure{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_mfigure_localsub2_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\mfigure{param1}{figure}{param3}{param4}
			\end{document}
			''',
			'imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\mfigure{param1}{figure.pdf}{param3}{param4}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_mfigurestar_standard(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\mfigure*{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\mfigure*{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_mfigurestar_local_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigure*{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigure*{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_mfigurestar_local_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigure*{param1}{figure}{param3}{param4}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigure*{param1}{figure.pdf}{param3}{param4}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_mfigurestar_localsub1_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigure*{param1}{./imgs/figure}{param3}{param4}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigure*{param1}{./imgs/figure}{param3}{param4}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_mfigurestar_localsub1_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigure*{param1}{./imgs/figure}{param3}{param4}
			\end{document}
			''',
			'./imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigure*{param1}{figure.pdf}{param3}{param4}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_mfigurestar_localsub2_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\mfigure*{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\mfigure*{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_mfigurestar_localsub2_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\mfigure*{param1}{figure}{param3}{param4}
			\end{document}
			''',
			'imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\mfigure*{param1}{figure.pdf}{param3}{param4}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_msubfigure_standard(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\msubfigure{param1}{figure}{param3}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\msubfigure{param1}{figure}{param3}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_msubfigure_local_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\msubfigure{param1}{figure}{param3}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\msubfigure{param1}{figure}{param3}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_msubfigure_local_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\msubfigure{param1}{figure}{param3}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\msubfigure{param1}{figure.pdf}{param3}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_msubfigure_localsub1_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\msubfigure{param1}{./imgs/figure}{param3}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\msubfigure{param1}{./imgs/figure}{param3}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_msubfigure_localsub1_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\msubfigure{param1}{./imgs/figure}{param3}
			\end{document}
			''',
			'./imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\msubfigure{param1}{figure.pdf}{param3}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_msubfigure_localsub2_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\msubfigure{param1}{figure}{param3}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\msubfigure{param1}{figure}{param3}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_msubfigure_localsub2_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\msubfigure{param1}{figure}{param3}
			\end{document}
			''',
			'imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\msubfigure{param1}{figure.pdf}{param3}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_msubfigurestar_standard(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\msubfigure*{param1}{figure}{param3}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\msubfigure*{param1}{figure}{param3}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_msubfigurestar_local_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\msubfigure*{param1}{figure}{param3}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\msubfigure*{param1}{figure}{param3}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_msubfigurestar_local_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\msubfigure*{param1}{figure}{param3}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\msubfigure*{param1}{figure.pdf}{param3}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_msubfigurestar_localsub1_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\msubfigure*{param1}{./imgs/figure}{param3}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\msubfigure*{param1}{./imgs/figure}{param3}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_msubfigurestar_localsub1_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\msubfigure*{param1}{./imgs/figure}{param3}
			\end{document}
			''',
			'./imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\msubfigure*{param1}{figure.pdf}{param3}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_msubfigurestar_localsub2_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\msubfigure*{param1}{figure}{param3}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\msubfigure*{param1}{figure}{param3}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_msubfigurestar_localsub2_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\msubfigure*{param1}{figure}{param3}
			\end{document}
			''',
			'imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\msubfigure*{param1}{figure.pdf}{param3}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_mfigurewtex_standard(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\mfigurewtex{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\mfigurewtex{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_mfigurewtex_local_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigurewtex{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigurewtex{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_mfigurewtex_local_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigurewtex{param1}{figure}{param3}{param4}
			\end{document}
			''',
			'figure.pdf_tex' : r'''\includegraphics{figure.pdf}''',
			'figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\usepackage{filecontents}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: figure.pdf_tex
			%=======================================================
			\begin{filecontents*}{figure.pdf_tex}
			\includegraphics{figure.pdf}
			\end{filecontents*}
			%=======================================================
			\mfigurewtex{param1}{figure.pdf_tex}{param3}{param4}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_mfigurewtex_localsub1_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigurewtex{param1}{./imgs/figure}{param3}{param4}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigurewtex{param1}{./imgs/figure}{param3}{param4}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_mfigurewtex_localsub1_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigurewtex{param1}{./imgs/figure}{param3}{param4}
			\end{document}
			''',
			'./imgs/figure.pdf_tex' : r'''\includegraphics{figure.pdf}''',
			'./imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\usepackage{filecontents}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: figure.pdf_tex
			%=======================================================
			\begin{filecontents*}{figure.pdf_tex}
			\includegraphics{figure.pdf}
			\end{filecontents*}
			%=======================================================
			\mfigurewtex{param1}{figure.pdf_tex}{param3}{param4}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_mfigurewtex_localsub2_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\mfigurewtex{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\mfigurewtex{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_mfigurewtex_localsub2_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\mfigurewtex{param1}{figure}{param3}{param4}
			\end{document}
			''',
			'imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\mfigurewtex{param1}{figure.pdf}{param3}{param4}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_mfigurewtexstar_standard(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\mfigurewtex*{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\mfigurewtex*{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_mfigurewtexstar_local_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigurewtex*{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigurewtex*{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_mfigurewtexstar_local_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigurewtex*{param1}{figure}{param3}{param4}
			\end{document}
			''',
			'figure.pdf_tex' : r'''\includegraphics{figure.pdf}''',
			'figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\usepackage{filecontents}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: figure.pdf_tex
			%=======================================================
			\begin{filecontents*}{figure.pdf_tex}
			\includegraphics{figure.pdf}
			\end{filecontents*}
			%=======================================================
			\mfigurewtex*{param1}{figure.pdf_tex}{param3}{param4}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_mfigurewtexstar_localsub1_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigurewtex*{param1}{./imgs/figure}{param3}{param4}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigurewtex*{param1}{./imgs/figure}{param3}{param4}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_mfigurewtexstar_localsub1_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\begin{document}
			\mfigurewtex*{param1}{./imgs/figure}{param3}{param4}
			\end{document}
			''',
			'./imgs/figure.pdf_tex' : r'''\includegraphics{figure.pdf}''',
			'./imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\usepackage{filecontents}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: figure.pdf_tex
			%=======================================================
			\begin{filecontents*}{figure.pdf_tex}
			\includegraphics{figure.pdf}
			\end{filecontents*}
			%=======================================================
			\mfigurewtex*{param1}{figure.pdf_tex}{param3}{param4}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_mfigurewtexstar_localsub2_noFile(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\mfigurewtex*{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\mfigurewtex*{param1}{figure}{param3}{param4}
			\end{document}
			''' }
		self.assertFlat('doc.tex')



	def test_mfigurewtexstar_localsub2_file(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./imgs/}}
			\begin{document}
			\mfigurewtex*{param1}{figure}{param3}{param4}
			\end{document}
			''',
			'imgs/figure.pdf' : r'''MYPDF''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{myclass}
			\graphicspath{{./}}
			\begin{document}
			\mfigurewtex*{param1}{figure.pdf}{param3}{param4}
			\end{document}
			''',
			'figure.pdf' : r'''MYPDF''' }
		self.assertFlat('doc.tex')



	def test_addbibresource_onebase_noFile_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\addbibresource{mybiblio}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_addbibresource_onebase_file_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\addbibresource{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_addbibresource_twobases_noFile_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\addbibresource{mybiblio,mybiblio2}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_addbibresource_twobases_file_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\addbibresource{mybiblio,mybiblio2}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO',
			'mybiblio2.bib': 'BIBLIO2'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_addbibresource_twobases_sublocalfile_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\addbibresource{subfolder/mybiblio}
			\end{document}
			''',
			'subfolder/mybiblio.bib': 'BIBLIO',
			'mybiblio2.bib': 'BIBLIO2'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_addbibresource_onebase_noFile_usebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			\addbibresource{mybiblio}
			\end{document}
			'''}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			\addbibresource{mybiblio}
			\end{document}
			'''}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_addbibresource_onebase_file_usebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			\addbibresource{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO'}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			\addbibresource{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_addbibresource_onebase_localsubfile_usebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			\addbibresource{myfolder/mybiblio}
			\end{document}
			''',
			'myfolder/mybiblio.bib': 'BIBLIO'}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			\addbibresource{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_addbibresource_twobases_noFile_usebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			\addbibresource{mybiblio,mybiblio2}
			\end{document}
			'''}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			\addbibresource{mybiblio,mybiblio2}
			\end{document}
			'''}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_addbibresource_twobases_file_usebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			\addbibresource{mybiblio,mybiblio2}
			\end{document}
			''',
		   'mybiblio.bib': 'BIBLIO',
		   'mybiblio2.bib': 'BIBLIO2'}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			\addbibresource{mybiblio,mybiblio2}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO',
			'mybiblio2.bib': 'BIBLIO2'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)


	def test_printbibliography_onebase_noFile_nousebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\addbibresource{mybiblio}
			\begin{document}
			\printbibliography
			\end{document}
			'''}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_printbibliography_onebase_file_nousebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\addbibresource{mybiblio}
			\begin{document}
			\printbibliography
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO',
			'doc.bbl': 'BIBLIO ENTRIES'}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: doc.bbl
			%=======================================================
			BIBLIO ENTRIES
			%=======================================================
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_printbibliography_twobases_noFile_nousebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\addbibresource{mybiblio,mybiblio2}
			\begin{document}
			\printbibliography
			\end{document}
			'''}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_printbibliography_twobases_file_nousebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\addbibresource{mybiblio,mybiblio2}
			\begin{document}
			\printbibliography
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO',
			'mybiblio2.bib': 'BIBLIO2',
			'doc.bbl': 'BIBLIO ENTRIES'}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: doc.bbl
			%=======================================================
			BIBLIO ENTRIES
			%=======================================================
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_printbibliography_onebase_noFile_usebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\addbibresource{mybiblio}
			\begin{document}
			\printbibliography
			\end{document}
			'''}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\addbibresource{mybiblio}
			\begin{document}
			\printbibliography
			\end{document}
			'''}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_printbibliography_onebase_file_usebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\addbibresource{mybiblio}
			\begin{document}
			\printbibliography
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO',
			'doc.bbl': 'BIBLIO ENTRIES'}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\addbibresource{mybiblio}
			\begin{document}
			\printbibliography
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_printbibliography_twobases_noFile_usebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\addbibresource{mybiblio,mybiblio2}
			\begin{document}
			\printbibliography
			\end{document}
			'''}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\addbibresource{mybiblio,mybiblio2}
			\begin{document}
			\printbibliography
			\end{document}
			'''}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_printbibliography_twobases_file_usebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\addbibresource{mybiblio,mybiblio2}
			\begin{document}
			\printbibliography
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO',
			'mybiblio2.bib': 'BIBLIO2',
			'doc.bbl': 'BIBLIO ENTRIES'}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\addbibresource{mybiblio,mybiblio2}
			\begin{document}
			\printbibliography
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO',
			'mybiblio2.bib': 'BIBLIO2'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)



	def test_bibunit_nobase_noFile_nousebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			'''}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibunit_nobase_file_nousebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			''',
			'doc.bib': 'BIBLIO',
			'doc.bbl': 'GENERAL BIBLIO ENTRIES',
			'doc.1.bbl': 'SPECIFIC BIBLIO ENTRIES'}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: doc.1.bbl
			%=======================================================
			SPECIFIC BIBLIO ENTRIES
			%=======================================================
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibunit_onebase_noFile_nousebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\putbib[mybiblio]
			\end{bibunit}
			\end{document}
			'''}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibunit_onebase_file_nousebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\putbib[mybiblio]
			\end{bibunit}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO',
			'doc.bbl': 'GENERAL BIBLIO ENTRIES',
			'doc.1.bbl': 'SPECIFIC BIBLIO ENTRIES'}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: doc.1.bbl
			%=======================================================
			SPECIFIC BIBLIO ENTRIES
			%=======================================================
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibunit_twobases_noFile_nousebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\putbib[mybiblio,mybiblio2]
			\end{bibunit}
			\end{document}
			'''}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibunit_twobases_file_nousebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\putbib[mybiblio,mybiblio2]
			\end{bibunit}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO',
			'mybiblio2.bib': 'BIBLIO2',
			'doc.bbl': 'GENERAL BIBLIO ENTRIES',
			'doc.1.bbl': 'SPECIFIC BIBLIO ENTRIES'}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: doc.1.bbl
			%=======================================================
			SPECIFIC BIBLIO ENTRIES
			%=======================================================
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibunit_twounits_nousebib(self):
		self.inputs = {'doc.tex': r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\putbib[mybiblio]
			\end{bibunit}
			\begin{bibunit}
			\putbib[mybiblio2]
			\end{bibunit}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO',
			'mybiblio2.bib': 'BIBLIO2',
			'doc.bbl': 'GENERAL BIBLIO ENTRIES',
			'doc.1.bbl': 'SPECIFIC BIBLIO ENTRIES',
			'doc.2.bbl': 'OTHER BIBLIO ENTRIES'}
		self.outputs = {'doc.tex': r'''
			\documentclass{article}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: doc.1.bbl
			%=======================================================
			SPECIFIC BIBLIO ENTRIES
			%=======================================================
			%=======================================================
			%== BEGIN FILE: doc.2.bbl
			%=======================================================
			OTHER BIBLIO ENTRIES
			%=======================================================
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)



	def test_bibliography_nobibfile_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliography{mybiblio}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliography{mybiblio}
			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibliography_nobblfile_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliography{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliography{mybiblio}
			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibliography_file_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliography{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO',
			'doc.bbl': 'BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: doc.bbl
			%=======================================================
			BIBLIO ENTRIES
			%=======================================================
			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibliography_subfile_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliography{mysubfolder/mybiblio}
			\end{document}
			''',
			'mysubfolder/mybiblio.bib': 'BIBLIO',
			'doc.bbl': 'BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: doc.bbl
			%=======================================================
			BIBLIO ENTRIES
			%=======================================================
			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibliography_nobibfile_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliography{mybiblio}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliography{mybiblio}
			\end{document}
			''' }
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_bibliography_nobblfile_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliography{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliography{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_bibliography_file_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliography{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO',
			'doc.bbl': 'BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliography{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_bibliography_subfile_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliography{mysubfolder/mybiblio}
			\end{document}
			''',
			'mysubfolder/mybiblio.bib': 'BIBLIO',
			'doc.bbl': 'BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliography{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)



	def test_bibliographyXXX_nobibfile_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographyXXX{mybiblio}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographyXXX{mybiblio}
			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibliographyXXX_nobblfile_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographyXXX{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographyXXX{mybiblio}
			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibliographyXXX_file_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographyXXX{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO',
			'doc.bbl': 'BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: doc.bbl
			%=======================================================
			BIBLIO ENTRIES
			%=======================================================
			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibliographyXXX_subfile_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographyXXX{mysubfolder/mybiblio}
			\end{document}
			''',
			'mysubfolder/mybiblio.bib': 'BIBLIO',
			'doc.bbl': 'BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: doc.bbl
			%=======================================================
			BIBLIO ENTRIES
			%=======================================================
			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibliographyXXX_nobibfile_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographyXXX{mybiblio}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographyXXX{mybiblio}
			\end{document}
			''' }
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_bibliographyXXX_nobblfile_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographyXXX{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographyXXX{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_bibliographyXXX_file_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographyXXX{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO',
			'doc.bbl': 'BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographyXXX{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_bibliographyXXX_subfile_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographyXXX{mysubfolder/mybiblio}
			\end{document}
			''',
			'mysubfolder/mybiblio.bib': 'BIBLIO',
			'doc.bbl': 'BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographyXXX{mybiblio}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)





	def test_bibliographystyle_standard_nobib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyle{alpha}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}

			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)



	def test_bibliographystyle_local_noFile_nobib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyle{mystyle}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}

			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)



	def test_bibliographystyle_local_file_nobib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyle{mystyle}
			\end{document}
			''',
			'mystyle.bst' : r'''MYBIBLIO''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}

			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)



	def test_bibliographystyle_localsub1_noFile_nobib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyle{./biblio/mystyle}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}

			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)



	def test_bibliographystyle_localsub1_file_nobib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyle{./biblio/mystyle}
			\end{document}
			''',
			'./biblio/mybiblio.bbl' : r'''MYBIBLIO''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}

			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)



	def test_bibliographystyle_standard_bib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyle{alpha}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyle{alpha}
			\end{document}
			''' }
		self.assertFlat('doc.tex', True)
		self.assertTrue(self.flattener.use_biblio)



	def test_bibliographystyle_local_noFile_bib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyle{mystyle}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyle{mystyle}
			\end{document}
			''' }
		self.assertFlat('doc.tex', True)
		self.assertTrue(self.flattener.use_biblio)



	def test_bibliographystyle_local_file_bib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyle{mystyle}
			\end{document}
			''',
			'mystyle.bst' : r'''MYBIBLIO''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyle{mystyle}
			\end{document}
			''',
			'mystyle.bst' : r'''MYBIBLIO''' }
		self.assertFlat('doc.tex', True)
		self.assertTrue(self.flattener.use_biblio)



	def test_bibliographystyle_localsub1_noFile_bib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyle{./biblio/mystyle}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyle{./biblio/mystyle}
			\end{document}
			''' }
		self.assertFlat('doc.tex', True)
		self.assertTrue(self.flattener.use_biblio)



	def test_bibliographystyle_localsub1_file_bib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyle{./biblio/mystyle}
			\end{document}
			''',
			'./biblio/mystyle.bst' : r'''MYBIBLIO''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyle{mystyle}
			\end{document}
			''',
			'mystyle.bst' : r'''MYBIBLIO''' }
		self.assertFlat('doc.tex', True)
		self.assertTrue(self.flattener.use_biblio)



	def test_bibliographystyleXXX_standard_nobib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyleXXX{alpha}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}

			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)



	def test_bibliographystyleXXX_local_noFile_nobib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyleXXX{mystyle}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}

			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)



	def test_bibliographystyleXXX_local_file_nobib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyleXXX{mystyle}
			\end{document}
			''',
			'mystyle.bst' : r'''MYBIBLIO''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}

			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)



	def test_bibliographystyleXXX_localsub1_noFile_nobib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyleXXX{./biblio/mystyle}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}

			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)



	def test_bibliographystyleXXX_localsub1_file_nobib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyleXXX{./biblio/mystyle}
			\end{document}
			''',
			'./biblio/mybiblio.bbl' : r'''MYBIBLIO''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}

			\end{document}
			''' }
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)



	def test_bibliographystyleXXX_standard_bib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyleXXX{alpha}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyleXXX{alpha}
			\end{document}
			''' }
		self.assertFlat('doc.tex', True)
		self.assertTrue(self.flattener.use_biblio)



	def test_bibliographystyleXXX_local_noFile_bib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyleXXX{mystyle}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyleXXX{mystyle}
			\end{document}
			''' }
		self.assertFlat('doc.tex', True)
		self.assertTrue(self.flattener.use_biblio)



	def test_bibliographystyleXXX_local_file_bib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyleXXX{mystyle}
			\end{document}
			''',
			'mystyle.bst' : r'''MYBIBLIO''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyleXXX{mystyle}
			\end{document}
			''',
			'mystyle.bst' : r'''MYBIBLIO''' }
		self.assertFlat('doc.tex', True)
		self.assertTrue(self.flattener.use_biblio)



	def test_bibliographystyleXXX_localsub1_noFile_bib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyleXXX{./biblio/mystyle}
			\end{document}
			''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyleXXX{./biblio/mystyle}
			\end{document}
			''' }
		self.assertFlat('doc.tex', True)
		self.assertTrue(self.flattener.use_biblio)



	def test_bibliographystyleXXX_localsub1_file_bib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyleXXX{./biblio/mystyle}
			\end{document}
			''',
			'./biblio/mystyle.bst' : r'''MYBIBLIO''' }
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographystyleXXX{mystyle}
			\end{document}
			''',
			'mystyle.bst' : r'''MYBIBLIO''' }
		self.assertFlat('doc.tex', True)
		self.assertTrue(self.flattener.use_biblio)



	def test_bibliographyslide_nofile_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\bibliographyslide
			\end{bibunit}
			\end{document}
			'''}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographyslide
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibliographyslide_file_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\bibliographyslide
			\end{bibunit}
			\end{document}
			''',
			'biblio.bib': 'BIBLIO ENTRIES',
			'doc.1.bbl': 'SPECIFIC BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\bibliographyslide
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibliographyslide_nofile_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\bibliographyslide
			\end{bibunit}
			\end{document}
			'''}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\bibliographyslide
			\end{bibunit}
			\end{document}
			'''}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_bibliographyslide_file_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\bibliographyslide
			\end{bibunit}
			\end{document}
			''',
			'biblio.bib': 'BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\bibliographyslide
			\end{bibunit}
			\end{document}
			''',
			'biblio.bib': 'BIBLIO ENTRIES'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)



	def test_bibliographysection_nofile_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibliographysection}
			Text
			\end{bibliographysection}
			\end{document}
			'''}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			Text
			\bibliographyslide
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibliographysection_file_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibliographysection}
			Text
			\end{bibliographysection}
			\end{document}
			''',
			'biblio.bib': 'BIBLIO ENTRIES',
			'doc.1.bbl': 'SPECIFIC BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			Text
			\bibliographyslide
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_bibliographysection_nofile_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibliographysection}
			Text
			\end{bibliographysection}
			\end{document}
			'''}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibliographysection}
			Text
			\end{bibliographysection}
			\end{document}
			'''}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_bibliographysection_file_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibliographysection}
			Text
			\end{bibliographysection}
			\end{document}
			''',
			'biblio.bib': 'BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibliographysection}
			Text
			\end{bibliographysection}
			\end{document}
			''',
			'biblio.bib': 'BIBLIO ENTRIES'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)




	def test_defaultbibliography_nodft_nofile_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			'''}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_defaultbibliography_dft_nofile_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\defaultbibliography{mybiblio}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			'''}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_defaultbibliography_nodft_file_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO ENTRIES',
			'doc.1.bbl': 'SPECIFIC BIBLIO ENTRIES',
			'doc.bbl': 'RAW BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: doc.1.bbl
			%=======================================================
			SPECIFIC BIBLIO ENTRIES
			%=======================================================
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_defaultbibliography_dft_file_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\defaultbibliography{mybiblio}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO ENTRIES',
			'doc.1.bbl': 'SPECIFIC BIBLIO ENTRIES',
			'doc.bbl': 'RAW BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: doc.1.bbl
			%=======================================================
			SPECIFIC BIBLIO ENTRIES
			%=======================================================
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_defaultbibliography_dft_subfile_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\defaultbibliography{subfolder/mybiblio}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			''',
			'subfolder/mybiblio.bib': 'BIBLIO ENTRIES',
			'doc.1.bbl': 'SPECIFIC BIBLIO ENTRIES',
			'doc.bbl': 'RAW BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: doc.1.bbl
			%=======================================================
			SPECIFIC BIBLIO ENTRIES
			%=======================================================
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_defaultbibliography_nodft_nofile_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			'''}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\putbib[doc]
			\end{bibunit}
			\end{document}
			'''}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_defaultbibliography_dft_nofile_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\defaultbibliography{mybiblio}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			'''}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\putbib[doc]
			\end{bibunit}
			\end{document}
			'''}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_defaultbibliography_nodft_file_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO ENTRIES',
			'doc.1.bbl': 'SPECIFIC BIBLIO ENTRIES',
			'doc.bbl': 'RAW BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\putbib[doc]
			\end{bibunit}
			\end{document}
			'''}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_defaultbibliography_dft_file_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\defaultbibliography{mybiblio}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO ENTRIES',
			'doc.1.bbl': 'SPECIFIC BIBLIO ENTRIES',
			'doc.bbl': 'RAW BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\putbib[mybiblio]
			\end{bibunit}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO ENTRIES'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_defaultbibliography_dft_subfile_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\defaultbibliography{subfolder/mybiblio}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			''',
			'subfolder/mybiblio.bib': 'BIBLIO ENTRIES',
			'doc.1.bbl': 'SPECIFIC BIBLIO ENTRIES',
			'doc.bbl': 'RAW BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\begin{document}
			\begin{bibunit}
			\putbib[mybiblio]
			\end{bibunit}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO ENTRIES'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)




	def test_defaultbibliographystyle_nofile_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\defaultbibliographystyle{mybiblio}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			'''}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_defaultbibliographystyle_file_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\defaultbibliographystyle{mybiblio}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO ENTRIES',
			'mybiblio.bst': 'MY STYLE',
			'doc.1.bbl': 'SPECIFIC BIBLIO ENTRIES',
			'doc.bbl': 'RAW BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: doc.1.bbl
			%=======================================================
			SPECIFIC BIBLIO ENTRIES
			%=======================================================
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_defaultbibliographystyle_subfile_nousebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\defaultbibliographystyle{subfolder/mybiblio}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO ENTRIES',
			'subfolder/mybiblio.bst': 'MY STYLE',
			'doc.1.bbl': 'SPECIFIC BIBLIO ENTRIES',
			'doc.bbl': 'RAW BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\begin{document}
			%=======================================================
			%== BEGIN FILE: doc.1.bbl
			%=======================================================
			SPECIFIC BIBLIO ENTRIES
			%=======================================================
			\end{document}
			'''}
		self.assertFlat('doc.tex')
		self.assertFalse(self.flattener.use_biblio)

	def test_defaultbibliographystyle_nofile_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\defaultbibliographystyle{mybiblio}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			'''}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\defaultbibliographystyle{mybiblio}
			\begin{document}
			\begin{bibunit}
			\putbib[doc]
			\end{bibunit}
			\end{document}
			'''}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_defaultbibliographystyle_file_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\defaultbibliographystyle{mybiblio}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO ENTRIES',
			'mybiblio.bst': 'MY STYLE',
			'doc.1.bbl': 'SPECIFIC BIBLIO ENTRIES',
			'doc.bbl': 'RAW BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\defaultbibliographystyle{mybiblio}
			\begin{document}
			\begin{bibunit}
			\putbib[doc]
			\end{bibunit}
			\end{document}
			''',
			'mybiblio.bst': 'MY STYLE'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)

	def test_defaultbibliographystyle_subfile_usebib(self):
		self.inputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\defaultbibliographystyle{subfolder/mybiblio}
			\begin{document}
			\begin{bibunit}
			\putbib
			\end{bibunit}
			\end{document}
			''',
			'mybiblio.bib': 'BIBLIO ENTRIES',
			'subfolder/mybiblio.bst': 'MY STYLE',
			'doc.1.bbl': 'SPECIFIC BIBLIO ENTRIES',
			'doc.bbl': 'RAW BIBLIO ENTRIES'}
		self.outputs = { 'doc.tex' : r'''
			\documentclass{article}
			\usepackage{bibunits}
			\defaultbibliographystyle{mybiblio}
			\begin{document}
			\begin{bibunit}
			\putbib[doc]
			\end{bibunit}
			\end{document}
			''',
			'mybiblio.bst': 'MY STYLE'}
		self.assertFlat('doc.tex', use_biblio=True)
		self.assertTrue(self.flattener.use_biblio)


if __name__ == '__main__':
	unittest.main()

