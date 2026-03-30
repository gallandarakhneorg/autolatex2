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
Configuration for the logging system.
"""

from autolatex2.utils.extlogging import LogLevel
from autolatex2.utils.i18n import T

class LoggingConfig:
	"""
	Configuration of a AutoLaTeX instance.
	"""

	DEFAULT_LEVEL : int = LogLevel.INFO
	DEFAULT_LOG_MESSAGE : str = T('%(levelname)s: %(message)s')

	def __init__(self):
		self.__message : str = ''
		self.__level : LoggingConfig = LoggingConfig.DEFAULT_LEVEL

	def reset_internal_attributes(self):
		"""
		Reset the internal attributes.
		"""
		self.__message = ''
		self.__level = LoggingConfig.DEFAULT_LEVEL

	@property
	def message(self) -> str:
		"""
		Replies the template for the logging message.
		:return: the template.
		:rtype: str
		"""
		return self.__message

	@message.setter
	def message(self,  template : str):
		"""
		Change the template for the logging message.
		:param template: the template.
		:type template: str
		"""
		self.__message = template

	@property
	def level(self) -> int :
		"""
		Replies the logging level.
		:return: the level.
		:rtype: int
		"""
		return self.__level

	@level.setter
	def level(self,  level : int):
		"""
		Change the logging level.
		:param level: the level.
		:type level: int
		"""
		if level:
			self.__level = level
		else:
			self.__level = LoggingConfig.DEFAULT_LEVEL
			
