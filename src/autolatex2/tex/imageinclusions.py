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
Tools for extracting the list of the included figures in a TeX document.
"""

import os
import re
import textwrap
import logging
from typing import override, Any

from autolatex2.tex.texobservers import Observer
from autolatex2.tex.texparsers import Parser
from autolatex2.tex.texparsers import TeXParser
import autolatex2.utils.utilfunctions as genutils
from autolatex2.utils.i18n import T

class ImageInclusions(Observer):
	"""
	Observer on TeX parsing for extracting included images in a TeX document.
	"""

	__MACROS : dict[str,str] = {
		'input'							: '!{}',
		'include'						: '!{}',
		'includeanimatedfigure'			: '![]!{}',
		'includeanimatedfigurewtex'		: '![]!{}',
		'includefigurewtex'				: '![]!{}',
		'includegraphics'				: '![]!{}',
		'includegraphicswtex'			: '![]!{}',
		'graphicspath'					: '![]!{}',
		'mfigure'						: '![]!{}!{}!{}!{}',
		'mfigure*'						: '![]!{}!{}!{}!{}',
		'msubfigure'					: '![]!{}!{}!{}',
		'msubfigure*'					: '![]!{}!{}!{}',
		'mfiguretex'					: '![]!{}!{}!{}!{}',
		'mfiguretex*'					: '![]!{}!{}!{}!{}',
		'pgfdeclareimage'				: '![]!{}!{}',
	}

	def __init__(self, filename : str):
		"""
		Constructor.
		:param filename: The name of the file to parse.
		:type filename: str
		"""
		self.__filename = filename
		self.__basename = os.path.basename(os.path.splitext(filename)[0])
		self.__directory_name = os.path.dirname(filename)
		self.__dynamic_preamble = list()
		self.__init()

	def __init(self) :
		# Inclusion paths for pictures.
		self.__include_paths = []
		if self.__directory_name:
			self.__include_paths.append(self.__directory_name)
		# Content of the TeX file to generate
		self.__files_to_copy = set()
		# Mapping between the files of the source TeX and the target TeX.
		self.__source2target = dict()
		self.__target2source = dict()

	@property
	def include_paths(self) -> list[str]:
		"""
		Replies the paths in which included files are search for.
		:return: The list of the inclusion path.
		:rtype: list
		"""
		return self.__include_paths

	def get_included_figures(self) -> set[str]:
		"""
		Replies the list of included figures.
		:rtype: list
		"""
		return self.__files_to_copy

	@property
	def basename(self) -> str:
		"""
		Replies the basename of the parsed file.
		:return: The basename  of the parsed file.
		:rtype: str
		"""
		return self.__basename

	@basename.setter
	def basename(self, n : str):
		"""
		Set the basename of the parsed file.
		:param n: The basename of the parsed file.
		:type n: str
		"""
		self.__basename = n

	@property
	def dirname(self) -> str:
		"""
		Replies the dirname of the parsed file.
		:return: The dirname  of the parsed file.
		:rtype: str
		"""
		return self.__directory_name

	@dirname.setter
	def dirname(self, n : str):
		"""
		Set the dirname of the parsed file.
		:param n: The dirname of the parsed file.
		:type n: str
		"""
		self.__directory_name = n

	@property
	def filename(self) -> str:
		"""
		Replies the filename of the parsed file.
		:return: The filename of the parsed file.
		:rtype: str
		"""
		return self.__filename

	@filename.setter
	def filename(self, n : str):
		"""
		Set the filename of the parsed file.
		:param n: The filename of the parsed file.
		:type n: str
		"""
		self.__filename = n

	@override
	def open_block(self, parser : Parser, text : str) -> str:
		"""
		Invoked when a block is opened.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: The text used for opening the block.
		:type text: str
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		"""
		return '{'

	@override
	def close_block(self, parser : Parser, text : str) -> str:
		"""
		Invoked when a block is closed.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: The text used for opening the block.
		:type text: str
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		"""
		return '}'

	@override
	def open_math(self, parser : Parser, inline : bool) -> str:
		"""
		Invoked when a math environment is opened.
		:param parser: reference to the parser.
		:type parser: Parser
		:param inline: Indicates if the math environment is inline or not.
		:type inline: bool
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		"""
		return '$' if inline else '\\['

	@override
	def close_math(self, parser : Parser, inline : bool) -> str:
		"""
		Invoked when a math environment is closed.
		:param parser: reference to the parser.
		:type parser: Parser
		:param inline: Indicates if the math environment is inline or not.
		:type inline: bool
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str
		"""
		return '$' if inline else '\\]'

	@override
	def text(self, parser : Parser, text : str):
		"""
		Invoked when characters were found and must be output.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: the text to filter.
		:type text: str
		"""
		pass

	# noinspection DuplicatedCode
	@override
	def expand(self, parser : Parser, raw_text : str, name : str, *parameter : dict[str,Any]) -> str:
		"""
		Expand the given macro on the given parameters.
		:param parser: reference to the parser.
		:type parser: Parser
		:param raw_text: The raw text that is the source of the expansion.
		:type raw_text: str
		:param name: Name of the macro.
		:type name: str
		:param parameter: Descriptions of the values passed to the TeX macro.
		:type parameter: dict[str,Any]
		:return: the result of expansion of the macro, or None to not replace the macro by something (the macro is used as-is)
		:rtype: str
		"""
		if	name == "\\includegraphics" or name == "\\includeanimatedfigure" or name == "\\includeanimatedfigurewtex" or name == "\\includefigurewtex" or name == "\\includegraphicswtex":
			self.__find_picture(parameter[1]['text'])
		elif name == "\\graphicspath":
			t = parameter[1]['text']
			if t:
				r = re.match(r'^\s*(?:\{([^}]+)}|([^,]+))\s*[,;]?\s*(.*)$', t)
				while r:
					path = r.group(1) or r.group(2)
					if not os.path.isabs(path):
						path = os.path.normpath(os.path.join(self.__directory_name, path))
					t = r.group(3)
					self.__include_paths.insert(0, path)
					r = re.match(r'^\s*(?:\{([^}]+)}|([^,]+))\s*[,;]?\s*(.*)$', t) if t else None
		elif	name == "\\mfigure" or name == "\\mfigure*" or name == "\\mfiguretex" or name == "\\mfiguretex*":
			self.__find_picture(parameter[2]['text'])
		elif name == "\\msubfigure" or name == "\\msubfigure*":
			self.__find_picture(parameter[2]['text'])
		elif name == "\\pgfdeclareimage":
			self.__find_picture(parameter[2]['text'])
		elif name == "\\include" or name == "\\input":
			filename = self.__make_filename(parameter[0]['text'], '.tex')
			with open(filename) as f:
				subcontent = f.read()
			subcontent += textwrap.dedent("""
							%%=======================================================
							%%== END FILE: %s
							%%=======================================================
							""") % (os.path.basename(filename))

			parser.put_back(subcontent)
			return textwrap.dedent("""
					%%=======================================================
					%%== BEGIN FILE: %s
					%%=======================================================
					""") % (os.path.basename(filename))
		# Reply the raw text back to the generated TeX document.
		return raw_text

	def __make_filename(self, basename : str, ext : str = None) -> str:
		"""
		Create a valid filename for the flattening process.
		:param basename: The basename.
		:param basename: str
		:param ext: The filename extension (default: None).
		:param ext: str
		"""
		if ext and not basename.endswith(ext):
			name = basename + ext
		else:
			name = basename
		if not os.path.isabs(name):
			return os.path.join(self.dirname, name)
		return name

	# noinspection DuplicatedCode
	def __create_mapping(self, filename : str, ext : str) -> str:
		"""
		Compute an unique filename, and map it to the source file.
		:param filename: The filename to translate.
		:type filename: str
		:param ext: The filename extension to remove.
		:type ext: str
		:return: The unique basename.
		:rtype: str
		"""
		name = os.path.basename(filename)
		if ext and name.endswith(ext):
			name = name[0:(-len(ext))]
		bn = name
		i = 0
		while (name + ext) in self.__target2source:
			name = "%s_%d" % (bn, i)
			i += 1
		self.__target2source[name + ext] = filename
		self.__source2target[filename] = name + ext
		return name

	# noinspection DuplicatedCode
	def __find_picture(self, tex_name : str) -> tuple[str,str]:
		"""
		Find a picture.
		:param tex_name: The name of the picture in the TeX document.
		:type tex_name: str
		:return: the tuple (target filename, the prefix to add before the macro)
		:rtype: tuple[str,str]
		"""
		# Search in the registered/found bitmaps
		if self.__source2target:
			for src in self.__source2target:
				if src == tex_name:
					return os.path.basename(self.__source2target[src]), ''

		prefix = ''
		filename = self.__make_filename(tex_name)
		if not os.path.isfile(filename):
			texexts = ('.pdftex_t', '.pstex_t', '.pdf_tex', '.ps_tex', '.tex')
			figexts = (	'.pdf', '.eps', '.ps', '.png', '.jpeg', '.jpg', '.gif', '.bmp')
			exts = figexts + texexts
			ofilename = filename
			obasename = genutils.basename(tex_name, *exts)
			filenames = {}

			# Search in the registered paths
			template = obasename
			for path in self.include_paths:
				for ext in figexts:
					fullname = os.path.join(path, template + ext)
					fullname = self.__make_filename(fullname)
					if os.path.isfile(fullname):
						filenames[fullname] = False
				for ext in texexts:
					fullname = os.path.join(path, template + ext)
					fullname = self.__make_filename(fullname, '')
					if os.path.isfile(fullname):
						filenames[fullname] = True

			# Search in the folder, i.e. the document directory.
			if not filenames:
				template = os.path.join(os.path.dirname(ofilename), genutils.basename(ofilename, *exts))
				for ext in figexts:
					fn = template + ext
					if os.path.isfile(fn):
						filenames[fn] = False
				for ext in texexts:
					fn = template + ext
					if os.path.isfile(fn):
						filenames[fn] = True

			if not filenames:
				logging.error(T('Picture not found: %s'), tex_name)
			else:
				selected_name1 = None
				selected_name2 = None
				for filename in filenames:
					ext = os.path.splitext(filename)[1] or ''
					tex_name = self.__create_mapping(filename, ext) + ext
					if filenames[filename]:
						if not selected_name1:
							selected_name1 = (tex_name, filename)
					else:
						self.__files_to_copy.add(os.path.normpath(filename))
						selected_name2 = tex_name
				if selected_name1:
					tex_name, filename = selected_name1
					logging.debug(T('Embedding %s'), filename)
					with open(filename) as f:
						file_content = f.read()
					# Replacing the filename in the newly embedded TeX file
					if self.__source2target:
						for source in self.__source2target:
							file_content = file_content.replace('{' + source + '}',
											'{' + self.__source2target[source] + '}')
					bsn = os.path.basename(tex_name)
					prefix +=	textwrap.dedent("""
								%%=======================================================
								%%== BEGIN FILE: %s
								%%=======================================================
								\\begin{filecontents*}{%s}
								%s
								\\end{filecontents*}
								%%=======================================================
								""") % (bsn, bsn, file_content)
					self.__dynamic_preamble.append('\\usepackage{filecontents}')
				elif selected_name2:
					tex_name = selected_name2
		else:
			ext = os.path.splitext(tex_name)[1] or ''
			tex_name = self.__create_mapping(filename, ext) + ext
			self.__files_to_copy.add(os.path.normpath(filename))

		return tex_name, prefix

	# noinspection DuplicatedCode
	def _analyze_document(self):
		"""
		Analyze the tex document for extracting information.
		:return: The content of the file.
		"""
		with open(self.filename) as f:
			content = f.read()

		parser = TeXParser()
		parser.observer = self
		parser.filename = self.filename

		for k, v in self.__MACROS.items():
			parser.add_text_mode_macro(k, v)
			parser.add_math_mode_macro(k, v)

		parser.parse(content)

	def run(self) -> bool:
		"""
		Make the input file standalone.
		:return: True if the execution is a success, otherwise False.
		"""
		self.__init()
		self._analyze_document()
		return True

	@override
	def comment(self, parser: Parser, raw: str, comment: str) -> str | None:
		return None

	@override
	def find_macro(self, parser: Parser, name: str, special: bool, math: bool) -> str | None:
		return None
