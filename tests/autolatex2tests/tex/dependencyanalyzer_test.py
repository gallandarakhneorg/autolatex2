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
import re
import logging
import pathlib
from typing import override

from autolatex2.tex import dependencyanalyzer
from autolatex2.tex.utils import FileType
from autolatex2tests.abstract_base_test import AbstractBaseTest

class TestDependencyAnalyzer(AbstractBaseTest):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__lastDirname = None
		self.__lastBasename = None
		self.__lastFilename = None

	@override
	def setUp(self):
		logging.getLogger().setLevel(logging.CRITICAL)

	def ___run(self, content : str, *filenames : str):
		f = tempfile.NamedTemporaryFile(delete=False)
		name = f.name
		self.__lastFilename = name
		self.__lastDirname = os.path.dirname(name)
		self.__lastBasename = os.path.basename(name)
		f.file.write(bytes(content, 'UTF-8'))
		f.seek(0)
		f.close()
		for filename in filenames:
			fn = re.sub(r'\?\?\?', self.__lastFilename, filename)
			pathlib.Path(os.path.join(self.__lastDirname, fn)).touch()
		analyzer = dependencyanalyzer.DependencyAnalyzer(name, self.__lastDirname, self.__lastFilename, include_extra_macros=True)
		analyzer.run()
		os.remove(name)
		for filename in filenames:
			fn = re.sub(r'\?\?\?', self.__lastFilename, filename)
			os.remove(os.path.join(self.__lastDirname, fn))
		return analyzer

	def test_emptyString(self):
		analyzer = self.___run('')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_input_nofile(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\input{myfile}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_input_file(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\input{myfile}\\end{document}', 'myfile.tex')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		self.assertIn(FileType.tex, types)
		tex_deps = analyzer.get_dependencies_for_type(FileType.tex)
		self.assertEqual(1, len(tex_deps))
		self.assertIn(os.path.join(self.__lastDirname, "myfile.tex"), tex_deps)
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_include_nofile(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\include{myfile}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_include_file(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\include{myfile}\\end{document}', 'myfile.tex')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		self.assertIn(FileType.tex, types)
		tex_deps = analyzer.get_dependencies_for_type(FileType.tex)
		self.assertEqual(1, len(tex_deps))
		self.assertIn(os.path.join(self.__lastDirname, "myfile.tex"), tex_deps)
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_makeindex(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\makeindex\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertTrue(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_printindex(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\printindex\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertTrue(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_multibib(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{multibib}\\begin{document}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertTrue(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_biblatex(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{biblatex}\\begin{document}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertTrue(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_biber(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage[backend=biber]{biblatex}\\begin{document}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertTrue(analyzer.is_biblatex)
		self.assertTrue(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_usepackage_nofile(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{mypackage}\\begin{document}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_usepackage_file(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{mypackage}\\begin{document}\\end{document}', 'mypackage.sty')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		self.assertIn(FileType.sty, types)
		tex_deps = analyzer.get_dependencies_for_type(FileType.sty)
		self.assertEqual(1, len(tex_deps))
		self.assertIn(os.path.join(self.__lastDirname, "mypackage.sty"), tex_deps)
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_requirepackage_nofile(self):
		analyzer = self.___run('\\documentclass{article}\\RequirePackage{mypackage}\\begin{document}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_requirepackage_file(self):
		analyzer = self.___run('\\documentclass{article}\\RequirePackage{mypackage}\\begin{document}\\end{document}', 'mypackage.sty')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		self.assertIn(FileType.sty, types)
		tex_deps = analyzer.get_dependencies_for_type(FileType.sty)
		self.assertEqual(1, len(tex_deps))
		self.assertIn(os.path.join(self.__lastDirname, "mypackage.sty"), tex_deps)
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_documentclass_nofile(self):
		analyzer = self.___run('\\documentclass{myarticle}\\begin{document}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_documentclass_file(self):
		analyzer = self.___run('\\documentclass{myarticle}\\begin{document}\\end{document}', 'myarticle.cls')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		self.assertIn(FileType.cls, types)
		tex_deps = analyzer.get_dependencies_for_type(FileType.cls)
		self.assertEqual(1, len(tex_deps))
		self.assertIn(os.path.join(self.__lastDirname, "myarticle.cls"), tex_deps)
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_bibliography_nofile(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\bibliography{mybib}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_bibliography_file(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\bibliography{mybib}\\end{document}', 'mybib.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "mybib.bib"), dbs)

	def test_bibliography_files(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\bibliography{mybib,mybib1}\\end{document}',
							   'mybib.bib', 'mybib1.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(2, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "mybib.bib"), dbs)
		self.assertIn(os.path.join(self.__lastDirname, "mybib1.bib"), dbs)

	def test_bibliographyXXX_nomultibib_nofile(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\bibliographyXXX{mybib}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_bibliographyXXX_nomultibib_file(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\bibliographyXXX{mybib}\\end{document}', 'mybib.cls')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_bibliographyXXX_nomultibib_files(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\bibliographyXXX{mybib,mybib1}\\end{document}',
							   'mybib.cls','mybib1.cls')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_bibliographyXXX_multibib_nofile(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{multibib}\\begin{document}\\bibliographyXXX{mybib}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertTrue(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_bibliographyXXX_multibib_file(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{multibib}\\begin{document}\\bibliographyXXX{mybib}\\end{document}', 'mybib.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertTrue(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn('XXX', types)
		dbs = analyzer.get_dependencies_for_type(FileType.bib, 'XXX')
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "mybib.bib"), dbs)

	def test_bibliographyXXX_multibib_files(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{multibib}\\begin{document}\\bibliographyXXX{mybib,mybib1}\\end{document}',
							   'mybib.bib', 'mybib1.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertTrue(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn('XXX', types)
		dbs = analyzer.get_dependencies_for_type(FileType.bib, 'XXX')
		self.assertEqual(2, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "mybib.bib"), dbs)
		self.assertIn(os.path.join(self.__lastDirname, "mybib1.bib"), dbs)

	def test_bibliographystyle_nofile(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\bibliographystyle{mystyle}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))

	def test_bibliographystyle_file(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\bibliographystyle{mystyle}\\end{document}', 'mystyle.bst')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bst, self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "mystyle.bst"), dbs)

	def test_bibliographysection_nofile(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\begin{document}\\begin{bibliographysection}blablabla\\end{bibliographysection}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(0, len(dbs))

	def test_bibliographysection_otherfile(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\begin{document}\\begin{bibliographysection}blablabla\\end{bibliographysection}\\end{document}', 'mybib.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(0, len(dbs))

	def test_bibliographysection_file(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\begin{document}\\begin{bibliographysection}blablabla\\end{bibliographysection}\\end{document}', 'biblio.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "biblio.bib"), dbs)

	def test_bibliographysection_files(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\begin{document}\\begin{bibliographysection}blablabla\\end{bibliographysection}\\end{document}', 'biblio.bib', 'mybib.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "biblio.bib"), dbs)

	def test_bibliographyslide_nofile(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\begin{document}\\bibliographyslide\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(0, len(dbs))

	def test_bibliographyslide_otherfile(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\begin{document}\\bibliographyslide\\end{document}', 'mybiblio.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(0, len(dbs))

	def test_bibliographyslide_file(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\begin{document}\\bibliographyslide\\end{document}', 'biblio.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "biblio.bib"), dbs)

	def test_bibliographyslide_files(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\begin{document}\\bibliographyslide\\end{document}', 'biblio.bib', 'mybiblio.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "biblio.bib"), dbs)

	def test_putbib_param_nofile(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\begin{document}\\putbib[mybiblio1]\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(0, len(dbs))

	def test_putbib_param_otherfile(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\begin{document}\\putbib[mybiblio1]\\end{document}', 'mybiblio0.bib', 'mybiblio2.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(0, len(dbs))

	def test_putbib_param_file(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\begin{document}\\putbib[mybiblio1]\\end{document}', 'mybiblio0.bib', 'mybiblio1.bib', 'mybiblio2.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "mybiblio1.bib"), dbs)

	def test_putbib_param_files(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\begin{document}\\putbib[mybiblio1,mybiblio2]\\end{document}', 'mybiblio0.bib', 'mybiblio1.bib', 'mybiblio2.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(2, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "mybiblio1.bib"), dbs)
		self.assertIn(os.path.join(self.__lastDirname, "mybiblio2.bib"), dbs)

	def test_putbib_noparam_nofile(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\begin{document}\\putbib\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(0, len(dbs))

	def test_putbib_noparam_otherfile(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\begin{document}\\putbib\\end{document}', 'mybiblio0.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(0, len(dbs))

	def test_putbib_noparam_file(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\begin{document}\\putbib\\end{document}',
							   '???.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, self.__lastBasename + ".bib"), dbs)


	def test_putbib_noparam_nofile_dflt(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\defaultbibliography{mybib.bib}\\begin{document}\\putbib\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(0, len(dbs))

	def test_putbib_noparam_otherfile_dflt(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\defaultbibliography{mybib.bib}\\begin{document}\\putbib\\end{document}', 'mybiblio0.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(0, len(dbs))

	def test_putbib_noparam_file_dflt(self):
		analyzer = self.___run('\\documentclass{article}\\usepackage{bibunits}\\defaultbibliography{mybib}\\begin{document}\\putbib\\end{document}',
							   'mybib.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertTrue(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "mybib.bib"), dbs)


	def test_defaultbibliography__noexplicit_nofile(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\defaultbibliography{mybib}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(0, len(dbs))


	def test_defaultbibliography__noexplicit_otherfile(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\defaultbibliography{mybib}\\end{document}', 'mybib1.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(0, len(dbs))


	def test_defaultbibliography__noexplicit_file(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\defaultbibliography{mybib}\\end{document}', 'mybib.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "mybib.bib"), dbs)

	def test_defaultbibliography__noexplicit_files(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\defaultbibliography{mybib,mybib1,mybib2}\\end{document}', 'mybib.bib', 'mybib1.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(2, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "mybib.bib"), dbs)
		self.assertIn(os.path.join(self.__lastDirname, "mybib1.bib"), dbs)

	def test_defaultbibliography__explicit_nofile(self):
		analyzer = self.___run('\\documentclass{article}\\bibliography{mybib2}\\begin{document}\\defaultbibliography{mybib}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(0, len(dbs))


	def test_defaultbibliography__explicit_otherfile(self):
		analyzer = self.___run('\\documentclass{article}\\bibliography{mybib2}\\begin{document}\\defaultbibliography{mybib}\\end{document}', 'mybib1.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(0, len(dbs))


	def test_defaultbibliography__explicit_file(self):
		analyzer = self.___run('\\documentclass{article}\\bibliography{mybib2}\\begin{document}\\defaultbibliography{mybib}\\end{document}', 'mybib2.bib', 'mybib1.bib', 'mybib.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "mybib2.bib"), dbs)


	def test_defaultbibliography__explicit_files(self):
		analyzer = self.___run('\\documentclass{article}\\bibliography{mybib2}\\begin{document}\\defaultbibliography{mybib,mybib1}\\end{document}', 'mybib2.bib', 'mybib1.bib', 'mybib.bib')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bib, self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "mybib2.bib"), dbs)


	def test_defaultbibliographystyle__noexplicit_nofile(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\defaultbibliographystyle{mybib}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bst, self.__lastBasename)
		self.assertEqual(0, len(dbs))


	def test_defaultbibliographystyle__noexplicit_otherfile(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\defaultbibliographystyle{mybib}\\end{document}', 'mybib1.bst')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bst, self.__lastBasename)
		self.assertEqual(0, len(dbs))


	def test_defaultbibliographystyle__noexplicit_file(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\defaultbibliographystyle{mybib}\\end{document}', 'mybib.bst')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bst, self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "mybib.bst"), dbs)

	def test_defaultbibliographystyle__noexplicit_files(self):
		analyzer = self.___run('\\documentclass{article}\\begin{document}\\defaultbibliographystyle{mybib}\\end{document}', 'mybib.bst', 'mybib1.bst')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bst, self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "mybib.bst"), dbs)

	def test_defaultbibliographystyle__explicit_nofile(self):
		analyzer = self.___run('\\documentclass{article}\\bibliographystyle{mybib2}\\begin{document}\\defaultbibliographystyle{mybib}\\end{document}')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bst, self.__lastBasename)
		self.assertEqual(0, len(dbs))


	def test_defaultbibliographystyle__explicit_otherfile(self):
		analyzer = self.___run('\\documentclass{article}\\bibliographystyle{mybib2}\\begin{document}\\defaultbibliographystyle{mybib}\\end{document}', 'mybib1.bst')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(0, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(0, len(types))
		dbs = analyzer.get_dependencies_for_type(FileType.bst, self.__lastBasename)
		self.assertEqual(0, len(dbs))


	def test_defaultbibliographystyle__explicit_file(self):
		analyzer = self.___run('\\documentclass{article}\\bibliographystyle{mybib2}\\begin{document}\\defaultbibliographystyle{mybib}\\end{document}', 'mybib2.bst', 'mybib.bst')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bst, self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "mybib2.bst"), dbs)


	def test_defaultbibliographystyle__explicit_files(self):
		analyzer = self.___run('\\documentclass{article}\\bibliographystyle{mybib2}\\begin{document}\\defaultbibliographystyle{mybib}\\end{document}', 'mybib2.bst', 'mybib.bst')

		self.assertEqual(self.__lastDirname, analyzer.root_directory)
		self.assertEqual(self.__lastBasename, analyzer.basename)
		self.assertEqual(self.__lastFilename, analyzer.filename)
		self.assertFalse(analyzer.is_multibib)
		self.assertFalse(analyzer.is_bibunits)
		self.assertFalse(analyzer.is_biblatex)
		self.assertFalse(analyzer.is_biber)
		self.assertFalse(analyzer.is_makeindex)

		types = analyzer.get_dependency_types()
		self.assertEqual(1, len(types))
		types = analyzer.get_bibliography_scopes()
		self.assertEqual(1, len(types))
		self.assertIn(self.__lastBasename, types)
		dbs = analyzer.get_dependencies_for_type(FileType.bst, self.__lastBasename)
		self.assertEqual(1, len(dbs))
		self.assertIn(os.path.join(self.__lastDirname, "mybib2.bst"), dbs)


if __name__ == '__main__':
	unittest.main()

