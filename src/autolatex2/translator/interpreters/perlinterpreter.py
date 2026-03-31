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
Perl implementation of an interpreter for the translators.
"""

import io
import pprint
import shutil
from typing import override, Any

from autolatex2.translator.interpreters.abstractinterpreter import AbstractTranslatorInterpreter
from autolatex2.config.configobj import Config
from autolatex2.utils.runner import ScriptOutput


class TranslatorInterpreter(AbstractTranslatorInterpreter):
	"""
	Definition of a Perl implementation of an interpreter for the translators.
	"""

	def __init__(self,  configuration : Config):
		"""
		Construct a translator interpreter.
		:param configuration: The general configuration.
		:type configuration: Config
		"""
		super().__init__(configuration)

	# noinspection PyDeprecation
	@property
	@override
	def runnable(self) -> bool:
		"""
		Replies if the interpreter is runnable, i.e., the underground interpreter can be run.
		:return: True if the interpreter could be run.
		:rtype: bool
		"""
		return shutil.which('perl') is not None

	
	@property
	@override
	def interpreter(self) -> str:
		"""
		Replies the name of the interpreter.
		:return: The name of the interpreter.
		:rtype: str
		"""
		return 'perl'


	def to_perl(self, value : Any, inline : bool = True) -> str | None:
		"""
		Convert a value to Perl code.
		:param value: The value to convert.
		:type value: Any
		:param inline: Indicates if th perl in inlined (default: True).
		:param inline: bool
		:return: The Perl expression for the value.
		:rtype: str
		"""
		if value is None:
			return 'undef'
		elif isinstance(value, list):
			plist = list()
			for e in value:
				plist.append(self.to_perl(e, False))
			pvalue = ', '.join(plist)
			if inline:
				return "(" + pvalue + ")"
			else:
				return "[" + pvalue + "]"
		elif isinstance(value, set):
			plist = list()
			for e in value:
				plist.append(
					"%s => 1" % self.to_perl(e, False))
			pvalue = ', '.join(plist)
			if inline:
				return "(" + pvalue + ")"
			else:
				return "[" + pvalue + "]"
		elif isinstance(value, dict):
			plist = list()
			for e in value:
				plist.append(
					"%s => %s" % (e, self.to_perl(value[e], False)))
			pvalue = ', '.join(plist)
			if inline:
				return "(" + pvalue + ")"
			else:
				return "[" + pvalue + "]"
		elif isinstance(value,(str,int,float,bool)):
			pp = pprint.PrettyPrinter()
			v = pp.pformat(value)
			return str(v)
		else:
			return None

	# noinspection PyMethodMayBeStatic
	def get_perl_prefix(self, value : Any) -> str:
		"""
		Replies the perl variable prefix for the given value.
		:param value: The value to get the type for.
		:type value: Any
		:return: The perl variable prefix.
		:rtype: str
		"""
		if isinstance(value, list):
			return '@'
		elif isinstance(value, set) or isinstance(value, dict):
			return '%'
		elif isinstance(value, io.IOBase):
			return '*'
		else:
			return '$'

	@override
	def filter_variable_name(self, name : str) -> str:
		"""
		Filter the name of the variable.
		:param name: The name to filter.
		:type name: str
		:return: The filtering result, that must be a valid name in the translator's language.
		:rtype: str
		"""
		return name

	@override
	def run(self, code : str) -> ScriptOutput:
		"""
		Run the interpreter.
		:param code: The Perl code to interpret.
		:type code: str
		:return: A quadruplet containing the standard output, the
				 error output, the exception, the return code.
		:rtype: tuple[str,str,Any,int]
		"""
		full_code = "#!/usr/bin/env perl\n"
		for name in self.global_variables:
			value = self.global_variables[name]
			prefix = self.get_perl_prefix(value)
			pvalue = self.to_perl(value)
			if pvalue is not None:
				full_code += ("my %s%s = %s;\n" % (prefix, self.filter_variable_name(name), pvalue))
		full_code += "\n\n\n"+ code
		return self.run_script(full_code, 'perl')


