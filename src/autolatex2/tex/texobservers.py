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
import abc
from typing import override, Any

from autolatex2.tex.parser import Parser

import gettext
_T = gettext.gettext

class Observer(abc.ABC):
	"""
	Interface for observer on events in the TeX parser.
	"""
	__metaclass__ = abc.ABCMeta

	@abc.abstractmethod
	def text(self, parser : Parser, text : str):
		"""
		Invoked when characters were found and must be output.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: the text to filter.
		:type text: str
		"""
		raise NotImplementedError

	@abc.abstractmethod
	def comment(self, parser : Parser, raw : str, comment : str) -> str | None:
		"""
		Invoked when comments were found and must be output.
		:param parser: reference to the parser.
		:type parser: Parser
		:param raw: Raw text of the comment to filter.
		:type raw: str
		:param comment: the comment to filter.
		:type comment: str
		:return: The text to reinject and to pass to the 'text' callback
		:rtype: str | None
		"""
		raise NotImplementedError

	@abc.abstractmethod
	def open_block(self, parser : Parser, text : str) -> str | None:
		"""
		Invoked when a block is opened.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: The text used for opening the block.
		:type text: str
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str | None
		"""
		raise NotImplementedError

	@abc.abstractmethod
	def close_block(self, parser : Parser, text : str) -> str | None:
		"""
		Invoked when a block is closed.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: The text used for opening the block.
		:type text: str
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str | None
		"""
		raise NotImplementedError

	@abc.abstractmethod
	def open_math(self, parser : Parser, inline : bool) -> str | None:
		"""
		Invoked when a math environment is opened.
		:param parser: reference to the parser.
		:type parser: Parser
		:param inline: Indicates if the math environment is inline or not.
		:type inline: bool
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str | None
		"""
		raise NotImplementedError

	@abc.abstractmethod
	def close_math(self, parser : Parser, inline : bool) -> str | None:
		"""
		Invoked when a math environment is closed.
		:param parser: reference to the parser.
		:type parser: Parser
		:param inline: Indicates if the math environment is inline or not.
		:type inline: bool
		:return: the text that must replace the block opening in the output, or
		         None if no replacement is needed.
		:rtype: str | None
		"""
		raise NotImplementedError

	@abc.abstractmethod
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
		:rtype: str | None
		"""
		raise NotImplementedError

	@abc.abstractmethod
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
		:type parameter: dict[str,str]
		:return: the result of the expand of the macro, or None to not replace the macro by something (the macro is used as-is)
		:rtype: str
		"""
		raise NotImplementedError




class ReinjectObserver(Observer):
	"""
	Observer on events in the TeX parser that is putting back the detected text into the given content.
	"""

	def __init__(self):
		self.__content = ''

	@property
	def content(self):
		"""
		Replies the content of the TeX file.
		"""
		return self.__content

	@override
	def text(self, parser : Parser, text : str):
		"""
		Invoked when characters were found and must be output.
		:param parser: reference to the parser.
		:type parser: Parser
		:param text: the text to filter.
		:type text: str
		"""
		t = str(text)
		if t:
			self.__content += t

	@override
	def comment(self, parser : Parser, raw : str, comment : str) -> str:
		"""
		Invoked when comments were found and must be output.
		:param parser: reference to the parser.
		:type parser: Parser
		:param raw: Raw text of the comment to filter.
		:type raw: str
		:param comment: the comment to filter.
		:type comment: str
		:return: The text to reinject and to pass to the 'text' callback
		:rtype: str
		"""
		return "%" + re.sub('[\n\r]',  ' ',  str(comment)) + "\n"

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
		return text

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
		return text

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
		if inline:
			return '$'
		else:
			return '\\['

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
		if inline:
			return '$'
		else:
			return '\\]'

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
		:return: the result of the expand of the macro, or None to not replace the macro by something (the macro is used as-is)
		:rtype: str
		"""
		return raw_text

	@override
	def find_macro(self, parser: Parser, name: str, special: bool, math: bool) -> str | None:
		return None
