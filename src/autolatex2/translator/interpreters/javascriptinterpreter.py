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
JavaScript implementation of an interpreter for the translators.
"""

import pprint
import shutil
from typing import override, Any

from autolatex2.translator.interpreters.abstractinterpreter import AbstractTranslatorInterpreter
from autolatex2.config.configobj import Config
from autolatex2.utils.runner import ScriptOutput


class TranslatorInterpreter(AbstractTranslatorInterpreter):
	"""
	Definition of a JavaScript implementation of an interpreter for the translators.
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
		return shutil.which('js') is not None

	
	@property
	@override
	def interpreter(self) -> str:
		"""
		Replies the name of the interpreter.
		:return: The name of the interpreter.
		:rtype: str
		"""
		return 'javascript'


	def to_javascript(self, value : Any) -> str:
		"""
		Convert a value to JavaScript code.
		:param value: The value to convert.
		:type value: Any
		:return: The JavaScript expression for the value.
		:rtype: str
		"""
		if isinstance(value, list) or isinstance(value, set):
			plist = list()
			for e in value:
				plist.append(self.to_javascript(e))
			pvalue = ', '.join(plist)
			return "[" + pvalue + "]"
		elif isinstance(value, dict):
			raise RuntimeError("dictionary not supported")
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
	def run(self, code : str) -> ScriptOutput:
		"""
		Run the interpreter.
		:param code: The JavaScript code to interprete.
		:type code: str
		:return: An output containing the standard output, the
				 error output, the exception, the return code.
		:rtype: InterpreterOutput
		"""
		full_code = ""
		for name, value in self.global_variables.items():
			value = self.filter_variable_name(value)
			pvalue = self.to_javascript(value)
			full_code += "var %s = %s\n" % (name, pvalue)
		full_code += "\n\n\n"+ code
		return self.run_script(full_code, 'js')


