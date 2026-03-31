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

import unittest
import logging
import os
from abc import ABC
from typing import override

from autolatex2.config.configobj import Config
from autolatex2.config.generation import GenerationConfig
from autolatex2.config.translator import TranslatorConfig
from autolatex2.config.view import ViewerConfig
from autolatex2.config.scm import ScmConfig
from autolatex2.config.clean import CleanConfig
from autolatex2.config.logging import LoggingConfig
from autolatex2tests.abstract_base_test import AbstractBaseTest


class ConfigMock(Config):
	def __init__(self, config : Config, *, isdir : bool):
		super().__init__()
		self.__isDir = isdir
		self.reset_internal_attributes(config.os_name)
		self.home_directory = config.home_directory

	@override
	def _isdir(self, directory : str) -> bool:
		return self.__isDir


class AbstractTestConfig(AbstractBaseTest,ABC):

	@property
	def expectedAutoLaTeXVersion(self) -> str:
		return "50.0"


class TestPosixConfig(AbstractTestConfig):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = None
		self.__dirname = None

	@override
	def setUp(self):
		super().setUp()
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__dirname = os.path.dirname(os.path.realpath(__file__))
		self.__config = Config()
		self.__config.os_name = 'posix'
		self.__config.home_directory = os.path.join('', 'home')

	@property
	def config(self) -> Config:
		return self.__config

	@property
	def dirname(self) -> str:
		return self.__dirname



	def test_make_document_config_filename(self):
		filename = self.config.make_document_config_filename(self.dirname)
		self.assertEqual(os.path.join(self.dirname, '.autolatex_project.cfg'), filename)



	def test_user_config_directory(self):
		name = self.config.user_config_directory
		self.assertEqual(os.path.join('home', '.autolatex'), name)



	def test_user_config_file_directory(self):
		self.__config = ConfigMock(self.__config, isdir = True)
		name = self.config.user_config_file
		self.assertEqual(os.path.join('home', '.autolatex', 'autolatex.conf'), name)

	def test_user_config_file_noDirectory(self):
		self.__config = ConfigMock(self.__config, isdir = False)
		name = self.config.user_config_file
		self.assertEqual(os.path.join('home', '.autolatex'), name)



	def test_document_directory_getter(self):
		directory = self.config.document_directory
		self.assertFalse(directory)

	def test_document_directory_setter(self):
		pass



	def test_installation_directory(self):
		directory = self.config.installation_directory
		expected = os.path.normpath(os.path.join(os.path.dirname(__file__),  '..',  '..',  '..', 'src',  'autolatex2'))
		self.assertEqual(expected, directory)



	def test_name_getter(self):
		self.assertFalse(self.config.name)

	def test_name_setter(self):
		self.config.name = "myname"
		self.assertEqual("myname", self.config.name)



	def test_launch_name_getter(self):
		self.assertFalse(self.config.launch_name)

	def test_launch_name_setter(self):
		self.config.launch_name = "myname"
		self.assertEqual("myname", self.config.launch_name)



	def test_version(self):
		version = self.config.version
		self.assertEqual(self.expectedAutoLaTeXVersion, version)



	def test_generation_getter(self):
		self.assertIsNotNone(self.config.generation)

	def test_generation_setter(self):
		g = GenerationConfig()
		self.config.generation = g
		self.assertEqual(g, self.config.generation)



	def test_translators_getter(self):
		self.assertIsNotNone(self.config.translators)

	def test_translators_setter(self):
		g = TranslatorConfig()
		self.config.translators = g
		self.assertEqual(g, self.config.translators)



	def test_view_getter(self):
		self.assertIsNotNone(self.config.view)

	def test_view_setter(self):
		g = ViewerConfig()
		self.config.view = g
		self.assertEqual(g, self.config.view)



	def test_logging_getter(self):
		self.assertIsNotNone(self.config.logging)

	def test_logging_setter(self):
		g = LoggingConfig()
		self.config.logging = g
		self.assertEqual(g, self.config.logging)


	def test_scm_getter(self):
		self.assertIsNotNone(self.config.scm)

	def test_scm_setter(self):
		g = ScmConfig()
		self.config.scm = g
		self.assertEqual(g, self.config.scm)


	def test_clean_getter(self):
		self.assertIsNotNone(self.config.clean)

	def test_clean_setter(self):
		g = CleanConfig()
		self.config.clean = g
		self.assertEqual(g, self.config.clean)


