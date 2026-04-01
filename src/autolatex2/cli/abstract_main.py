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
Abstract implementation for main program.
"""

import textwrap
from abc import ABC, abstractmethod
import argparse
from collections import defaultdict, deque
import logging
import os
import platform
import sys
from argparse import Namespace
from typing import Any, override

import autolatex2.cli.exiters as exiters
from autolatex2.cli.autolatexcommands import AutolatexCommand
from autolatex2.config.configobj import Config
from autolatex2.config.configreader import OldStyleConfigReader
from autolatex2.translator.translatorobj import TranslatorLevel
from autolatex2.utils.extlogging import LogLevel, DynamicLogLevelFormatter
import autolatex2.utils.extprint as eprintpkg
import autolatex2.utils.utilfunctions as genutils
from autolatex2.utils.i18n import T


class AbstractAutoLaTeXMain(ABC):
	"""
	Abstract implementation for a main program.
	"""

	def __init__(self,  read_system_config : bool = True,  read_user_config : bool = True,
				 args : list[str] | None = None,  exiter : exiters.AutoLaTeXExiter | None = None):
		"""
		Constructor.
		:param read_system_config: Indicates if the system-level configuration must be read. Default is True.
		:type read_system_config: bool
		:param read_user_config: Indicates if the user-level configuration must be read. Default is True.
		:type read_user_config: bool
		:param args: List of command line arguments. If it is None, the system args are used.
		:type args: list
		:param exiter: The instance of the object that is called when the program should stop.
		:type exiter: exiters.AutoLaTeXExiter | None
		"""
		self.__initial_argv = args
		self.__read_document_configuration = True
		if exiter:
			self.__exiter : exiters.AutoLaTeXExiter = exiter
		else:
			self.__exiter : exiters.AutoLaTeXExiter = exiters.AutoLaTeXSysExitExiter()

		# Create the AutoLaTeX configuration object
		self.__configuration = Config()

		# Initialization of the logging system (must be after configuration creation)
		self.__logging_handler = None
		self._init_logging_system()
		
		# Initialization that depends on the script itself
		script_launch_name = os.path.basename(sys.argv[0])
		script_path,  script_ext = os.path.splitext(sys.argv[0])
		script_name = os.path.basename(script_path)
		self.__configuration.name = script_name
		self.__configuration.launch_name = script_launch_name

		# Read the configuration from the system
		config_reader = OldStyleConfigReader()
		if read_system_config:
			config_reader.read_system_config_safely(self.__configuration)

		# Read the configuration from the user home
		if read_user_config:
			config_reader.read_user_config_safely(self.__configuration)
		
		# Create the CLI parser
		self._cli_parser = self._create_cli_parser(name = self.__configuration.name, version = self.__configuration.version,  epilog = self._build_help_epilog())

	@property
	def configuration(self) -> Config:
		"""
		Replies the global configuration of the program.
		:rtype: Config
		"""
		return self.__configuration

	@configuration.setter
	def configuration(self, config : Config):
		"""
		Change the global configuration of AutoLaTeX.
		:type config: Config
		"""
		self.__configuration = config

	@property
	def cli_parser(self) -> argparse.ArgumentParser:
		"""
		Replies the CLI parser.
		:rtype: argparse.ArgumentParser
		"""
		return self._cli_parser

	@property
	def exiter(self) -> exiters.AutoLaTeXExiter:
		"""
		Replies the component for stopping the autolatex main program.
		:rtype: exiters.AutoLaTeXExiter
		"""
		return self.__exiter

	@exiter.setter
	def exiter(self, exiter : exiters.AutoLaTeXExiter):
		"""
		Change the component for stopping the autolatex main program.
		:type exiter: exiters.AutoLaTeXExiter
		"""
		if exiter:
			self.__exiter = exiter
		else:
			self.__exiter = exiters.AutoLaTeXSysExitExiter()

	def show_configuration(self):
		"""
		Show up the configuration of the program.
		"""
		eprintpkg.epprint(self.configuration)

	def _detect_autolatex_configuration_file(self,  directory : str | None) -> str | None:
		"""
		Search for a configuration file in the given directory or one of its parent directories.
		:param directory: The start of the search.
		:type directory: str
		:return: the path to the configuration file, or None.
		:rtype: str
		"""
		if directory:
			root = os.path.abspath(os.sep)
			if os.path.isdir(directory):
				path = os.path.abspath(directory)
			else:
				path = os.path.dirname(os.path.abspath(directory))
			while path and path != root and os.path.isdir(path):
				filename = self.configuration.make_document_config_filename(path)
				if filename and os.path.isfile(filename):
					return filename
				path = os.path.dirname(path)
		return None

	def add_cli_options(self,  parser : argparse.ArgumentParser):
		"""
		Add the definition of the application CLI options.
		:param parser: the CLI parser
		:type parser: argparse.ArgumentParser
		"""
		pass

	def add_cli_positional_arguments(self,  parser : argparse.ArgumentParser):
		"""
		Add the definition of the application CLI positional arguments.
		:param parser: the CLI parser
		:type parser: argparse.ArgumentParser
		"""
		pass

	def add_bootstrap_cli_options(self):
		"""
		Add the definition of the CLI options for bootstrapping: general ones and those for path management.
		"""
		self._add_standard_cli_options_general()
		self._add_standard_cli_options_path()

	def add_standard_cli_options(self):
		"""
		Add the definition of the standard CLI options, except the general ones and those for path management.
		"""
		self._add_standard_cli_options_output()
		self._add_standard_cli_options_tex()
		self._add_standard_cli_options_translator()
		self._add_standard_cli_options_biblio()
		self._add_standard_cli_options_index()
		self._add_standard_cli_options_glossary()
		self._add_standard_cli_options_warning()
		self._add_standard_cli_options_logging()


	def _add_standard_cli_options_general(self):
		"""
		Add standard CLI options in the "general" category.
		"""
		# --version
		self._cli_parser.add_argument('--version',
			action = 'version',
			help = T('Display the version of AutoLaTeX'))


	def _add_standard_cli_options_path(self):
		"""
		Add standard CLI options in the "path configuration" category.
		"""
		path_group = self._cli_parser.add_argument_group(T('path optional arguments'))

		input_method_group = path_group.add_mutually_exclusive_group()

		outer : AbstractAutoLaTeXMain = self

		# --directory
		class DirectoryAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				if os.path.isdir(value):
					outer.configuration.document_directory = value
					outer.configuration.document_filename = None
				else:
					logging.error(T("Invalid directory: %s") % value)
					outer._exit_on_failure()
		input_method_group.add_argument('-d', '--directory',
			action = DirectoryAction,
			help = T('Specify a directory in which a LaTeX document to compile is located. You could specify this option for each directory in which you have a LaTeX document to treat'))

		# --file
		class FileAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				if os.path.isfile(value):
					outer.configuration.set_document_directory_and_filename(value)
				else:
					logging.error(T("File not found: %s") % value)
					outer._exit_on_failure()
		input_method_group.add_argument('-f', '--file',
			action = FileAction,
			metavar = 'TEX_FILE',
			help = T('Specify the main LaTeX file to compile. If this option is not specified, AutoLaTeX will search for a TeX file in the current directory'))

		# --search-project-from
		class SearchProjectFromAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				if value:
					config_file = outer._detect_autolatex_configuration_file(value)
				else:
					config_file = outer._detect_autolatex_configuration_file(outer.configuration.document_directory)
				if config_file:
					config_reader = OldStyleConfigReader()
					outer.configuration = config_reader.read_document_config_safely(config_file, outer.configuration)
					outer.__read_document_configuration = False
		path_group.add_argument('--search-project-from',
			action=SearchProjectFromAction, 
			metavar = 'FILE',
			help = T('When this option is specified, AutoLaTeX is searching a project configuration file (usually \'.autolatex_project.cfg\' on Unix platforms) in the directory of the specified FILE or in one of its ancestors'))


	def _add_standard_cli_options_output(self):
		"""
		Add standard CLI options in the "output configuration" category.
		"""
		output_group = self._cli_parser.add_argument_group(T('output optional arguments'))

		output_type_group = output_group.add_mutually_exclusive_group()

		outer : AbstractAutoLaTeXMain = self

		# --pdf
		class PdfAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.generation.pdf_mode = True
		output_type_group.add_argument('--pdf',
			action = PdfAction,
			nargs = 0,
			help = T('Do the compilation to produce a PDF document'))

		# --dvi
		# --ps
		class DvipsAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.generation.pdf_mode = False
		output_type_group.add_argument('--dvi',  '--ps',
			action = DvipsAction,
			nargs = 0,
			help = T('Do the compilation to produce a DVI, XDV or Postscript document'))

		# --stdout
		# --stderr
		class StdouterrAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				eprintpkg.IS_STANDARD_OUTPUT = self.const

		std_output_group = output_group.add_mutually_exclusive_group()

		std_output_group.add_argument('--stdout',
			action = StdouterrAction,
			const = True, 
			nargs = 0,
			help = T('All the standard messages (no log message) are printed out on the standard output (stdout) of the process'))

		std_output_group.add_argument('--stderr',
			action = StdouterrAction,
			const = False, 
			nargs = 0,
			help = T('All the standard messages (no log message) are printed out on the standard error output (stderr) of the process'))


	def _add_standard_cli_options_tex(self):
		"""
		Add standard CLI options in the "tex configuration" category.
		"""
		tex_group = self._cli_parser.add_argument_group(T('TeX optional arguments'))

		tex_tool_group = tex_group.add_mutually_exclusive_group()

		outer : AbstractAutoLaTeXMain = self

		# --pdflatex
		class PdflatexCmdAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.generation.latex_compiler = 'pdflatex'
		tex_tool_group.add_argument('--pdflatex',
			action = PdflatexCmdAction,
			nargs = 0,
			help = T('Use the LaTeX command: \'pdflatex\''))

		# --latex
		class LatexCmdAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.generation.latex_compiler = 'latex'
		tex_tool_group.add_argument('--latex',
			action = LatexCmdAction,
			nargs = 0,
			help = T('Use the historical LaTeX command: \'latex\''))

		# --lualatex
		class LualatexCmdAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.generation.latex_compiler = 'lualatex'
		tex_tool_group.add_argument('--lualatex',
			action = LualatexCmdAction,
			nargs = 0,
			help = T('Use the LaTeX command: \'lualatex\''))

		# --xelatex
		class XelatexCmdAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.generation.latex_compiler = 'xelatex'
		tex_tool_group.add_argument('--xelatex',
			action = XelatexCmdAction,
			nargs = 0,
			help = T('Use the LaTeX command: \'xelatex\''))

		# --synctex
		# --nosynctex
		synctex_group = tex_group.add_mutually_exclusive_group()

		class SynctexAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.generation.synctex = self.const

		synctex_group.add_argument('--synctex',
			action = SynctexAction,
			const = True, 
			nargs = 0,
			help = T('Enable the generation of the output file with SyncTeX'))

		synctex_group.add_argument('--nosynctex',
			action = SynctexAction,
			const = False, 
			nargs = 0,
			help = T('Disable the generation of the output file with SyncTeX'))

		# --extramacros
		# --noextramacros
		extramacros_group = tex_group.add_mutually_exclusive_group()

		class ExtramacrosAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.generation.include_extra_macros = self.const

		extramacros_group.add_argument('--extramacro',
			action = ExtramacrosAction,
			const = True,
			nargs = 0,
			help = T('Enable the support of the extra TeX and LaTeX macros and environments'))

		synctex_group.add_argument('--noextramacro',
			action = ExtramacrosAction,
			const = False,
			nargs = 0,
			help = T('Disable the support of the extra TeX and LaTeX macros and environments'))


	def _add_standard_cli_options_translator(self):
		"""
		Add standard CLI options in the "translator configuration" category.
		"""
		translator_group = self._cli_parser.add_argument_group(T('translator optional arguments'))

		outer : AbstractAutoLaTeXMain = self

		# --auto
		# --noauto
		class AutoAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.translators.is_translator_enable = self.const

		enable_translator_group = translator_group.add_mutually_exclusive_group()

		enable_translator_group.add_argument('--auto',
			action = AutoAction,
			const = True,
			nargs = 0,
			help = T('Enable the auto generation of the figures'))

		enable_translator_group.add_argument('--noauto',
			action = AutoAction,
			const = False,
			nargs = 0,
			help = T('Disable the auto generation of the figures'))

		# --exclude
		class ExcludeAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.translators.set_included(value, TranslatorLevel.DOCUMENT, False)
		translator_group.add_argument('-e', '--exclude',
			action = ExcludeAction,
			metavar = 'TRANSLATOR',
			help = T('Avoid AutoLaTeX to load the translator named TRANSLATOR'))

		# --include
		class IncludeAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.translators.set_included(value, TranslatorLevel.DOCUMENT, True)
		translator_group.add_argument('-i', '--include',
			action = IncludeAction,
			metavar = 'TRANSLATOR',
			help = T('Force AutoLaTeX to load the translator named TRANSLATOR'))

		# --include-path
		class IncludePathAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				paths = genutils.to_path_list(value, outer.configuration.document_directory)
				for path in paths:
					outer.configuration.translators.add_include_path(path)
		translator_group.add_argument('-I', '--include-path',
			action = IncludePathAction,
			metavar = 'PATH',
			help = T('Notify AutoLaTeX that it could find translator scripts inside the specified directories. The specified PATH could be a list of paths separated by the operating system\'s path separator (\':\' for Unix, \';\' for Windows for example)'))

		# --imgdirectory
		class ImgDirectoryAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				paths = genutils.to_path_list(value, outer.configuration.document_directory)
				for path in paths:
					outer.configuration.translators.add_image_path(path)
		translator_group.add_argument('-D', '--imgdirectory',
			action = ImgDirectoryAction,
			metavar = 'DIRECTORY',
			help = T('Specify a directory inside which AutoLaTeX will find the pictures which must be processed by the translators. Each time this option is put on the command line, a directory is added inside the list of the directories to explore'))


	def _add_standard_cli_options_biblio(self):
		"""
		Add standard CLI options in the "bibliography configuration" category.
		"""
		biblio_group = self._cli_parser.add_argument_group(T('bibliography optional arguments'))

		outer : AbstractAutoLaTeXMain = self

		# --biblio
		# --nobiblio
		class BiblioAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.generation.is_biblio_enable = self.const

		enable_biblio_group = biblio_group.add_mutually_exclusive_group()

		enable_biblio_group.add_argument('--biblio',
			action=BiblioAction,
			const = True, 
			nargs = 0, 
			help = T('Enable the call to the bibliography tool (BibTeX, Biber...)'))

		enable_biblio_group.add_argument('--nobiblio',
			action=BiblioAction,
			const = False, 
			nargs = 0, 
			help = T('Disable the call to the bibliography tool (BibTeX, Biber...)'))


	def _add_standard_cli_options_index(self):
		"""
		Add standard CLI options in the "index configuration" category.
		"""
		index_group = self._cli_parser.add_argument_group(T('index optional arguments'))

		outer : AbstractAutoLaTeXMain = self

		# --defaultist
		class DefaultistAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.generation.makeindex_style_filename = outer.configuration.get_system_ist_file()
		index_group.add_argument('--defaultist',
			action = DefaultistAction,
			nargs = 0,
			help = T('Allow AutoLaTeX to use MakeIndex with the default style (\'.ist\' file)'))

		# --index
		index_e_group = index_group.add_mutually_exclusive_group()

		class IndexAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.generation.is_index_enable = True
				if value:
					path = genutils.abs_path(value, outer.configuration.document_directory)
					if os.path.isfile(path):
						outer.configuration.generation.makeindex_style_filename = path
					else:
						logging.error(T("File not found: %s") % value)
						outer._exit_on_failure()
						return
		index_e_group.add_argument('--index',
			action = IndexAction, 
			default = None, 
			nargs = '?', 
			metavar = 'FILE',
			help = T('Allow AutoLaTeX to use MakeIndex. If this option was specified with a value, the FILE value will be assumed to be an \'.ist\' file to pass to MakeIndex'))

		# --noindex
		class NoindexAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.generation.is_index_enable = False
		index_e_group.add_argument('--noindex',
			action = NoindexAction,
			nargs = 0, 
			help = T('Avoid AutoLaTeX to use MakeIndex'))


	def _add_standard_cli_options_glossary(self):
		"""
		Add standard CLI options in the "glossary configuration" category.
		"""
		glossary_group = self._cli_parser.add_argument_group(T('glossary optional arguments'))

		outer : AbstractAutoLaTeXMain = self

		# --glossary
		# --noglossary
		# --gloss
		# --nogloss
		class GlossaryAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.generation.is_glossary_enable = self.const

		glossary_e_group = glossary_group.add_mutually_exclusive_group()

		glossary_e_group.add_argument('--glossary', '--gloss', 
			action=GlossaryAction,
			const = True, 
			nargs = 0, 
			help = T('Enable the call to the glossary tool (makeglossaries...)'))

		glossary_e_group.add_argument('--noglossary', '--nogloss', 
			action=GlossaryAction,
			const = False, 
			nargs = 0, 
			help = T('Disable the call to the glossary tool (makeglossaries...)'))


	def _add_standard_cli_options_warning(self):
		"""
		Add standard CLI options in the "warning configuration" category.
		"""
		warning_cfg_group = self._cli_parser.add_argument_group(T('warning optional arguments'))

		outer : AbstractAutoLaTeXMain = self

		# --file-line-warning
		# --nofile-line-warning
		class FilelinewarningAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				outer.configuration.generation.extended_warnings = self.const

		warning_group = warning_cfg_group.add_mutually_exclusive_group()

		warning_group.add_argument('--file-line-warning',
			action=FilelinewarningAction,
			const = True, 
			nargs=0, 
			help = T('Enable the extended format for warnings. This format add the filename and the line number where the warning occurs, before the warning message by itself'))

		warning_group.add_argument('--nofile-line-warning',
			action=FilelinewarningAction,
			const = False, 
			nargs=0, 
			help = T('Disable the extended format for warnings. This format add the filename and the line number where the warning occurs, before the warning message by itself'))

	def _add_standard_cli_options_logging(self):
		"""
		Add standard CLI options in the "logging configuration" category.
		"""
		logging_group = self._cli_parser.add_argument_group(T('logging optional arguments'))

		outer : AbstractAutoLaTeXMain = self

		# --debug
		class DebugAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				logger = logging.getLogger()
				logger.setLevel(LogLevel.DEBUG)
				for handler in logger.handlers:
					handler.setLevel(LogLevel.DEBUG)
		logging_group.add_argument('--debug',
			action = DebugAction,
			nargs = 0,
			help = T('Run AutoLaTeX in debug mode, i.e., the maximum logging level'))

		# --quiet
		class QuietAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				logger = logging.getLogger()
				logger.setLevel(LogLevel.ERROR)
				for handler in logger.handlers:
					handler.setLevel(LogLevel.ERROR)
		logging_group.add_argument('-q', '--quiet',
			action = QuietAction,
			nargs = 0,
			help = T('Run AutoLaTeX without logging except the errors'))

		# --silent
		class SilentAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				logger = logging.getLogger()
				logger.setLevel(LogLevel.OFF)
				for handler in logger.handlers:
					handler.setLevel(LogLevel.OFF)
		logging_group.add_argument('--silent',
			action = SilentAction,
			nargs = 0,
			help = T('Run AutoLaTeX without logging, including no error message'))

		# --info
		class InfoAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				logger = logging.getLogger()
				logger.setLevel(LogLevel.INFO)
				for handler in logger.handlers:
					handler.setLevel(LogLevel.INFO)
		logging_group.add_argument('--info',
			action = InfoAction,
			nargs = 0,
			help = T('Run AutoLaTeX with info logging level'))

		# --verbose
		class VerboseAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				logger = logging.getLogger()
				level = LogLevel.to_lower_level(logger.level)
				if level < LogLevel.TRACE:
					# Specific behavior that shows up the configuration
					outer.show_configuration()
					outer._exit_on_success()
				else:
					logger.setLevel(level)
					for handler in logger.handlers:
						handler.setLevel(level)
		logging_group.add_argument('-v', '--verbose',
			action = VerboseAction,
			nargs = 0,
			help = T('Each time this option was specified, AutoLaTeX is more verbose'))

		# --Wall
		class WallAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				logger = logging.getLogger()
				logger.setLevel(LogLevel.FINE_WARNING)
				for handler in logger.handlers:
					handler.setLevel(LogLevel.FINE_WARNING)
		logging_group.add_argument('--Wall',
			action = WallAction,
			nargs = 0,
			help = T('Show all the warnings'))

		#--Wnone
		class WnoneAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				logger = logging.getLogger()
				logger.setLevel(LogLevel.ERROR)
				for handler in logger.handlers:
					handler.setLevel(LogLevel.ERROR)
		logging_group.add_argument('--Wnone',
			action = WnoneAction,
			nargs = 0,
			help = T('Show no warning'))

		#--showloglevel
		class ShowloglevelAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				logger = logging.getLogger()
				level = logger.level
				level_name = LogLevel.get_logging_level_name(level)
				eprintpkg.eprint("%s (%d)" % (level_name, level))
				outer._exit_on_success()
		logging_group.add_argument('--showloglevel',
			action = ShowloglevelAction,
			nargs = 0,
			help = T('Show the current level of logging'))

		#--testlogs
		class TestlogsAction(argparse.Action):
			@override
			def __call__(self, parser, namespace, value, option_string=None):
				for level in LogLevel:
					level_name = LogLevel.get_logging_level_name(level)
					logging.log(level, T("message for level '%s' (%d)") % (level_name, level))
				outer._exit_on_success()
		logging_group.add_argument('--testlogs',
			action = TestlogsAction,
			nargs = 0,
			help = T('Show a message at each level of logging'))


	def _init_logging_system(self):
		"""
		Configure the logging system.
		"""
		if self.__configuration.logging.message:
			logging.basicConfig(format = self.__configuration.logging.message, level = self.__configuration.logging.level)
		else:
			handler = logging.StreamHandler()
			handler.setFormatter(DynamicLogLevelFormatter())
			logger = logging.getLogger()
			logger.addHandler(handler)
			logger.setLevel(self.__configuration.logging.level)

	# noinspection PyMethodMayBeStatic
	def _build_help_epilog(self) -> str | None:
		"""
		Build a string that could serve as help epilog.
		:return: the epilog text.
		:rtype: str | None
		"""
		return None

	# noinspection PyMethodMayBeStatic
	def _create_cli_parser(self, name : str, version : str, default_arg : Any | None = None,
						   description : str | None = None, osname : str | None = None,
						   platform_name : str | None = None, epilog : str | None = None) -> argparse.ArgumentParser:
		"""
		Create the instance of the CLI parser.
		:param name: The name of the program.
		:type name: str
		:param version: The version of the program.
		:type version: str
		:param default_arg: The default argument for the program.
		:type default_arg: Any | None
		:param description: The description of the program.
		:type description: str | None
		:param osname: The name of the operating system.
		:type osname: str | None
		:param platform_name: The name of the platform.
		:type platform_name: str | None
		:param epilog: The epilog of the documentation.
		:type epilog: str | None
		:return: the created instance.
		:rtype: argparse.ArgumentParser
		"""
		if not description:
			description = T('AutoLaTeX is a tool for managing small to large sized LaTeX documents. The user can easily '
				'perform all required steps to do such tasks as: preview the document, or produce a PDF file. '
				'AutoLaTeX will keep track of files that have changed and how to run the various programs that '
				'are needed to produce the output. One of the best feature of AutoLaTeX is to provide translator '
				'rules (aka. translators) to automatically generate the figures which will be included into the PDF.')
		if not osname:
			osname = os.name
		if not platform_name:
			platform_name = platform.system()
		parser = argparse.ArgumentParser(prog=name,
										 argument_default=default_arg,
										 description=description,
										 epilog=epilog,
										 formatter_class=argparse.HelpFormatter)
		parser.version = T("%s %s - %s/%s platform") % (name, version, osname, platform_name)
		return parser


	def _pre_run_program(self, strict_arguments : bool) -> tuple[Namespace,list[str],list[str]]:
		"""
		Run the general behavior of the main program before the specific behavior related to commands.
		:param strict_arguments: Indicates if only the arguments from the main script and the associated commands are allowed.
		If True, the CLI arguments are parsed strictly and if an argument is not known, there is a failure. If False,
		the function doers not fail if it is encountering an unknown argument.
		:type strict_arguments: bool
		:return: the tuple with as first element the parsed CLI arguments (argparse namespace), the actions , and the second element the list of unknown arguments.
		:rtype: tuple[Namespace,list[str],list[str]]
		"""

		# Get the command line value
		if self.__initial_argv is None or not isinstance(self.__initial_argv, list):
			script_cli = sys.argv[1:]
		else:
			script_cli = list(self.__initial_argv)

		# Force the document_directory to have a default value
		if not self.__configuration.document_directory:
			self.__configuration.document_directory = os.getcwd()

		# Parse command line options that are the base and may change the behavior of the rest of the tool
		self.add_bootstrap_cli_options()
		self.add_standard_cli_options()
		self.add_cli_options(self._cli_parser)
		self.add_cli_positional_arguments(self._cli_parser)

		# Parse the rest of the command line according to the registered CLI definition
		positional_arguments = [arg for arg in script_cli if not arg.startswith('-')]

		# Check if a command is provided; and add the default command.
		if not positional_arguments:
			default_action = self.configuration.default_cli_action
			if default_action:
				positional_arguments.insert(0, default_action)

		if strict_arguments:
			parsed_args = self._cli_parser.parse_args(args=script_cli)
			other_args = list()
		else:
			parsed_args, other_args =  self._cli_parser.parse_known_args(args=script_cli)

		# Read configuration from the document's folder, if it is possible
		if self.__read_document_configuration:
			config_file = self._detect_autolatex_configuration_file(self.__configuration.document_directory)
			if config_file:
				config_reader = OldStyleConfigReader()
				self.__configuration = config_reader.read_document_config_safely(config_file, self.__configuration)

		# Remove positional arguments if they are not recognized (other args)
		positional_arguments = [arg for arg in positional_arguments if arg not in other_args]

		return parsed_args, positional_arguments, other_args


	# noinspection PyUnusedLocal
	def _post_run_program(self,  cli_arguments : Namespace, positional_arguments: list[str], unknown_arguments: list[str]):
		"""
		Run the behavior of the main program after the specific behavior.
		:param cli_arguments: the argparse object that contains the CLI arguments successfully parsed.
		:type cli_arguments: Namespace
		:param positional_arguments: the CLI arguments that are not consumed by the argparse library.
		:type positional_arguments: list[str]
		:param unknown_arguments: the list of the unsupported arguments.
		:type unknown_arguments: list[str]
		"""
		self._exit_on_success()

	@abstractmethod
	def _run_program(self, cli_arguments : Namespace, positional_arguments: list[str], unknown_arguments: list[str]):
		"""
		Run the specific behavior.
		:param cli_arguments: the argparse object that contains the CLI arguments successfully parsed.
		:type cli_arguments: Namespace
		:param positional_arguments: the CLI arguments that are not consumed by the argparse library.
		:type positional_arguments: list[str]
		:param unknown_arguments: the list of the unsupported arguments.
		:type unknown_arguments: list[str]
		"""
		raise NotImplementedError


	def run(self):
		"""
		Run the program. The program is run according to three steps: initialization (pre-run), command run (run-program) and post-execution (post-run).
		"""
		cli_arguments, positional_arguments, unknown_arguments = self._pre_run_program(True)
		self._run_program(cli_arguments, positional_arguments, unknown_arguments)
		self._post_run_program(cli_arguments, positional_arguments, unknown_arguments)


	@staticmethod
	def build_command_dict(package_name : str) -> dict[str,AutolatexCommand]:
		"""
		Build the dictionary that maps the command's names to AutoLaTeX commands.
		:param package_name: The name of the package to explore.
		:type package_name: str
		:return: the dict of the commands.
		:rtype: dict[str,AutolatexCommand]
		"""
		execution_environment : dict[str,Any] = {
			'modules': None,
		}
		exec("import " + package_name + "\nmodules = " + package_name + ".__all__",  None, execution_environment)
		modules = execution_environment['modules']
		ids = dict()
		for module in modules:
			execution_environment = {
				'id': None,
				'alias': None,
				'type': None,
				'help': None,
				'prereq': None,
			}
			cmd = textwrap.dedent("""\
						from %s.%s import MakerAction
						type = MakerAction
						id = MakerAction.id
						help = MakerAction.help
						try:
							alias = MakerAction.alias
						except:
							alias = None
						try:
							prereq = MakerAction.prerequisites
						except:
							prereq = None
				""") % (package_name,  module)
			exec(cmd,  None, execution_environment)
			cmd_id = execution_environment['id']
			cmd_alias = execution_environment['alias']
			if cmd_alias is not None:
				if isinstance(cmd_alias, tuple) or isinstance(cmd_alias, list):
					cmd_alias = list(cmd_alias)
				else:
					cmd_alias = list([str(cmd_alias)])
			cmd_prereq = execution_environment['prereq']
			if cmd_prereq is not None:
				if isinstance(cmd_prereq, tuple) or isinstance(cmd_prereq, list):
					cmd_prereq = list(cmd_prereq)
				else:
					cmd_prereq = list([str(cmd_prereq)])
			ids[cmd_id] = AutolatexCommand(name=cmd_id,  action_type=execution_environment['type'],
										   help_text=execution_environment['help'],
										   aliases=cmd_alias,
										   prerequisites=cmd_prereq)
		return ids

	def _create_cli_arguments_for_commands(self,  commands : dict[str,AutolatexCommand],  title : str,  help_text : str,  metavar : str = 'COMMAND'):
		"""
		Create CLI arguments for the given commands.
		:param commands: the pairs "command id"-"command instance".
		:type commands: dict[str,AutolatexCommand]
		:param title: The title of the command set.
		:type title: str
		:param help_text: The help description of the command set.
		:type help_text: str
		:param metavar: The name of the command set in the help. Default is: COMMAND.
		:type metavar: str
		"""
		subparsers = self.cli_parser.add_subparsers(title=title,  metavar=metavar,  help=help_text)
		for cmd_id,  command in commands.items():
			command.instance.register_command(sub_parsers=subparsers,
											  command_name=command.name,
											  command_help=command.help,
											  command_aliases=command.aliases,
											  configuration=self.configuration)

	def build_command_list_from_prerequisites(self, commands_to_run : list[str], all_commands : dict[str,AutolatexCommand]) -> list[str]:
		"""
		Build an ordered list of commands depending on the prerequisites of each command.
		:param commands_to_run: the list of commands to run.
		:type commands_to_run:  list[str]
		:param all_commands: the definition of all the available commands.
		:type all_commands: dict[str,AutolatexCommand]
		:return: the ordered list of commands
		:rtype: list[str]
		"""
		# Adjacency list for the graph
		graph = defaultdict(set[str])
		# In-degree for Kahn's algorithm
		in_degree = defaultdict(int)

		queue = deque(commands_to_run)
		to_be_run = set()
		while queue:
			cmd = queue.popleft()
			if cmd not in to_be_run:
				if cmd in all_commands:
					to_be_run.add(cmd)
					instance = all_commands[cmd]
					for prereq in instance.prerequisites:
						queue.append(prereq)
				else:
					msg = T('Undefined command %s') % cmd
					logging.error(msg)
					ex = Exception(msg)
					self._exit_on_exception(ex)
					raise ex

		for cmd in to_be_run:
			if cmd in all_commands:
				instance = all_commands[cmd]
				for prereq in instance.prerequisites:
					graph[prereq].add(cmd)
					in_degree[cmd] += 1
				if cmd not in in_degree:
					in_degree[cmd] = 0
			else:
				msg = T('Undefined command %s') % cmd
				logging.error(msg)
				ex = Exception(msg)
				self._exit_on_exception(ex)
				raise ex

		# Return the order in which commands should be executed. Kahn's algorithm for topological sort
		execution_order = list()
		queue = deque([cmd for cmd in in_degree if in_degree[cmd] == 0])

		while queue:
			current = queue.popleft()
			if current in in_degree:
				in_degree.pop(current)
			execution_order.append(current)
			for neighbor in graph[current]:
				in_degree[neighbor] -= 1
				if in_degree[neighbor] == 0:
					queue.append(neighbor)

		if in_degree:
			msg = T('Cycle detected in command prerequisites')
			logging.error(msg)
			ex = ValueError(msg)
			self._exit_on_exception(ex)
			raise ex

		return execution_order

	# noinspection PyMethodMayBeStatic
	def __unaliases(self, commands_to_run : list[str], all_commands : dict[str,AutolatexCommand]) -> list[str]:
		"""
		Replace any alias in the given list of commands to run by their regular names.
		:param commands_to_run: the list of names or aliases for the commands to be run.
		:type commands_to_run: list[str]
		:param all_commands: The definition of all the known commands.
		:type all_commands: dict[str,AutolatexCommand]
		:return: the list of commands to run, with their regular names.
		:rtype: list[str]
		"""
		aliases = dict()
		for name, cmd in all_commands.items():
			aliases[name] = name
			if cmd.aliases:
				for alias in cmd.aliases:
					if alias in aliases:
						raise Exception('multiple commands have the alias \'%s\'' % alias)
					aliases[alias] = name
		real_commands = list()
		for command in commands_to_run:
			if command in aliases:
				cmd = aliases[command]
				if cmd:
					real_commands.append(cmd)
				else:
					real_commands.append(command)
			else:
				real_commands.append(command)
		return real_commands

	def _execute_commands(self,  commands_to_run : list[str],  all_commands : dict[str,AutolatexCommand], cli_arguments : Namespace):
		"""
		Execute the commands.
		:param commands_to_run: List of arguments on the command line.
		:type commands_to_run: list[str]
		:param all_commands: Dict of all the available commands.
		:type all_commands: dict[str,AutolatexCommand]
		:param cli_arguments: the successfully parsed CLI arguments.
		:type cli_arguments: Namespace
		"""

		# Check existing command
		if not commands_to_run:
			logging.error(T('Unable to determine the command to run'))
			self._exit_on_failure()
		else:
			# Convert aliases to the real command names
			commands_to_run = self.__unaliases(commands_to_run, all_commands)

			# Build the list of commands
			cmds = self.build_command_list_from_prerequisites(commands_to_run, all_commands)

			# Run the commands
			for cmd in cmds:
				try:
					cmd_instance = all_commands[cmd]
					continuation = cmd_instance.instance.run(cli_arguments)
					if not continuation:
						self._exit_on_success()
						break
				except BaseException as exception:
					#logging.error(_T('Error when running the command: %s') % str(exception))
					self._exit_on_exception(exception)
					break

	@staticmethod
	def _detect_tex_file(directory : str) -> str | None:
		"""
		Detect the name of the main TeX file in the project directory.
		:param directory: the directory to search inside.
		:type directory: str
		:return: the filename of the root TeX file, or None if not found.
		:rtype: str | None
		"""
		files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith('.tex')]
		length = len(files)
		if length <= 0:
			logging.error(T("Unable to find a TeX file to compile in: %s") % directory)
			return None
		else:
			file = files[0]
			if length > 1:
				logging.warning(T("Too much TeX files in: %s") % directory)
				logging.warning(T("Select the TeX file: %s") % file)
			return file

	def _exit_on_failure(self):
		"""
		Exit the main program on failure.
		"""
		self.exiter.exit_on_failure()

	def _exit_on_success(self):
		"""
		Exit the main program on success.
		"""
		self.exiter.exit_on_success()

	def _exit_on_exception(self,  exception : BaseException):
		"""
		Exit the main program on exception.
		:param exception: The exception.
		:type exception: exception
		"""
		self.exiter.exit_on_exception(exception)
