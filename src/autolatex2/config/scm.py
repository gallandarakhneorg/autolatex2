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
Configuration for the SCM.
"""

import autolatex2.utils.utilfunctions as genutils

class ScmConfig:
	"""
	Configuration of a AutoLaTeX instance.
	"""

	def __init__(self):
		self.__commit_cli = list()
		self.__update_cli = list()

	def reset_internal_attributes(self):
		"""
		Reset the internal attributes.
		"""
		self.__commit_cli = list()
		self.__update_cli = list()

	@property
	def commit_cli(self) -> list[str]:
		"""
		Replies the command-line for commiting to the SCM system.
		:return: The CLI
		:rtype: list
		"""
		return self.__commit_cli

	@commit_cli.setter
	def commit_cli(self, cli : list[str] | str | None):
		"""
		Change the command-line for commiting to the SCM system.
		:return: The CLI
		:rtype: list or str
		"""
		if cli is None:
			self.__commit_cli = list()
		elif isinstance(cli,  list):
			self.__commit_cli = cli
		else:
			self.__commit_cli = genutils.parse_cli(cli)

	@property
	def update_cli(self) -> list[str]:
		"""
		Replies the command-line for updating the current folder from the SCM system.
		:return: The CLI
		:rtype: list
		"""
		return self.__update_cli

	@update_cli.setter
	def update_cli(self, cli : list[str] | str | None):
		"""
		Change the command-line for updating the current folder from the SCM system.
		:return: The CLI
		:rtype: list or str
		"""
		if cli is None:
			self.__update_cli = list()
		elif isinstance(cli,  list):
			self.__update_cli = cli
		else:
			self.__update_cli = genutils.parse_cli(cli)