class TestNtConfig(AbstractTestConfig):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = None
		self.__dirname = None

	@override
	def setUp(self):
		super().setUp()
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__dirname = os.path.dirname(os.path.realpath(__file__))
		self.__config = Config()
		self.__config.os_name = 'nt'
		self.__config.home_directory = os.path.join('C:', 'home')

	@property
	def config(self) -> Config:
		return self.__config

	@property
	def dirname(self) -> str:
		return self.__dirname




	def test_make_document_config_filename(self):
		filename = self.config.make_document_config_filename(self.dirname)
		self.assertEqual(os.path.join(self.dirname, 'autolatex_project.cfg'), filename)



	def test_user_config_directory(self):
		name = self.config.user_config_directory
		self.assertEqual(os.path.join('C:', 'home', 'Local Settings', 'Application Data', 'autolatex'), name)



	def test_user_config_file_directory(self):
		self.__config = ConfigMock(self.__config, isdir = True)
		name = self.config.user_config_file
		self.assertEqual(os.path.join('C:', 'home', 'Local Settings', 'Application Data', 'autolatex', 'autolatex.conf'), name)

	def test_user_config_file_noDirectory(self):
		self.__config = ConfigMock(self.__config, isdir = False)
		name = self.config.user_config_file
		self.assertEqual(os.path.join('C:', 'home', 'Local Settings', 'Application Data', 'autolatex.conf'), name)



	def test_document_directory_getter(self):
		directory = self.config.document_directory
		self.assertFalse(directory)

	def test_document_directory_setter(self):
		pass



	def test_document_filename_getter(self):
		name = self.config.document_filename
		self.assertFalse(name)

	def test_document_filename_setter(self):
		pass



	def test_installation_directory(self):
		directory = self.config.installation_directory
		expected = os.path.normpath(os.path.join(os.path.dirname(__file__),  '..',  '..', '..', 'src', 'autolatex2'))
		self.assertEqual(expected, directory)



	def test_name_getter(self):
		self.assertFalse(self.config.name)

	def test_name_setter(self):
		self.config.name = "myname"
		self.assertEqual("myname", self.config.name)



	def test_launch_name_getter(self):
		self.assertFalse(self.config.launch_name)

	def test_launch_name_setter(self):
		self.config.launch_name = "myname"
		self.assertEqual("myname", self.config.launch_name)



	def test_version(self):
		version = self.config.version
		self.assertEqual(self.expectedAutoLaTeXVersion, version)



	def test_generation_getter(self):
		self.assertIsNotNone(self.config.generation)

	def test_generation_setter(self):
		g = GenerationConfig()
		self.config.generation = g
		self.assertEqual(g, self.config.generation)



	def test_translators_getter(self):
		self.assertIsNotNone(self.config.translators)

	def test_translators_setter(self):
		g = TranslatorConfig()
		self.config.translators = g
		self.assertEqual(g, self.config.translators)





	def test_view_getter(self):
		self.assertIsNotNone(self.config.view)

	def test_view_setter(self):
		g = ViewerConfig()
		self.config.view = g
		self.assertEqual(g, self.config.view)



	def test_logging_getter(self):
		self.assertIsNotNone(self.config.logging)

	def test_logging_setter(self):
		g = LoggingConfig()
		self.config.logging = g
		self.assertEqual(g, self.config.logging)


	def test_scm_getter(self):
		self.assertIsNotNone(self.config.scm)

	def test_scm_setter(self):
		g = ScmConfig()
		self.config.scm = g
		self.assertEqual(g, self.config.scm)


	def test_clean_getter(self):
		self.assertIsNotNone(self.config.clean)

	def test_clean_setter(self):
		g = CleanConfig()
		self.config.clean = g
		self.assertEqual(g, self.config.clean)


