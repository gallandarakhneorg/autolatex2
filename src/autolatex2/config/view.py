#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 1998-2021 Stephane Galland <galland@arakhne.org>
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
Configuration for the viewer.
"""

import autolatex2.utils.utilfunctions as genutils

class ViewerConfig:
	"""
	Configuration of a AutoLaTeX instance.
	"""

	def __init__(self):
		self.__view_enable : bool = False
		self.__viewer_cli : list[str] = list()
		self.__async_view_enable : bool = False

	def reset_internal_attributes(self):
		"""
		Reset the internal attributes.
		"""
		self.__view_enable = False
		self.__viewer_cli = list()
		self.__async_view_enable = False

	@property
	def view(self) -> bool:
		"""
		Replies if the viewer is enabled.
		:return: True if the viewer is enabled.
		:rtype: bool
		"""
		return self.__view_enable

	@view.setter
	def view(self,  enable : bool):
		"""
		Change if the viewer is enabled.
		:param enable: True if the viewer is enabled.
		:type enable: bool
		"""
		self.__view_enable = enable

	@property
	def async_view(self) -> bool:
		"""
		Replies if the asynchronous view is enabled.
		:return: True if the async view is enabled.
		:rtype: bool
		"""
		return self.__async_view_enable

	@async_view.setter
	def async_view(self, enable : bool):
		"""
		Change if the asynchronous view is enabled.
		:param enable: True if the async view is enabled.
		:type enable: bool
		"""
		self.__async_view_enable = enable

	@property
	def viewer_cli(self) -> list[str]:
		"""
		Replies the command-line for the viewer.
		:rtype: list[str]
		"""
		return self.__viewer_cli

	@viewer_cli.setter
	def viewer_cli(self, cli : list[str] | str | None):
		"""
		Set the command-line for the viewer.
		:type cli: list[str] | str | None
		"""
		if cli is None:
			self.__viewer_cli = list()
		elif isinstance(cli, list):
			self.__viewer_cli = cli
		else:
			self.__viewer_cli = genutils.parse_cli(cli)

