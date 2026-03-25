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
Abstract implementation of an interpreter for the AutoLaTeX translators.
"""

import pprint
import abc
from typing import Any

from autolatex2.utils.runner import Runner
from autolatex2.config.configobj import Config

class AbstractTranslatorInterpreter(Runner):
	"""
	Definition of an abstract implementation of an interpreter for the AutoLaTeX translators.
	"""

	def __init__(self,  configuration : Config):
		"""
		Construct a translator interpreter.
		:param configuration: The general configuration.
		:type configuration: Config
		"""
		self.__global_variables = dict()
		self.__parent = None
		self.__configuration = configuration

	@property
	def configuration(self) -> Config:
		"""
		Replies the configuration.
		:return: The configuration.
		:rtype: Config
		"""
		return self.__configuration

	@configuration.setter
	def configuration(self, c : Config):
		"""
		Change the configuration.
		:param c: The configuration.
		:type c: Config
		"""
		self.__configuration = c

	@property
	def parent(self) -> Any:
		"""
		Replies the parent interpreter.
		:return: The parent interpreter.
		:rtype: AbstractTranslatorInterpreter
		"""
		return self.__parent

	@parent.setter
	def parent(self, p : Any):
		"""
		Change the parent interpreter.
		:param p: The parent interpreter, or None for unset it.
		:type p: AbstractTranslatorInterpreter
		"""
		self.__parent = p

	@property
	def global_variables(self) -> dict[str,str]:
		"""
		Replies all the global variables.
		:return: the map of the global variables in which the keys are the variable names.
		:rtype: map
		"""
		return self.__global_variables

	@property
	def runnable(self) -> bool:
		"""
		Replies if the interpreter is runnable, i.e., the underground interpreter can be run.
		:return: True if the interpreter could be run.
		:rtype: bool
		"""
		raise NotImplementedError

	@property
	def interpreter(self) -> str:
		"""
		Replies the name of the interpreter.
		:return: The name of the interpreter.
		:rtype: str
		"""
		raise NotImplementedError

	@abc.abstractmethod
	def run(self, code : str):
		"""
		Run the interpreter.
		:param code: The Python code to interprete.
		:type code: str
		"""
		raise NotImplementedError

	@abc.abstractmethod
	def filter_variable_name(self, name : str) -> str:
		"""
		Filter the name of the variable.
		:param name: The name to filter.
		:type name: str
		:return: The filtering result, that must be a valid name in the translator's language.
		:rtype: str
		"""
		raise NotImplementedError

	# noinspection PyMethodMayBeStatic
	def to_python(self, value : Any) -> str:
		"""
		Convert a value to a valid Python code.
		:param value: The value to convert.
		:type value: Any
		:return: Python code.
		:rtype: str
		"""
		pp = pprint.PrettyPrinter(indent=2)
		v = pp.pformat(value)
		return v