class TestOtherConfig(AbstractTestConfig):

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.__config = None
		self.__dirname = None

	@override
	def setUp(self):
		super().setUp()
		logging.getLogger().setLevel(logging.CRITICAL)
		self.__dirname = os.path.dirname(os.path.realpath(__file__))
		self.__config = Config()
		self.__config.os_name = 'otheros'
		self.__config.home_directory = 'home'

	@property
	def config(self) -> Config:
		return self.__config

	@property
	def dirname(self) -> str:
		return self.__dirname




	def test_make_document_config_filename(self):
		filename = self.config.make_document_config_filename(self.dirname)
		self.assertEqual(os.path.join(self.dirname, 'autolatex_project.cfg'), filename)



	def test_user_config_directory(self):
		name = self.config.user_config_directory
		self.assertEqual(os.path.join('home', 'autolatex'), name)



	def test_user_config_file_directory(self):
		self.__config = ConfigMock(self.__config, isdir = True)
		name = self.config.user_config_file
		self.assertEqual(os.path.join('home', 'autolatex', 'autolatex.conf'), name)

	def test_user_config_file_noDirectory(self):
		self.__config = ConfigMock(self.__config, isdir = False)
		name = self.config.user_config_file
		self.assertEqual(os.path.join('home', 'autolatex.conf'), name)



	def test_document_directory_getter(self):
		directory = self.config.document_directory
		self.assertFalse(directory)

	def test_document_directory_setter(self):
		pass



	def test_installation_directory(self):
		directory = self.config.installation_directory
		expected = os.path.normpath(os.path.join(os.path.dirname(__file__),  '..',  '..',  '..',  'src', 'autolatex2'))
		self.assertEqual(expected, directory)



	def test_name_getter(self):
		self.assertFalse(self.config.name)

	def test_name_setter(self):
		self.config.name = "myname"
		self.assertEqual("myname", self.config.name)



	def test_launch_name_getter(self):
		self.assertFalse(self.config.launch_name)

	def test_launch_name_setter(self):
		self.config.launch_name = "myname"
		self.assertEqual("myname", self.config.launch_name)



	def test_version(self):
		version = self.config.version
		self.assertEqual(self.expectedAutoLaTeXVersion, version)



	def test_generation_getter(self):
		self.assertIsNotNone(self.config.generation)

	def test_generation_setter(self):
		g = GenerationConfig()
		self.config.generation = g
		self.assertEqual(g, self.config.generation)



	def test_translators_getter(self):
		self.assertIsNotNone(self.config.translators)

	def test_translators_setter(self):
		g = TranslatorConfig()
		self.config.translators = g
		self.assertEqual(g, self.config.translators)




	def test_view_getter(self):
		self.assertIsNotNone(self.config.view)

	def test_view_setter(self):
		g = ViewerConfig()
		self.config.view = g
		self.assertEqual(g, self.config.view)



	def test_logging_getter(self):
		self.assertIsNotNone(self.config.logging)

	def test_logging_setter(self):
		g = LoggingConfig()
		self.config.logging = g
		self.assertEqual(g, self.config.logging)


	def test_scm_getter(self):
		self.assertIsNotNone(self.config.scm)

	def test_scm_setter(self):
		g = ScmConfig()
		self.config.scm = g
		self.assertEqual(g, self.config.scm)


	def test_clean_getter(self):
		self.assertIsNotNone(self.config.clean)

	def test_clean_setter(self):
		g = CleanConfig()
		self.config.clean = g
		self.assertEqual(g, self.config.clean)





if __name__ == '__main__':
	unittest.main()

