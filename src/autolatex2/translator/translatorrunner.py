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
Translation engine.
"""

import logging
import os
import shlex
import subprocess
import re
from importlib import util as import_lib_util
import glob
from typing import override, Any

from autolatex2.config.configobj import Config
from autolatex2.translator.translatorobj import Translator
from autolatex2.translator.translatorrepository import TranslatorRepository
import autolatex2.utils.utilfunctions as genutils
from autolatex2.utils.extlogging import LogLevel
from autolatex2.utils.i18n import T


class TranslatorError(Exception):

	def __init__(self, msg : str):
		super().__init__(msg)
		self.message = msg

	@override
	def __str__(self) -> str:
		return self.message


class TranslatorRunner:
	"""
	Runner of translators.
	"""

	def __init__(self, repository : TranslatorRepository):
		"""
		Construct the runner of translators.
		:param repository: The repository of translators.
		:type repository: TranslatorRepository
		"""
		self._repository : TranslatorRepository = repository
		self.configuration : Config = repository.configuration
		self.__images : set[str] | None = None

	@property
	def translators_repository(self) -> TranslatorRepository:
		"""
		Replies the repository of translators that is used by this runner.
		:return: The repository of translators.
		:rtype: TranslatorRepository
		"""
		return self._repository

	def sync(self, detect_conflicts : bool = True):
		"""
		Resynchronize the translator data.
		:param detect_conflicts: Indicates if the conflicts in translator loading is run. Default is True.
		:type detect_conflicts: bool
		"""
		self._repository.sync(detect_conflicts = detect_conflicts)
		self.__images = None

	def add_source_image(self, filename : str):
		"""
		Add a source image.
		:param filename: The filename of a source image.
		:type filename: str
		"""
		if self.__images is None:
			self.__images = set(filename)
		else:
			self.__images.update(filename)

	def get_source_images(self) -> set[str]:
		"""
		Replies the list of the images on which the translators could be applied.
		:return: The list of the image filenames.
		:rtype: set[str]
		"""
		if self.__images is None:
			self.__images = set()
			# Add the images that were manually specified
			assert self.__images is not None
			self.__images.update(self.configuration.translators.images_to_convert)

			# Detect the image formats
			types = set()
			for translator in self._repository.included_translators.translators():
				types.update(translator.get_input_extensions())
			types = tuple(types)

			# Detect the image from the file system
			for image_directory in self.configuration.translators.image_paths:
				logging.debug(T("Detecting images inside '%s'") % image_directory)
				if self.configuration.translators.recursive_image_path:
					for root, dirs, files in os.walk(image_directory):
						for filename in files:
							abs_path = os.path.join(root, filename)
							if not genutils.is_hidden_file(abs_path) and abs_path.endswith(types):
								self.__images.add(abs_path)
				else:
					for filename in os.listdir(image_directory):
						abs_path = os.path.join(image_directory, filename)
						if not os.path.isdir(abs_path) and not genutils.is_hidden_file(abs_path):
							if abs_path.endswith(types):
								self.__images.add(abs_path)
		return self.__images

	def get_translator_for(self, input_filename : str, output_filename : str = None) -> Translator | None:
		"""
		Replies the translator that could be used for the given filename.
		:param input_filename: The name of the file to the translated.
		:type input_filename: str
		:param output_filename: The name of the file to be generated.
		:type output_filename: str
		:return: The translator or None
		:rtype: Translator | None
		"""
		# NOTE : Cannot use "os.path.splitex" because several extensions have characters before the point, e.g. "+tex.svg"
		if os.name == 'nt':
			f0 = input_filename.lower()
		else:
			f0 = input_filename
		candidate_extension = 0
		candidates = list()
		for translator in self._repository.included_translators.translators():
			exts = translator.get_input_extensions()
			for extension in exts:
				if f0.endswith(extension):
					ln = len(extension)
					if not candidates or ln > candidate_extension:
						candidate_extension = ln
						candidates = list([translator])
					elif candidate_extension == ln:
						candidates.append(translator)
		ln = len(candidates)
		if ln == 0:
			return None
		elif ln == 1:
			selected = candidates[0]
		else:
			if output_filename is not None:
				if os.name == 'nt':
					f1 = output_filename.lower()
				else:
					f1 = output_filename
				out_candidate_extension = 0
				out_candidates = list()
				for candidate in candidates:
					exts = candidate.get_output_extensions()
					for extension in exts:
						if f1.endswith(extension):
							ln = len(extension)
							if not candidates or ln > out_candidate_extension:
								out_candidate_extension = ln
								out_candidates = list([candidate])
							elif out_candidate_extension == ln:
								out_candidates.append(candidate)
				if len(out_candidates) == 1:
					selected = out_candidates[0]
				else:
					selected = out_candidates[0]
					logging.warning(T("Too much translators for file '%s': %s") % (os.path.basename(input_filename), '; '.join(str(element) for element in out_candidates)))
					logging.warning(T("Selecting translator: %s") % (str(selected)))
			else:
				selected = candidates[0]
				logging.warning(T("Too much translators for file '%s': %s") % (os.path.basename(input_filename), '; '.join(str(element) for element in candidates)))
				logging.warning(T("Selecting translator: %s") % (str(selected)))
		return selected

	# noinspection DuplicatedCode
	def get_temporary_files(self, *, in_file: str, translator_name: str = None, out_file: str = None,
							pdf_mode: bool = None) -> list[str]:
		"""
		Replies the list of the temporary files that could be generated by the translator.
		:param in_file: The name of the source file.
		:type in_file: str
		:param translator_name: Name of the translator to run. Default value: None.
		:type translator_name: str
		:param out_file: The name of the output file. Default value: None
		:type out_file: str
		:param pdf_mode: Indicates if the generation must be done in PDF mode or not. The value is True, False, or None to get the global configuration flag.
		:type pdf_mode: bool
		:return: The list of the temporary files.
		:rtype: list[str]
		"""
		if not in_file:
			return list()

		translator = None
		if translator_name:
			translator = self._repository.get_object_for(translator_name)
		if translator is None:
			translator = self.get_translator_for(in_file)
		if translator is None:
			raise TranslatorError(T("Unable to find a translator for the source image %s") % in_file)

		in_exts = translator.get_input_extensions()
		in_ext = None
		for e in in_exts:
			if in_file.endswith(e):
				in_ext = e
				break
		if not in_ext:
			in_ext = translator.get_input_extensions()[0]
		out_exts = translator.get_output_extensions()
		if len(out_exts) > 0 and out_exts[0]:
			out_ext = out_exts[0]
		else:
			out_ext = ''

		if not out_file:
			out_file = genutils.basename2(in_file, *in_exts) + out_ext

		if pdf_mode is None:
			current_pdf_mode = translator.configuration.generation.pdf_mode
		else:
			current_pdf_mode = pdf_mode

		environment = translator.get_constants()
		environment['pdfmode'] = bool(current_pdf_mode)
		environment['in'] = in_file
		indir = os.path.dirname(in_file)
		environment['indir'] = indir
		environment['in_exts'] = in_exts
		environment['in_ext'] = in_ext
		environment['out'] = out_file
		outdir = os.path.dirname(out_file)
		environment['outdir'] = outdir
		environment['out_exts'] = out_exts
		environment['out_ext'] = out_ext
		environment['ext'] = out_ext
		environment['outbasename'] = genutils.basename(out_file, *out_exts)
		environment['outwoext'] = os.path.join(outdir, str(environment['outbasename']))
		environment['outmode'] = 'pdf' if current_pdf_mode else 'eps'

		fixed_patterns = genutils.expand_env(translator.get_temporary_file_patterns(), environment)
		temp_files = list()
		for pattern in fixed_patterns:
			if os.path.isabs(pattern):
				pt0 = pattern
				pt1 = pattern
			else:
				pt0 = os.path.join(indir,  pattern)
				pt1 = os.path.join(outdir,  pattern)
			temp_files.extend(glob.glob(pathname = pt0,  recursive = False))
			if indir != outdir:
				temp_files.extend(glob.glob(pathname = pt1,  recursive = False))
		return temp_files

	# noinspection DuplicatedCode
	def get_target_files(self, *, in_file : str, translator_name : str = None, out_file : str = None,
						 pdf_mode : bool = None) -> list[str]:
		"""
		Replies the list of the generated files that are by the translator. The replied files exist in the file system.
		:param in_file: The name of the source file. Preferably, it should be absolute filename.
		:type in_file: str
		:param translator_name: Name of the translator to run. Default value: None.
		:type translator_name: str
		:param out_file: The name of the output file. Default value: None
		:type out_file: str
		:param pdf_mode: Indicates if the generation must be done in PDF mode or not. The value is True, False, or None to get the global configuration flag.
		:type pdf_mode: bool
		:return: The list of the target files.
		:rtype: list[str]
		"""
		if not in_file:
			return list()

		translator = None
		if translator_name:
			translator = self._repository.get_object_for(translator_name)
		if translator is None:
			translator = self.get_translator_for(in_file)
		if translator is None:
			raise TranslatorError(T("Unable to find a translator for the source image %s") % in_file)

		in_exts = translator.get_input_extensions()
		in_ext = None
		len_in_ext = 0
		for e in in_exts:
			if in_file.endswith(e) and len(e) > len_in_ext:
				in_ext = e
				len_in_ext = len(e)
		if not in_ext:
			in_ext = in_exts[0]
		out_exts = translator.get_output_extensions()
		if len(out_exts) > 0 and out_exts[0]:
			out_ext = out_exts[0]
		else:
			out_ext = ''
		if not out_file:
			out_file = genutils.basename2(in_file, *in_exts) + out_ext

		if pdf_mode is None:
			current_pdf_mode = translator.configuration.generation.pdf_mode
		else:
			current_pdf_mode = pdf_mode

		environment = translator.get_constants()
		environment['pdfmode'] = bool(current_pdf_mode)
		environment['in'] = in_file
		indir = os.path.dirname(in_file)
		environment['indir'] = indir
		environment['inexts'] = in_exts
		environment['inext'] = in_ext
		environment['out'] = out_file
		outdir = os.path.dirname(out_file)
		environment['outdir'] = outdir
		environment['outexts'] = out_exts
		environment['outext'] = out_ext
		environment['ext'] = out_ext
		environment['outbasename'] = genutils.basename(out_file, *out_exts)
		environment['outwoext'] = os.path.join(outdir, str(environment['outbasename']))
		environment['outmode'] = 'pdf' if current_pdf_mode else 'eps'

		fixed_patterns = genutils.expand_env(translator.get_target_file_patterns(), environment)
		target_files = set()
		for pattern in fixed_patterns:
			if os.path.isabs(pattern):
				pt0 = pattern
				pt1 = pattern
			else:
				pt0 = os.path.join(indir,  pattern)
				pt1 = os.path.join(outdir,  pattern)
			target_files.update(self.__do_glob(pt0))
			if indir != outdir:
				target_files.update(self.__do_glob(pt1))
		return list(target_files)

	def __do_glob(self, pattern : str) -> list[str]:
		glb = glob.glob(pattern, root_dir=self.configuration.document_directory)
		return glb

	# noinspection DuplicatedCode
	def generate_image(self, *, in_file : str, translator_name : str = None, out_file : str = None, only_more_recent : bool = True,
					   pdf_mode : bool = None,
					   fail_on_error : bool = True) -> str | None:
		"""
		Generate the image from the given source file by running the appropriate translator.
		:param in_file: The name of the source file.
		:type in_file: str
		:param translator_name: Name of the translator to run. Default value: None.
		:type translator_name: str
		:param out_file: The name of the output file. Default value: None
		:type out_file: str
		:param only_more_recent: Indicates if the translation is always run (False) or only if the source file is more recent than the target file. Default value: True
		:type only_more_recent: bool
		:param pdf_mode: Indicates if the generation must be done in PDF mode or not. The value is True, False, or None to get the global configuration flag.
		:type pdf_mode: bool
		:param fail_on_error: Indicates if the translator generates a Python exception on error during the run. Default value: True.
		:type fail_on_error: bool
		:return: The output filename on success; otherwise None on error or if the file is up-to-date
		:rtype: str | None
		"""
		if not in_file:
			return None

		translator = None
		if translator_name:
			translator = self._repository.get_object_for(translator_name)
			if not translator:
				raise TranslatorError(T("Translator %s was not found but it is mandatory for converting") % translator_name)
		if translator is None:
			translator = self.get_translator_for(in_file, out_file)
		if translator is None:
			raise TranslatorError(T("Unable to find a translator for the source image %s") % in_file)

		if not os.access(in_file, os.R_OK):
			errmsg = T("%s: file not found or not readable.") % in_file
			if fail_on_error:
				raise TranslatorError(errmsg)
			else:
				logging.error(errmsg)
				return None

		in_exts = translator.get_input_extensions()
		in_ext = None
		for e in in_exts:
			if in_file.endswith(e):
				in_ext = e
				break
		if not in_ext:
			in_ext = translator.get_input_extensions()[0]
		out_exts = translator.get_output_extensions()
		if len(out_exts) > 0 and out_exts[0]:
			out_ext = out_exts[0]
		else:
			out_ext = ''

		if not out_file:
			out_file = genutils.basename2(in_file, *in_exts) + out_ext

		# Try to avoid the translation if the source file is no more recent than the target file.
		if only_more_recent:
			in_change = genutils.get_file_last_change(in_file)
			if in_change is not None:
				out_change = genutils.get_file_last_change(out_file)
				if out_change is None:
					# No out file, try to detect other types of generated files
					dir_name = os.path.dirname(out_file)
					for filename in os.listdir(dir_name):
						abs_path = os.path.join(dir_name, filename)
						if not os.path.isdir(abs_path) and not genutils.is_hidden_file(abs_path):
							bn = genutils.basename(filename, *out_exts)
							m = re.match('^('+re.escape(bn+'_')+'.*)'+re.escape(out_ext)+'$', filename, re.S)
							if m:
								t = genutils.get_file_last_change(abs_path)
								if t is not None and (out_change is None or t < out_change):
									out_change = t
									break
				if out_change is not None and in_change <= out_change:
					# No need to translate again
					logging.log(LogLevel.FINE_INFO, T("%s is up-to-date") % (os.path.basename(out_file)))
					return None

		logging.info(T("%s -> %s") % (os.path.basename(in_file), os.path.basename(out_file)))

		if pdf_mode is None:
			current_pdf_mode = translator.configuration.generation.pdf_mode
		else:
			current_pdf_mode = pdf_mode

		logging.debug(T("Translator: %s") % translator.name)
		logging.debug(T("In: %s") % str(in_file))
		logging.debug(T("Out: %s") % str(out_file))
		logging.debug(T("Pdf: %s") % str(current_pdf_mode))

		command_line = translator.get_command_line()
		embedded_function = translator.get_embedded_function()

		environment = translator.get_constants()
		environment['pdfmode'] = bool(current_pdf_mode)
		environment['in'] = in_file
		environment['indir'] = os.path.dirname(in_file)
		environment['inexts'] = in_exts
		environment['inext'] = in_ext
		environment['out'] = out_file
		environment['outdir'] = os.path.dirname(out_file)
		environment['outexts'] = out_exts
		environment['outext'] = out_ext
		environment['ext'] = out_ext
		environment['outbasename'] = genutils.basename(out_file, *out_exts)
		environment['outwoext'] = os.path.join(os.path.dirname(out_file), str(environment['outbasename']))
		environment['outmode'] = 'pdf' if current_pdf_mode else 'eps'

		if command_line:
			################################
			# Run an external command line #
			################################
			# Create the environment of variables for the CLI
			# Create the CLI to run
			cli = genutils.expand_env(command_line, environment)
			
			# Run the cli
			if logging.getLogger().isEnabledFor(logging.DEBUG):
				sh_cmd = list()
				for e in cli:
					sh_cmd.append(shlex.quote(e))
				logging.debug(T("Run: %s") % ' '.join(sh_cmd))
			out = subprocess.Popen(cli, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			sout, serr = out.communicate()
			if out.returncode != 0:
				errmsg = T("%s\nReturn code: %d") % ((serr or ''), out.returncode)
				if fail_on_error:
					raise TranslatorError(errmsg)
				else:
					logging.error(errmsg)
					return None
			return out_file
		elif embedded_function:
			#########################
			# Run the embedded code #
			#########################
			interpreter = translator.get_embedded_function_interpreter()
			if not interpreter:
				interpreter = translator.configuration.python_interpreter
			else:
				interpreter = interpreter.lower()
			if interpreter == translator.configuration.python_interpreter:
				environment['runner'] = self
			environment['python_script_dependencies'] = translator.get_python_dependencies()
			environment['global_configuration'] = translator.configuration

			exec_env : dict[str,Any] = {
				'interpreter_object': None, 
				'global_configuration': translator.configuration,
			}

			if translator.configuration is None:
				raise Exception('No configuration specification')
			
			package_name = "autolatex2.translator.interpreters." + interpreter + "interpreter"
			if import_lib_util.find_spec(package_name) is None:
				m = re.match(r'^(.*?)[0-9]+$',  interpreter)
				if m:
					package_name = "autolatex2.translator.interpreters." + m.group(1) + "interpreter"
			exec("from " + package_name + " import TranslatorInterpreter\n"
					"interpreter_object = TranslatorInterpreter(global_configuration)",  None, exec_env)

			if not exec_env['interpreter_object'].runnable:
				errmsg = T("Cannot execute the translator '%s'.") % translator_name
				if fail_on_error:
					raise TranslatorError(errmsg)
				else:
					logging.error(errmsg)
					return None
			
			exec_env['interpreter_object'].global_variables.update(environment)
			interpreter_output = exec_env['interpreter_object'].run(embedded_function)
			if interpreter_output.exception is not None or interpreter_output.return_code != 0:
				errmsg = T("%s\nReturn code: %s") % ((interpreter_output.error_output or ''), interpreter_output.return_code)
				if fail_on_error:
					raise(TranslatorError(errmsg))
				else:
					logging.error(errmsg)
					return None

			return out_file
		else:
			errmsg = T("Unable to find the method of translation for '%s'.") % translator_name
			if fail_on_error:
				raise TranslatorError(errmsg)
			else:
				logging.error(errmsg)
				return None

