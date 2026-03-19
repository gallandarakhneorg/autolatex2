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
Ruby implementation of an interpreter for the AutoLaTeX translators.
"""

import pprint
import shutil
from typing import override, Any

from autolatex2.translator.interpreters.abstractinterpreter import AbstractTranslatorInterpreter
from autolatex2.config.configobj import Config

import gettext
_T = gettext.gettext

class TranslatorInterpreter(AbstractTranslatorInterpreter):
	"""
	Definition of a Ruby implementation of an interpreter for the AutoLaTeX translators.
	"""

	def __init__(self,  configuration : Config):
		"""
		Construct an translator interpreter.
		:param configuration: The general configuration.
		:type configuration: Config
		"""
		super().__init__(configuration)

	@property
	@override
	def runnable(self) -> bool:
		"""
		Replies if the interpreter is runnable, ie. the underground interpreter can be run.
		:return: True if the interpreter could be run.
		:rtype: bool
		"""
		return shutil.which('ruby') is not None

	
	@property
	@override
	def interpreter(self) -> str:
		"""
		Replies the name of the interpreter.
		:return: The name of the interpreter.
		:rtype: str
		"""
		return 'ruby'


	def to_ruby(self, value : Any) -> str:
		"""
		Convert a value to Ruby code.
		:param value: The value to convert.
		:type value: Any
		:return: The Ruby expression for the value.
		:rtype: str
		"""
		if isinstance(value, list) or isinstance(value, set):
			plist = list()
			for e in value:
				plist.append(self.to_ruby(e))
			pvalue = ', '.join(plist)
			return "[" + pvalue + "]"
		elif isinstance(value, dict):
			plist = list()
			for e in value:
				plist.append(
					"%s => %s" % (e, self.to_ruby(value[e])))
			pvalue = ', '.join(plist)
			return "{" + pvalue + "}"
		else:
			pp = pprint.PrettyPrinter()
			v = pp.pformat(value)
			return str(v)

	@override
	def filter_variable_name(self, name : str) -> str:
		"""
		Filter the name of the variable.
		:param name: The name to filter.
		:type name: str
		:return: The filtering result, that must be a valid name in the translator's language.
		:rtype: str
		"""
		return "_%s" % name

	@override
	def run(self, code : str) -> tuple[str,str,Any,int]:
		"""
		Run the interpreter.
		:param code: The Perl code to interpreter.
		:type code: str
		:return: A quadruplet containing the standard output, the
				 error output, the exception, the return code.
		:rtype: tuple[str,str,Any,int]
		"""
		full_code = "#!/usr/bin/env ruby\n"
		for name in self.global_variables:
			value = self.global_variables[name]
			pvalue = self.to_ruby(value)
			full_code += ("%s = %s\n" % (self.filter_variable_name(name), pvalue))
		full_code += "\n\n\n"+ code
		return self.run_script(full_code, 'ruby')


