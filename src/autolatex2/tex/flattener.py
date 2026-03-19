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
Tools for creating a flattened version of a TeX document.
A flattened document contains a single TeX file, and all the
other related files are put inside the same directory of
the TeX file.
"""

import os
import shutil
import re
import textwrap
import logging
from typing import override, Any

from autolatex2.tex.texobservers import Observer
from autolatex2.tex.texparsers import Parser
from autolatex2.tex.texparsers import TeXParser
import autolatex2.utils.utilfunctions as genutils

import gettext
_T = gettext.gettext

class Flattener(Observer):
	"""
	Observer on TeX parsing for creating a flattened version of a TeX document.
	"""

	__MACROS : dict[str,str] = {
		'input'							: '!{}',
		'include'						: '!{}',
		'usepackage'					: '![]!{}',
		'RequirePackage'				: '![]!{}',
		'documentclass'					: '![]!{}',
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
		'addbibresource'				: '![]!{}',
		'begin'							: '![]!{}',
		'end'							: '![]!{}',
	}

	def __init__(self, filename : str, output_directory : str):
		"""
		Constructor.
		:param filename: The name of the file to parse.
		:type filename: str
		:param output_directory: The name of the directory in which the document must be generated.
		:type output_directory: ste
		"""
		# Following attributes are init in __init()
		self.__file_content_counter = None
		self.__embedded_files = None
		# Other attributes
		self.__filename = filename
		self.__basename = os.path.basename(os.path.splitext(filename)[0])
		self.__dirname = os.path.dirname(filename)
		self.__output = output_directory
		self.__use_biblio = False
		self.__init()
		self.__included_sty = dict()


	def __init(self) :
		# Inclusion paths for pictures.
		self.__include_paths = []
		if self.__dirname:
			self.__include_paths.append(self.__dirname)
		# Premable entries added by this tool
		self.__dynamic_preamble = []
		# Content of the TeX file to generate
		self.__tex_file_content = ''
		# Mapping betwwen the files of the source TeX and the target TeX.
		self.__source2target = dict()
		self.__target2source = dict()
		# Files to copy
		self.__files_to_copy = set()
		# Embedded files
		self.__embedded_files_added = set()
		self.__embedded_files = dict()
		self.__file_content_counter = 0

	@property
	def include_paths(self) -> list[str]:
		"""
		Replies the paths in which included files are search for.
		:return: The list of the inclusion path.
		:rtype: list[str]
		"""
		return self.__include_paths

	@property
	def use_biblio(self) -> bool:
		"""
		Replies if the biblio database.
		:return: True if the biblio database may be use. False for inline biliography entries.
		:rtype: bool
		"""
		return self.__use_biblio

	@use_biblio.setter
	def use_biblio(self, b : bool):
		"""
		Set if the biblio database.
		:param b: True if the biblio database may be use. False for inline biliography entries.
		:type b: bool
		"""
		self.__use_biblio = b

	@property
	def output_directory(self) -> str:
		"""
		Replies the output directory.
		:return: The name  of the output directory.
		:rtype: str
		"""
		return self.__output

	@output_directory.setter
	def output_directory(self, n : str):
		"""
		Set the output directory.
		:param n: The name of output directory.
		:type n: str
		"""
		self.__output = n

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
		return self.__dirname

	@dirname.setter
	def dirname(self, n : str):
		"""
		Set the dirname of the parsed file.
		:param n: The dirname of the parsed file.
		:type n: str
		"""
		self.__dirname = n

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
	def find_macro(self, parser : Parser, name : str, special : bool, math : bool) -> str | None:
		"""
		Invoked each time a macro definition is not found in the parser data.
		:param parser: reference to the parser.
		:type parser: Parser
		:param name: Name of the macro.
		:type name: str
		:param special: Indicates if the macro is a special macro or not.
		:type special: bool
		:param math: Indicates if the math mode is active.
		:type math: bool
		:return: the definition of the macro, ie. the macro prototype. See the class documentation for an explanation about the format of the macro prototype.
		:rtype: str
		"""
		if not special:
			if name.startswith('bibliographystyle'):
				return '!{}'
			elif name.startswith('bibliography'):
				return '!{}'
		return None

	@override
	def open_block(self, parser : Parser, text : str) -> str | None:
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
	def close_block(self, parser : Parser, text : str) -> str | None:
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
	def open_math(self, parser : Parser, inline : bool) -> str | None:
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
	def close_math(self, parser : Parser, inline : bool) -> str | None:
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
		if text:
			self.__tex_file_content += text

	@override
	def expand(self, parser : Parser, raw_text : str, name : str, *parameter : dict[str,Any]) -> str | None:
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
		:return: the result of the expand of the macro, or None to not replace the macro by something (the macro is used as-is)
		:rtype: str
		"""
		if name == "\\begin":
			tex_name = parameter[1]['text']
			if tex_name == 'filecontents*':
				self.__file_content_counter = self.__file_content_counter + 1
			ret = name
			if parameter[0]['text']:
				ret += "[%s]" % parameter[0]['text']
			ret += "{%s}" % tex_name
			return ret
		elif name == "\\end":
			tex_name = parameter[1]['text']
			if tex_name == 'filecontents*':
				self.__file_content_counter = self.__file_content_counter - 1
				if self.__file_content_counter <= 0:
					for key,  value in self.__embedded_files.items():
						parser.put_back(value)
					self.__embedded_files = dict()
			ret = name
			if parameter[0]['text']:
				ret += "[%s]" % parameter[0]['text']
			ret += "{%s}" % tex_name
			return ret
		elif name == "\\usepackage" or name == "\\RequirePackage":
			tex_name = parameter[1]['text']
			filename = self.__make_filename(tex_name, '.sty')
			added_file = ''
			if tex_name == 'biblatex':
				if not self.use_biblio:
					filename = self.__make_filename(self.basename, '.bbl', '.tex')
					if os.path.isfile(filename) and filename not in self.__embedded_files_added:
						logging.debug(_T('Embedding %s'), filename)
						if not self.__embedded_files_added:
							self.__dynamic_preamble.append("\\usepackage{filecontents}")
						self.__embedded_files_added.add(filename)
						with open(filename) as f:
							content = f.read()
						basename = os.path.basename(filename)
						added_file = textwrap.dedent("""
								%%=======================================================
								%%== BEGIN FILE: %s
								%%=======================================================
								\\begin{filecontents*}{%s}
								%s
								\\end{filecontents*}
								%%=======================================================
								""") % (basename, basename, content)
					else:
						logging.error(_T('File not found: %s'), filename)
			elif self.__is_document_file(filename) and filename not in self.__embedded_files_added:
				logging.debug(_T('Embedding %s'), filename)
				if not self.__embedded_files_added:
					self.__dynamic_preamble.append("\\usepackage{filecontents}")
				self.__embedded_files_added.add(filename)
				with open(filename) as f:
					content = f.read()
				basename = os.path.basename(filename)
				added_file = textwrap.dedent("""
						%%=======================================================
						%%== BEGIN FILE: %s
						%%=======================================================
						\\begin{filecontents*}{%s}
						%s
						\\end{filecontents*}
						%%=======================================================
						""") % (basename, basename, content)
			ret = name
			if parameter[0]['text']:
				ret += "[%s]" % parameter[0]['text']
			ret += "{%s}" % tex_name
			if added_file:
				if 	self.__file_content_counter <= 0:
					parser.put_back(added_file + ret)
					return ''
				else:
					self.__embedded_files[filename] = added_file
					return ret
			else:
				return ret
		if name == "\\documentclass":
			tex_name = parameter[1]['text']
			filename = self.__make_filename(tex_name, '.cls')
			if self.__is_document_file(filename):
				tex_name = self.__create_mapping(filename, '.cls')
				self.__files_to_copy.add(filename)
			ret = name
			if parameter[0]['text']:
				ret += "[%s]" % parameter[0]['text']
			ret += "{%s}\n\n%%========= AUTOLATEX PREAMBLE\n\n" % tex_name
			return ret
		elif	name == "\\includegraphics" or \
				name == "\\includeanimatedfigure" or \
				name == "\\includeanimatedfigurewtex" or \
				name == "\\includefigurewtex" or \
				name == "\\includegraphicswtex":
			tex_name, prefix = self.__find_picture(parameter[1]['text'])
			ret = prefix + name
			if parameter[0]['text']:
				ret += "[%s]" % parameter[0]['text']
			ret += "{%s}" % tex_name
			return ret
		elif name == "\\graphicspath":
			t = parameter[1]['text']
			if t:
				r = re.match(r'^\s*(?:\{([^}]+)}|([^,]+))\s*[,;]?\s*(.*)$', t)
				while r:					
					path = r.group(1) or r.group(2)
					if not os.path.isabs(path):
						path = os.path.join(self.__dirname, path)
					t = r.group(3)
					self.__include_paths.insert(0, path)
					r = re.match(r'^\s*(?:\{([^}]+)}|([^,]+))\s*[,;]?\s*(.*)$', t) if t else None
			return "\\graphicspath{{./}}"
		elif	name == "\\mfigure" or \
				name == "\\mfigure*" or \
				name == "\\mfiguretex" or \
				name == "\\mfiguretex*":
			tex_name, prefix = self.__find_picture(parameter[2]['text'])
			ret = prefix + name
			if parameter[0]['text']:
				ret += "[%s]" % parameter[0]['text']
			ret += "{%s}{%s}{%s}{%s}" % (parameter[1]['text'], tex_name, parameter[3]['text'], parameter[4]['text'])
			return ret
		elif name == "\\msubfigure" or name == "\\msubfigure*":
			tex_name, prefix = self.__find_picture(parameter[2]['text'])
			ret = prefix + name
			if parameter[0]['text']:
				ret += "[%s]" % parameter[0]['text']
			ret += "{%s}{%s}{%s}" % (parameter[1]['text'], tex_name, parameter[3]['text'])
			return ret
		elif name == "\\pgfdeclareimage":
			tex_name, prefix = self.__find_picture(parameter[2]['text'])
			ret = prefix + name
			if parameter[0]['text']:
				ret += "[%s]" % parameter[0]['text']
			ret += "{%s}{%s}" % (parameter[1]['text'], tex_name)
			return ret
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
		elif name.startswith("\\bibliographystyle"):
			if self.use_biblio:
				tex_name = parameter[0]['text']
				filename = self.__make_filename(tex_name, '.bst')
				if self.__is_document_file(filename):
					tex_name = self.__create_mapping(filename, '.bst')
					self.__files_to_copy.add(filename)
				return "%s{%s}" % (name, tex_name)
			return None
		elif name.startswith("\\bibliography"):
			if self.use_biblio:
				tex_name = parameter[0]['text']
				filename = self.__make_filename(tex_name, '.bib')
				if self.__is_document_file(filename):
					tex_name = self.__create_mapping(filename, '.bib')
					self.__files_to_copy.add(filename)
				return "%s{%s}" % (name, tex_name)
			else:
				if len(name) > 13:
					bibdb = name[13:]
				else:
					bibdb = self.basename
				bbl_file = bibdb + ".bbl"
				if not os.path.isabs(bbl_file):
					bbl_file = os.path.join(self.dirname, bbl_file)
				if os.path.isfile(bbl_file):
					with open(bbl_file) as f:
						content = f.read()
					return textwrap.dedent("""
							%%=======================================================
							%%== BEGIN FILE: %s
							%%=======================================================
							%s
							%%=======================================================
							""") % (os.path.basename(bbl_file), content)
				else:
					logging.error(_T('File not found: %s'), bbl_file)
		elif name == "\\addbibresource":
			if self.use_biblio:
				tex_name = parameter[1]['text']
				filename = self.__make_filename(tex_name, '.bib')
				if self.__is_document_file(filename):
					tex_name = self.__create_mapping(filename, '.bib')
					self.__files_to_copy.add(filename)
				return "%s{%s}" % (name, tex_name)
			else:
				return None
		# Reply the raw text back to the generated TeX document.
		return raw_text

	def __make_filename(self, basename : str, *ext : str) -> str:
		"""
		Create a valid filename for the flattening process.
		:param basename: The basename.
		:param basename: str
		:param ext: The filename extension (default: None).
		:param ext: list(str)
		"""
		name = basename
		for one_ext in ext:
			if one_ext and not basename.endswith(ext):
				name = basename + one_ext
				continue
		if not os.path.isabs(name):
			return os.path.join(self.dirname, name)
		return name

	def __is_document_file(self, filename : str) -> bool:
		"""
		Replies if the given file is a part of the document.
		:param filename: The filename to test.
		:type filename: str
		:return: True if the file is a part of the document; otherwise False.
		:rtype: bool
		"""
		if not os.path.isabs(filename):
			filename = os.path.join(self.dirname, filename)
		if os.path.isfile(filename):
			return filename.startswith(self.dirname)
		return False

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
					return os.path.basename(self.__source2target[tex_name]), ''

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
				logging.error(_T('Picture not found: %s'), tex_name)
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
						self.__files_to_copy.add(filename)
						selected_name2 = tex_name
				if selected_name1:
					tex_name, filename = selected_name1
					logging.debug(_T('Embedding %s'), filename)
					with open(filename) as f:
						filecontent = f.read()
					# Replacing the filename in the newly embedded TeX file
					if self.__source2target:
						for source in self.__source2target:
							filecontent = filecontent.replace('{' + source + '}',
											'{' + self.__source2target[source] + '}')
					prefix +=	textwrap.dedent("""
								%%=======================================================
								%%== BEGIN FILE: %s
								%%=======================================================
								\\begin{filecontents*}{%s}
								%s
								\\end{filecontents*}
								%%=======================================================
								""") % (os.path.basename(tex_name), os.path.basename(tex_name), filecontent)
					self.__dynamic_preamble.append('\\usepackage{filecontents}')
				elif selected_name2:
					tex_name = selected_name2
		else:
			ext = os.path.splitext(tex_name)[1] or ''
			tex_name = self.__create_mapping(filename, ext) + ext
			self.__files_to_copy.add(filename)

		return (tex_name, prefix)

	def _analyze_document(self) -> str:
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

		# Replace PREAMBLE content
		if self.__tex_file_content:
			preamble = '\n'.join(self.__dynamic_preamble)
			if not preamble:
				preamble = ''
			content = self.__tex_file_content.replace('%========= AUTOLATEX PREAMBLE', preamble, 1)

		# Clean the content by removing empty lines
		content = content.replace('\t', ' ').strip()
		content = re.sub("\n+[ \t]*", "\n", content, re.S)

		return content

	def _generate_flat_document(self,  content : str) -> bool:
		"""
		Generate the flat document.
		:param content: The content of the file.
		:type content: str
		:return: The success status of the generation.
		:rtype: bool
		"""
		# Create the output directory
		os.makedirs(self.output_directory)

		# Create the main TeX file
		output_file = os.path.join(self.output_directory, self.basename) + '.tex'

		logging.debug(_T('Writing %s') % output_file)
		with open(output_file, 'w') as f:
			f.write(content)

		# Copy the resources
		for source in self.__files_to_copy:
			target = self.__source2target[source]
			target = os.path.join(self.output_directory, target)
			logging.debug(_T('Copying resource %s to %s') % (source, target))
			target_directory = os.path.dirname(target)
			if not os.path.isdir(target_directory):
				os.makedirs(target_directory)
			shutil.copy(source, target)
		return True

	def run(self) -> bool:
		"""
		Make the input file standalone.
		:return: True if the execution is a success, otherwise False.
		"""
		self.__init()
		content = self._analyze_document()
		logging.debug(_T("File content: %s") % content)
		return self._generate_flat_document(content)

	@override
	def comment(self, parser: Parser, raw: str, comment: str) -> str | None:
		return None


