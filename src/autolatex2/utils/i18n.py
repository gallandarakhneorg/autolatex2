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

import gettext
import os

class Translation:
    """
    Global translation support for the application
    """

    def __init__(self, domain : str, locale_folder : str):
        """
        Construct a Translation object.
        :param domain: the name of the localized domain.
        :type domain: str
        :param locale_folder: Simple name of the folder that must contain localized tets.
        :type: Simple
        """
        root_folder = os.path.dirname(os.path.dirname(__file__))
        self.locale_dir : str = os.path.normpath(os.path.join(root_folder, locale_folder))
        self.domain : str = domain
        self._setup()

    def _setup(self):
        """
        Initialize the translation biding.
        """
        gettext.bindtextdomain(self.domain, str(self.locale_dir))
        gettext.textdomain(self.domain)
        gettext.install(self.domain)

    # noinspection PyMethodMayBeStatic
    def get_text(self, message: str) -> str:
        """
        Replies the localized message corresponding to the input message.
        If the localized message is not defined, the original message is replied.
        :param message: the message to translate.
        :type message: str
        :return: the translation result.
        :rtype: str
        """
        return gettext.gettext(message)

    # noinspection PyMethodMayBeStatic
    def get_text_n(self, singular: str, plural: str, n: int) -> str:
        """
        Replies the localized message corresponding to one of the input messages depending
        on the quantity of elements.
        If the localized message is not defined, the original message is replied.
        :param singular: the message to translate if there is zero or one element.
        :type singular: str
        :param plural: the message to translate if there is two or more elements.
        :type plural: str
        :param n: the quantity of elements
        :type n: int
        :return: the translation result.
        :rtype: str
        """
        return gettext.ngettext(singular, plural, 1 if n < 1 else n)

gettext.install('myapp')  # Installs _() globally

tr = Translation('autolatex', 'locales')
T = tr.get_text
TT = tr.get_text_n