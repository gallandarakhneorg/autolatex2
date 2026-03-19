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

import logging
import unittest
from typing import override

from autolatex2.cli.abstract_main import AbstractAutoLaTeXMain
from autolatex2.cli.autolatexcommands import AutolatexCommand
from autolatex2.cli.exiters import AutoLaTeXExceptionExiter
from autolatex2tests.cli.commands.abstract_command_test import AbstractCommandTest


class TestShowInstalledTranslatorsAction(AbstractCommandTest):

	def __init__(self, x):
		super().__init__(x, 'showinstalledtranslators')


	def test_w_level(self):
		self.do_test('--level')


	def test_wo_level(self):
		self.do_test('--nolevel')


if __name__ == '__main__':
	unittest.main()

