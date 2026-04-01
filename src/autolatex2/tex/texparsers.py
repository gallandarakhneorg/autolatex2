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
TeX parser.
"""

import re
import logging
from typing import override

from autolatex2.tex.mathmode import MathMode
from autolatex2.tex.parser import Parser
from autolatex2.tex.texobservers import Observer
from autolatex2.tex.utils import TeXMacroParameter
from autolatex2.utils.i18n import T
from autolatex2.utils.extlogging import LogLevel


class TeXParser(Parser):
	"""
	Parser of a TeX file.

	= Macro Prototype =

	The specification of the macro prototypes must be a sequence (eventually empty) of:
	* {} for a mandatory parameter;
	* [d] for an optional parameter, where d is the default value given to this parameter if it is not provided inside the LaTeX code;
	* \\ for a LaTeX command name;
	* ! for indicating that the following sign ({} or []) must not be interpreted by the LaTeX parser. It must be used for verbatim output.
	* - for reading the text until the end of the current LaTeX context.
	"""

	def __init__(self):
		"""
		Constructor.
		"""
		self.__put_back_text : str | None = ''
		self.__default_text_mode_macros : dict[str,str] | None = None
		self.__default_math_mode_macros : dict[str,str] | None  = None
		self.__default_text_mode_active_characters : dict[str,str] | None = None
		self.__default_math_mode_active_characters : dict[str,str] | None = None
		self.__default_comment_characters : list[str] | None = None
		self.__observer : Observer | None = None
		self.__filename : str | None = None
		self.__math_mode : MathMode | None = None
		self.__text_mode_macros : dict[str,str] | None = None
		self.__math_mode_macros : dict[str,str] | None = None
		self.__text_mode_active_characters : dict[str,str] | None = None
		self.__math_mode_active_characters : dict[str,str] | None = None
		self.__comment_characters : list[str] | None = None
		self.__separators : list[str] = []
		self.__stop_parsing : bool = False

	@property
	def default_text_mode_macros(self) -> dict[str,str]:
		"""
		Definition of the default text-mode macros.
		:return: the macros in text mode.
		:rtype: dict[str,str]
		"""
		if self.__default_text_mode_macros is None:
			self.__default_text_mode_macros = {
				' '                 : '',
				'_'                 : '',
				'-'                 : '',
				'$'                 : '',
				','                 : '',
				';'                 : '',
				'%'                 : '',
				'}'                 : '',
				'{'                 : '',
				'\\'                : '',
				'&'                 : '',
				'#'		     		: '',
				'\''                : '{}',
				'`'                 : '{}',
				'~'                 : '{}',
				'"'                 : '{}',
				'^'                 : '{}',
				'='                 : '{}',
				'AA'                : '',
				'aa'                : '',
				'AE'                : '',
				'ae'                : '',
				'begin'             : '!{}',
				'backslash'         : '',
				'beginblock'        : '',
				'bibliographystyle' : '!{}',
				'bibliography'      : '!{}',
				'bf'                : '-',
				'bfseries'          : '-',
				'BibTeX'            : '',
				'c'                 : '{}',
				'caption'	    	: '{}',
				'centering'	    	: '-',
				'cdot'              : '',
				'cdots'             : '',
				'cite'              : '[]{}',
				'def'               : '\\{}',
				'degree'            : '',
				'dg'                : '',
				'DH'                : '',
				'div'               : '',
				'edef'              : '\\{}',
				'Emph'              : '{}',
				'em'                : '-',
				'emph'              : '{}',
				'end'               : '!{}',
				'enditemize'        : '',
				'ensuremath'        : '{}',
				'euro'        	    : '',
				'footnotesize'      : '-',
				'gdef'              : '\\{}',
				'global'            : '',
				'guillemotleft'     : '',
				'guillemotright'    : '',
				'Huge'              : '-',
				'html'              : '!{}',
				'huge'              : '-',
				'i'                 : '',
				'include'	    	: '!{}',
				'includegraphics'   : '[]!{}',
				'indexentry'	    : '{}',
				'input'		    	: '!{}',
				'it'                : '-',
				'item'              : '[]',
				'itshape'           : '-',
				'L'		     		: '',
				'label'		    	: '{}',
				'LARGE'             : '-',
				'Large'             : '-',
				'LaTeX'             : '',
				'large'             : '-',
				'ldot'				: '',
				'ldots'				: '',
				'lnot'              : '',
				'mdseries'          : '-',
				'newcommand'        : '{}[][]{}',
				'newif'             : '\\',
				'normalfont'        : '-',
				'normalsize'        : '-',
				'O'                 : '',
				'o'                 : '',
				'OE'                : '',
				'oe'                : '',
				'P'                 : '',
				'pm'                : '',
				'pounds'            : '',
				'providecommand'    : '{}[][]{}',
				'ref'		    	: '{}',
				'relax'             : '',
				'renewcommand'      : '{}[][]{}',
				'rm'                : '-',
				'rmfamily'          : '-',
				'S'                 : '',
				'sc'                : '-',
				'scriptsize'        : '-',
				'scshape'           : '-',
				'sf'                : '-',
				'sffamily'          : '-',
				'sl'                : '-',
				'slshape'           : '-',
				'small'             : '-',
				'smash'             : '{}',
				'ss'                : '',
				'startblock'        : '',
				'startitemize'      : '',
				'string'            : '{}',
				'TeX'               : '',
				'text'              : '{}',
				'textasciicircum'   : '',
				'textasciitilde'    : '',
				'textbackslash'     : '',
				'textbf'            : '{}',
				'textbrokenbar'     : '',
				'textcent'          : '',
				'textcopyright'     : '',
				'textcurrency'      : '',
				'textexcladown'     : '',
				'textit'            : '{}',
				'textmd'            : '{}',
				'textnormal'        : '{}',
				'textonehalf'       : '',
				'textonequarter'    : '',
				'textordfeminine'   : '',
				'textordmasculine'  : '',
				'textquestiondown'  : '',
				'textregistered'    : '',
				'textrm'            : '{}',
				'textsc'            : '{}',
				'textsf'            : '{}',
				'textsl'            : '{}',
				'textthreequarters' : '',
				'texttt'            : '{}',
				'textup'            : '{}',
				'textyen'           : '',
				'times'             : '',
				'tiny'              : '-',
				'TH'                : '',
				'th'                : '',
				'tt'                : '-',
				'ttfamily'          : '-',
				'u'                 : '{}',
				'underline'         : '{}',
				'uline'             : '{}',
				'upshape'           : '{}',
				'url'               : '[]{}',
				'v'                 : '{}',
				'xdef'              : '\\{}',
				'xspace'            : '',
				# From S. Galland templates
				'animatedfigureslide': '[]{}!{}',
				'figureslide': '[]{}!{}',
				'libraryslide': '[]!{}{}{}{}{}',
				'partnerlogo': '!{}',
				'resolvedfilename': '',
				'resolvepicturename': '!{}',
				'sidecite': '!{}',
			}
		assert self.__default_text_mode_macros is not None
		return self.__default_text_mode_macros

	@property
	def default_math_mode_macros(self) -> dict[str,str]:
		"""
		Definition of the default math-mode macros.
		:return: the macros in math mode.
		:rtype: dict[str,str]
		"""
		if self.__default_math_mode_macros is None:
			self.__default_math_mode_macros = {
				'}'					: '',
				'{'					: '',
				'&'					: '',
				','                 : '',
				';'                 : '',
				'%'                 : '',
				'_'					: '',
				'\\'                : '',
				'mathmicro'			: '',
				'maththreesuperior'	: '',
				'mathtwosuperior'	: '',
				'alpha'				: "",
				'angle'				: "",
				'approx'			: "",
				'ast'				: "",
				'beta'				: "",
				'bot'				: "",
				'bullet'			: "",
				'cap'				: "",
				'cdot'				: "",
				'cdots'				: "",
				'chi'				: "",
				'clubsuit'			: "",
				'cong'				: "",
				'cup'				: "",
				'dagger'			: "",
				'ddagger'			: "",
				'delta'				: "",
				'Delta'				: "",
				'dfrac'				: "{}{}",
				'diamondsuit'		: "",
				'div'				: "",
				'downarrow'			: "",
				'Downarrow'			: "",
				'emptyset'			: "",
				'epsilon'			: "",
				'Epsilon'			: "",
				'equiv'				: "",
				'eta'				: "",
				'exists'			: "",
				'forall'			: "",
				'frac'				: "{}{}",
				'gamma'				: "",
				'Gamma'				: "",
				'ge'				: "",
				'heartsuit'			: "",
				'Im'				: "",
				'in'				: "",
				'indexentry'		: '{}',
				'infty'				: "",
				'infinity'			: "",
				'int'				: "",
				'iota'				: "",
				'kappa'				: "",
				'lambda'			: "",
				'Lambda'			: "",
				'langle'			: "",
				'lceil'				: "",
				'ldot'				: "",
				'ldots'				: "",
				'leftarrow'			: "",
				'Leftarrow'			: "",
				'leftrightarrow'	: "",
				'Leftrightarrow'	: "",
				'le'				: "",
				'lfloor'			: "",
				'mathbb'			: '{}',
				'mathbf'			: '{}',
				'mathit'			: '{}',
				'mathrm'			: '{}',
				'mathsf'			: '{}',
				'mathtt'  			: '{}',
				'mathnormal'		: '{}',
				'mu'				: "",
				'nabla'				: "",
				'ne'				: "",
				'neq'				: "",
				'ni'				: "",
				'not'				: "!{}",
				'nu'				: "",
				'omega'				: "",
				'Omega'				: "",
				'ominus'			: "",
				'oplus'				: "",
				'oslash'			: "",
				'Oslash'			: "",
				'otimes'			: "",
				'partial'			: "",
				'phi'				: "",
				'Phi'				: "",
				'pi'				: "",
				'Pi'				: "",
				'pm'				: "",
				'prime'				: "",
				'prod'				: "",
				'propto'			: "",
				'psi'				: "",
				'Psi'				: "",
				'rangle'			: "",
				'rceil'				: "",
				'Re'				: "",
				'rfloor'			: "",
				'rho'				: "",
				'rightarrow'		: "",
				'Rightarrow'		: "",
				'sfrac'				: "{}{}",
				'sigma'				: "",
				'Sigma'				: "",
				'sim'				: "",
				'spadesuit'			: "",
				'sqrt'				: "",
				'subseteq'			: "",
				'subset'			: "",
				'sum'				: "",
				'supseteq'			: "",
				'supset'			: "",
				'surd'				: "",
				'tau'				: "",
				'text'              : '{}',
				'theta'				: "",
				'Theta'				: "",
				'times'				: "",
				'to'				: "",
				'uparrow'			: "",
				'Uparrow'			: "",
				'upsilon'			: "",
				'Upsilon'			: "",
				'varpi'				: "",
				'vee'				: "",
				'wedge'				: "",
				'wp'				: "",
				'xi'				: "",
				'Xi'				: "",
				'xspace'			: "",
				'zeta'				: "",
			}
		assert self.__default_math_mode_macros is not None
		return self.__default_math_mode_macros

	@property
	def default_text_mode_active_characters(self) -> dict[str,str]:
		"""
		Definitions of the default active characters in text mode.
		:return: the active characters in text mode.
		:rtype: dict[str,str]
		"""
		if self.__default_text_mode_active_characters is None:
			self.__default_text_mode_active_characters = dict()
		assert self.__default_text_mode_active_characters is not None
		return self.__default_text_mode_active_characters

	@property
	def default_math_mode_active_characters(self) -> dict[str,str]:
		"""
		Definitions of the default active characters in math mode.
		:return: the active characters in math mode.
		:rtype: dict[str,str]
		"""
		if self.__default_math_mode_active_characters is None:
			self.__default_math_mode_active_characters = {
				'_'		: "{}",
				'^'		: "{}",
			}
		assert self.__default_math_mode_active_characters is not None
		return self.__default_math_mode_active_characters

	@property
	def default_comment_characters(self) -> list[str]:
		"""
		Definition of the default characters for comments.
		:return: the list of comment characters.
		:rtype: list[str]
		"""
		if self.__default_comment_characters is None:
			self.__default_comment_characters = [
				'%',
			]
		assert self.__default_comment_characters is not None
		return self.__default_comment_characters

	@property
	def observer(self) -> Observer:
		"""
		Return the observer on the internal parser events.
		:return: The observer.
		:rtype: Observer
		"""
		assert self.__observer is not None
		return self.__observer

	@observer.setter
	def observer(self, observer : Observer):
		"""
		Set an observer on the internal parser events.
		:param observer: The observer.
		:type observer: Observer
		"""
		self.__observer = observer

	@property
	def filename(self) -> str:
		return self.__filename or ''

	@filename.setter
	def filename(self, n : str):
		self.__filename = n

	@property
	@override
	def math_mode(self) -> MathMode | None:
		"""
		Replies if the math mode is active.
		:return: The math mode.
		:rtype: MathMode | None
		"""
		return self.__math_mode

	@math_mode.setter
	def math_mode(self, mode : MathMode | None):
		"""
		Set if the math mode is active.
		:param mode: The math mode or None if the parser must be in text mode.
		:type mode: MathMode | None
		"""
		self.__math_mode = mode

	@property
	def text_mode_macros(self) -> dict[str,str]:
		"""
		List of the macros in text mode.
		See the explanation in the class documentation for the format of the macro prototype.
		:return: the dictionary of macros; keys are macro names; values are macro prototype.
		:rtype: dict[str,str]
		"""
		self.__ensure_text_mode_macros()
		assert self.__text_mode_macros is not None
		return self.__text_mode_macros

	def __ensure_text_mode_macros(self):
		if self.__text_mode_macros is None:
			self.__text_mode_macros = dict()
			assert self.__text_mode_macros is not None
			self.__text_mode_macros.update(self.default_text_mode_macros)

	def add_text_mode_macro(self, name : str, prototype : str):
		"""
		Add a macro for the text mode.
		See the explanation in the class documentation for the format of the macro prototype.
		:param name: The name of the macro.
		:type name: str
		:param prototype: The prototype of the macro.
		:type prototype: str
		"""
		self.__ensure_text_mode_macros()
		assert self.__text_mode_macros is not None
		self.__text_mode_macros[name] = prototype

	@property
	def math_mode_macros(self) -> dict[str,str]:
		"""
		List of the macros in math mode.
		See the explanation in the class documentation for the format of the macro prototype.
		:return: the dictionary of macros; keys are macro names; values are macro prototype.
		:rtype: dict[str : str]
		"""
		self.__ensure_math_mode_macros()
		assert self.__math_mode_macros is not None
		return self.__math_mode_macros

	def __ensure_math_mode_macros(self):
		if self.__math_mode_macros is None:
			self.__math_mode_macros = dict()
			assert self.__math_mode_macros is not None
			self.__math_mode_macros.update(self.default_math_mode_macros)

	def add_math_mode_macro(self, name : str, prototype : str):
		"""
		Add a macro for the math mode.
		See the explanation in the class documentation for the format of the macro prototype.
		:param name: The name of the macro.
		:type name: str
		:param prototype: The prototype of the macro.
		:type prototype: str
		"""
		self.__ensure_math_mode_macros()
		assert self.__math_mode_macros is not None
		self.__math_mode_macros[name] = prototype

	@property
	def text_mode_active_characters(self) -> dict[str,str]:
		"""
		List of the active characters in text mode.
		See the explanation in the class documentation for the format of the macro prototype.
		:return: the dictionary of macros; keys are active characters; values are macro prototype.
		:rtype: dict[str : str]
		"""
		self.__ensure_text_mode_active_characters()
		assert self.__text_mode_active_characters is not None
		return self.__text_mode_active_characters

	def __ensure_text_mode_active_characters(self):
		if self.__text_mode_active_characters is None:
			self.__text_mode_active_characters = dict()
			assert self.__text_mode_active_characters is not None
			self.__text_mode_active_characters.update(self.default_text_mode_active_characters)

	def add_text_mode_active_character(self, character: str, prototype : str):
		"""
		Add an active character for the text mode.
		See the explanation in the class documentation for the format of the macro prototype.
		:param character: The active character.
		:type character: str
		:param prototype: The prototype of the active character.
		:type prototype: str
		"""
		self.__ensure_text_mode_active_characters()
		assert self.__text_mode_active_characters is not None
		self.__text_mode_active_characters[character] = prototype
		self.separators = None

	@property
	def math_mode_active_characters(self) -> dict[str,str]:
		"""
		List of the active characters in math mode.
		See the explanation in the class documentation for the format of the macro prototype.
		:return: the dictionary of macros; keys are active characters; values are macro prototype.
		:rtype: dict[str,str]
		"""
		self.__ensure_math_mode_active_characters()
		assert self.__math_mode_active_characters is not None
		return self.__math_mode_active_characters

	def __ensure_math_mode_active_characters(self):
		if self.__math_mode_active_characters is None:
			self.__math_mode_active_characters = dict()
			assert self.__math_mode_active_characters is not None
			self.__math_mode_active_characters.update(self.default_math_mode_active_characters)

	def add_math_mode_active_character(self, character : str, prototype : str):
		"""
		Add an active character for the math mode.
		See the explanation in the class documentation for the format of the macro prototype.
		:param character: The active character.
		:type character: str
		:param prototype: The prototype of the active character.
		:type prototype: str
		"""
		self.__ensure_math_mode_active_characters()
		assert self.__math_mode_active_characters is not None
		self.__math_mode_active_characters[character] = prototype
		self.separators = None

	@property
	def comment_characters(self) -> list[str]:
		"""
		List of the comment characters.
		:return: the list of characters.
		:rtype: list[str]
		"""
		if self.__comment_characters is None:
			self.__comment_characters = list()
			assert self.__comment_characters is not None
			self.__comment_characters.extend(self.default_comment_characters)
		return self.__comment_characters

	@property
	def separators(self) -> list[str]:
		"""
		List of the separators used by the parser.
		:return: the list of the separators.
		:rtype: list[str]
		"""
		return self.__separators

	@separators.setter
	def separators(self, s : list[str]):
		"""
		Change of the separators used by the parser.
		:param s: the list of the separators.
		:type s: list[str]
		"""
		self.__separators = s or list()

	def parse(self, text : str, lineno : int = 1):
		"""
		Parse the specified string and invoke the listeners on the TeX tokens.
		:param text: The string to parse.
		:type text: str
		:param lineno: The line number where the text can be found (default: 1).
		:type lineno: int
		"""
		if lineno < 1:
			lineno = 1
		# Search the first separator
		eaten, sep, text, cr_count = self.__eat_to_separator(text)

		self.__stop_parsing = False
		self.__math_mode = None

		while sep:

			# Stop parsing
			if self.__stop_parsing:
				return None

			lineno += cr_count

			# Parse the already eaten string
			if eaten and self.observer is not None:
				self.observer.text(self, eaten)

			if sep == '{':
				c = self.observer.open_block(self, sep)
				if c is not None:
					self.observer.text(self, c)
			elif sep == '}':
				c = self.observer.close_block(self, sep)
				if c is not None:
					self.observer.text(self, c)
			elif sep == '\\':
				c, text = self.__parse_cmd(text, lineno, '\\')
				if c is not None:
					self.observer.text(self, c)
			elif sep == '$':
				# Math mode
				if self.math_mode is None:
					c = self.observer.open_math(self, True)
					self.math_mode = MathMode.inline
					if c is not None:
						self.observer.text(self, c)
				elif self.math_mode == MathMode.inline:
					c = self.observer.close_math(self, True)
					self.math_mode = None
					if c is not None:
						self.observer.text(self, c)
				else:
					logging.debug(
						T("you try to close with a '\\$' a mathematical mode opened with '\\[' (%s:%d)") % (self.filename, lineno))
			elif sep in self.comment_characters:
				# Comment
				r = re.match(r'^(.*?)[\n\r](.*)$', text, re.DOTALL)
				if r: # Not a comment until the end-of-file
					comment_text = r.group(1)
					text = r.group(2)
				else:
					comment_text = text
					text = ''
				
				c = self.observer.comment(self, sep + comment_text, comment_text.strip())
				if c is not None:
					self.observer.text(self, c)
			else:
				is_text = sep in self.text_mode_active_characters
				is_math = sep in self.math_mode_active_characters
				if is_text or is_math:
					if self.math_mode is not None:
						if not is_math:
							logging.debug(
								T("you cannot use in text mode the active character '%s', which is defined in math mode (%s:%d)") % (sep, self.filename, lineno))
							if sep is not None:
								self.observer.text(self, sep)
						else:
							c, text = self.__parse_active_char(sep + text, lineno)
							if c is not None:
								self.observer.text(self, c)
					elif not is_text:
						logging.debug(
							T("you cannot use in math mode the active character '%s', which is defined in text mode (%s:%d)") % (sep, self.filename, lineno))
						if sep is not None:
							self.observer.text(self, sep)
					else:
						c, text = self.__parse_active_char(sep + text, lineno)
						if c is not None:
							self.observer.text(self, c)
				else: # Unknow separator, treat as text
					if sep is not None:
						self.observer.text(self,sep)

			# Search the next separator
			eaten, sep, text, cr_count = self.__eat_to_separator(text)

		if text is not None:
			self.observer.text(self, text)

		return None

	@override
	def put_back(self, text : str):
		"""
		Reinject a piece of text inside the parsed text in a way that it will
		be the next text to be parsed by this object.
		:param text: The text to reinject.
		:type text: str
		"""
		if text:
			self.__put_back_text = text

	@override
	def stop(self):
		"""
		Stop the parsing. The function parse() will stop its current loop.
		"""
		self.__stop_parsing = True

	def __eat_to_separator(self, text : str, *seps : str) -> tuple[str,str|None,str,int]:
		"""
		Eats the specified text until the first separator.
		:param text: The text to eat.
		:type text: str
		:param seps: The list of additional separators to consider.
		:type seps: str
		:return: the tuple (eaten text, detected separator, not eatend text, number of CR)
		:rtype: tuple[str,str|None,str,int]
		"""
		if text is None:
			text = ''
		if seps is None:
			seps = ()

		if self.__put_back_text:
			text = self.__put_back_text + text
			self.__put_back_text = None

		separators = set()
		std_separators = self.separators
		if std_separators:
			separators.update(std_separators)
		else:
			separators.update(self.__build_separators())

		separators.update(seps)

		ret1 = ''
		sep = None
		after = ''
		cr_count = 0

		regex = '^(.*?)(\n|\r'
		for s in separators:
			regex += '|'
			regex += '(?:' + str(re.escape(s)) + ')'
		regex += ')(.*)$'
		r = re.match(regex, text, re.DOTALL)
		while r:
			before = r.group(1)
			sep = r.group(2)
			text = r.group(3)
			ret1 += before
			if sep != "\n":
				return ret1, sep, text, cr_count
			ret1 += "\n"
			cr_count += 1
			r = re.match(regex, text, re.DOTALL)
	
		if text:
			ret1 += text
			sep = None
			after = ''

		return ret1, sep, after, cr_count

	def __build_separators(self) -> list[str]:
		"""
		Build a list of separators.
		:return: The list of separators.
		:rtype: list[str]
		"""
		sep_set = set()
		sep_set.update(self.comment_characters)
		sep_set.update(self.text_mode_active_characters.keys())
		sep_set.update(self.math_mode_active_characters.keys())
		sep_set.update( { '{', '}', '$', '\\' } )
		seps = list()
		for v in sep_set:
			seps.append(v)
		self.separators = seps
		return seps

	def __parse_cmd(self, text : str, lineno : int, prefix : str = '') -> tuple[str,str]:
		"""
		Parse a TeX command.
		:param text: The text, which follows the backslash, to scan.
		:type text: str
		:param lineno: The line number.
		:type lineno: int
		:param prefix: A prefix merged to the command name. Use carefully.
		:type prefix: str
		:return: the tuple (the result of expansion of the macro, the rest of the tex text after the macro).
		:rtype: tuple[str,str]
		"""
		expand_to = ''

		r = re.match(r'^\[(.*)', text, re.DOTALL)
		if r: # Starts multi-line math mode
			text = r.group(1)
			expand_to = self.observer.open_math(self, False)
			self.math_mode = MathMode.block
		else:
			r = re.match(r'^](.*)', text, re.DOTALL)
			if r: # Stop multi-line math mode
				text = r.group(1)
				expand_to = self.observer.close_math(self, False)
				self.math_mode = None
			else:
				r = re.match(r'^([a-zA-Z]+\*?|.)(.*)', text, re.DOTALL)
				if r: # default LaTeX command
					cmd_name = r.group(1)
					text = r.group(2)
					trans = self.__search_cmd_trans(cmd_name, lineno, (prefix != "\\"))
					if not trans:
						trans = ''
					expand_to, text = self.__run_cmd(prefix + cmd_name, trans, text, lineno)
				else:
					logging.log(LogLevel.FINE_WARNING, T("invalid syntax for the TeX command: %s (lineno: %d)"), prefix + text, lineno)
		if expand_to is None:
			expand_to = ''
		return expand_to, text

	def __parse_active_char(self, text : str, lineno : int) -> tuple[str,str]:
		"""
		Parse a TeX active character.
		:param text: The text, with the active char, to scan.
		:type text: str
		:param lineno: Line number.
		:type lineno: int
		:return: the rest of the tex text, after the active character.
		:rtype: tuple[str,str]
		"""
		r = re.match(r'^(.)(.*)', text, re.DOTALL)
		if r: # default LaTeX command
			active_char = r.group(1)
			text = r.group(2)
			trans = self.__search_cmd_trans(active_char, lineno, True)
			if not trans:
				trans = ''
			expand_to, text = self.__run_cmd(active_char, trans, text, lineno)
		else:
			logging.log(LogLevel.FINE_WARNING, T("invalid syntax for the TeX active character: %s (lineno: %d)"), text, lineno)
			expand_to = text[0:1] if len(text) > 0 else ''
			text = text[1:] if len(text) > 0 else ''

		return expand_to, text

	def __search_cmd_trans(self, name : str, lineno : int, special : bool = False):
		"""
		Replies the macro definition that corresponds to
		the specified TeX command.
		:param name: The name of the TeX command to search.
		:type name: str
		:param lineno: Line number.
		:type lineno: int
		:param special: Indicates if the searched command has a special purpose (example: _ in math mode).
		:type: bool
		"""
		found_math = False
		found_text = False
		math = None
		text = None

		if name:

			if special:
				if name in self.math_mode_active_characters:
					found_math = True
					math = self.math_mode_active_characters[name]
				if name in self.text_mode_active_characters:
					found_text = True
					text = self.text_mode_active_characters[name]
			else:
				if name in self.math_mode_macros:
					found_math = True
					math = self.math_mode_macros[name]
				if name in self.text_mode_macros:
					found_text = True
					text = self.text_mode_macros[name]

			if not found_text and not found_math:
				proto = self.observer.find_macro(self, name, special, (self.math_mode is not None))
				if proto:
					if self.math_mode is not None:
						found_math = True
						math = proto
					else:
						found_text = True
						text = proto

		logging.debug(T("Found parameter definition for '%s': math=%s; text=%s (%s:%d)") % (name, (math or '<undef>'), (text or '<undef>'), self.filename, lineno))

		if found_math or found_text:
			if self.math_mode is not None:
				if not found_math:
					logging.debug(T("the command %s%s was not defined for math-mode, assumes to use the text-mode version instead (lineno: %d)"),
							( '' if special else '\\' ), name, lineno)
					return text
				else:
					return math
			elif not found_text:
				logging.debug(T("the command %s%s was not defined for text-mode, assumes to use the math-mode version instead (lineno: %d)"),
						( '' if special else '\\' ), name, lineno)
				return math
			else:
				return text

		return None

	def __run_cmd(self, name : str, trans : str, text : str, lineno : int) -> tuple[str,str]:
		"""
		Execute the specified macro on the specified tex string.
		:param name: The name of the TeX macro.
		:type name: str
		:param trans: The definition for the macro.
		:type trans: str
		:param text: The text from which some data must be extracted to treat the macro.
		:type text: str
		:param lineno: The line number where the text starts.
		:param lineno: int
		:return: the rest of the tex text, after the active character.
		:rtype: tuple[str,str]
		"""
		if trans:
			# This macro has params
			logging.debug(T("Expanding '%s' (%s:%d)") % (name, self.filename, lineno))
			text, params, raw_params = self.__eat_cmd_parameters(trans, text, name, lineno)
			# Apply the macro
			expand_to = self.observer.expand(self, name + raw_params, name, *params)
		else:
			# No param, put the string inside the output stream
			logging.debug(T("Expanding '%s' (%s:%d)") % (name, self.filename, lineno))
			expand_to = self.observer.expand(self, name, name)
		return expand_to, text

	def __eat_cmd_parameters(self, p_params : str, text : str, macro : str, lineno : int) -> tuple[str,list[TeXMacroParameter],str]:
		"""
		Eat the parameters for a macro.
		:param p_params: The description of the parameters to eat.
		:type p_params: str
		:param text: The text from which some data must be extracted.
		:type text: str
		:param macro: The name of the macro for which parameters must be extracted.
		:type macro: str
		:param lineno: The line number.
		:type lineno: int
		:return: The tuple (the rest of the text, the array of parameters, the raw representation of the parameters)
		:rtype: tuple[str,list[TexMacroParameter],str]
		"""
		extracted_parameters : list[TeXMacroParameter] = list()
		raw_params = ''
		param_index = 0
		logging.debug(T("Macro prototype of '%s': %s (%s:%d)") % (macro, p_params, self.filename, lineno))
		for p in re.findall(r'(!?\{}|!?\[[^]]*]|-|\\)', p_params, re.DOTALL):
			# Eats no significant white spaces
			r = re.match(r'^(!?)\{}', p, re.DOTALL)
			if r: # Eats a mandatory parameter
				optional = r.group(1) or ''
				prem = text[0:1]
				text = text[1:]
				if prem == '{':
					context, text = self.__eat_context(text, '\\}')
					extracted_parameters.append(
						TeXMacroParameter(
							index=param_index,
							macro_name=False,
							optional=False,
							evaluable=optional != '!',
							text=context))
					raw_params += "{" + context + "}"
				elif prem == '\\':
					if optional != '!':
						# The following macro is expandable
						c, text = self.__parse_cmd(text, lineno, '\\')
						extracted_parameters.append(
							TeXMacroParameter(
								index=param_index,
								macro_name=True,
								optional=False,
								evaluable=True,
								text=c))
						raw_params += c
					else:
						# The following macro is not expandable
						r = re.match(r'^([a-zA-Z]+\*?|.)(.*)$', text, re.DOTALL)
						c = r.group(1)
						text = r.group(2)
						extracted_parameters.append(
							TeXMacroParameter(
								index=param_index,
								macro_name=True,
								optional=False,
								evaluable=False,
								text=c))
						raw_params += "\\" + c
				else:
					extracted_parameters.append(
						TeXMacroParameter(
							index=param_index,
							macro_name=False,
							optional=False,
							evaluable=optional != '!',
							text=prem))
					raw_params += prem
			else:
				r = re.match(r'^(!?)\[([^]]*)]', p, re.DOTALL)
				if r: # Eats an optional parameter
					optional = r.group(1) or ''
					default_val = r.group(2) or ''
					prem = text[0:1]
					if prem == '[':
						context, text = self.__eat_context(text[1:], ']')
						extracted_parameters.append(
							TeXMacroParameter(
								index=param_index,
								macro_name=False,
								optional=True,
								evaluable=optional != '!',
								text=context))
						raw_params += "[" + context + "]"
					else:
						# Assume default value
						extracted_parameters.append(
							TeXMacroParameter(
								index=param_index,
								macro_name=False,
								optional=True,
								evaluable=optional != '!',
								text=default_val))
				elif p == '\\': # Eats a TeX command name
					r = re.match(r'^\\([a-zA-Z]+\*?|.)(.*)$', text, re.DOTALL)
					if r:
						n = r.group(1)
						text = r.group(2)
						extracted_parameters.append(
							TeXMacroParameter(
								index=param_index,
								macro_name=True,
								optional=False,
								evaluable=True,
								text=n))
						raw_params += "\\" + n
					else:
						msg = text[0:50]
						msg = re.sub('[\n\r]', '\\n', msg, 0, re.DOTALL)
						msg = msg.replace("\t", "\\t")
						logging.log(LogLevel.FINE_WARNING, T("expected a TeX macro for expanding the macro %s, here: '%s' (%s:%d)") % (macro, msg, self.filename, lineno))
						extracted_parameters.append(
							TeXMacroParameter(
								index=param_index,
								macro_name=True,
								optional=False,
								evaluable=True,
								text=''))
						raw_params += "\\"
				elif p == '-': # Eats until the end of the current context
					context, text = self.__eat_context(text, '\\}')
					extracted_parameters.append(
						TeXMacroParameter(
							index=param_index,
							macro_name=False,
							optional=False,
							evaluable=True,
							text=context))
					raw_params += context
				else:
					raise Exception(T("unable to recognize the following argument specification: %s") % p)
			param_index = param_index + 1
		return text, extracted_parameters, raw_params


	def __eat_context(self, text : str, end_delim : str) -> tuple[str,str]:
		"""
		Eat the current context.
		:param text: The text from which some data must be extracted.
		:type text: str
		:param end_delim: The ending separator.
		:type end_delim: str
		:rtype: tuple[str,str]
		"""
		context = ''
		context_level = 0

		# Search the first separator
		eaten, sep, text, cr_count = self.__eat_to_separator(text, end_delim)
		while sep:

			if sep == '{': # open a context
				context_level += 1
				eaten += sep
			elif sep == '}': # close a context
				if context_level <= 0:
					return context + eaten, text
				eaten += sep
				context_level -= 1
			elif sep == '\\':
				r = re.match(r'^([a-zA-Z]+\*?|.)(.*)$', text, re.DOTALL)
				eaten += "\\" + r.group(1)
				text = r.group(2)
			elif (context_level <= 0) and (re.match(str(re.escape(end_delim)), str(sep), re.DOTALL)): # The closing delimiter was found
				return context + eaten, text
			else: # Unknow separator, treat as text
				eaten += sep

			# Translate the text before the separator
			context += eaten

			# Search the next separator
			eaten, sep, text, cr_count = self.__eat_to_separator(text, end_delim)

		return context + eaten, text

