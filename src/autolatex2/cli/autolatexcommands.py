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
Generic implementation of an AutoLaTeX command.
"""

from typing import Type

from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.utils.extlogging import ensure_autolatex_logging_levels


class AutolatexCommand:
    """
	Command to be run that is launched by the user of AutoLaTeX.
	"""
    def __init__(self, name: str, action_type: Type[AbstractMakerAction], help_text: str, aliases: list[str] | None, prerequisites : list[str] | None):
        """
		Constructor.
		:param name: The name of the command.
		:type name: str
		:param action_type: The type of action.
		:type action_type: Type[AbstractMakerAction]
		:param help_text: The help text.
		:type help_text: str
		:param aliases: The aliases for the command name.
		:type aliases: list[str] | None
		:param prerequisites: The list of names of the commands that must be run before this command.
		:type prerequisites: list[str] | None
		"""
        ensure_autolatex_logging_levels()
        self.__name = name
        self.__creator_type = action_type
        self.__help = help_text
        self.__instance = None
        if aliases is None:
            self.__aliases = list()
        else:
            self.__aliases = list(aliases)
        if prerequisites is None:
            self.__prerequisites = list()
        else:
            self.__prerequisites = list(prerequisites)

    @property
    def instance(self) -> AbstractMakerAction:
        """"
        Replies the concrete instance of the command implementation.
        :rtype: AbstractMakerAction
        """
        if self.__instance is None:
            self.__instance = self.creator_type()
        return self.__instance

    @property
    def name(self) -> str:
        """"
        Replies the name of the command.
        :rtype: str
        """
        return self.__name

    @property
    def creator_type(self) -> Type[AbstractMakerAction]:
        """"
        Replies the type of the command instance.
        :rtype: Type[AbstractMakerAction]
        """
        return self.__creator_type

    @property
    def help(self) -> str:
        """"
        Replies the helping text for the command.
        :rtype: str
        """
        return self.__help

    @property
    def aliases(self) -> list[str]:
        """"
        Replies the alias names for the command.
        :rtype: list[str]
        """
        return self.__aliases

    @property
    def prerequisites(self) -> list[str]:
        """"
        Replies the names of the commands that must be executed before this command
        :rtype: list[str]
        """
        return self.__prerequisites
