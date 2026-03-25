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
Abstract implementation of a command and script runner.
"""

import sys
import io
import os
import subprocess
from abc import ABC
from typing import override, Any

from autolatex2.utils.i18n import T

class CommandExecutionError(Exception):

	def __init__(self, return_code : int, msg : str =  None):
		"""
		Construct the exception with the given return code.
		:param return_code: The return code of the executed command.
		:type return_code: int
		:param msg: Error message.
		:type msg: str
		"""
		self.__errno = return_code
		if msg:
			self.__strerror = T('Error during the execution of the command: %s') % msg
		else:
			self.__strerror = T('Error during the execution of the command; return code is %d') % return_code

	@property
	def errno(self) -> int:
		"""
		Replies the number of the error, usually, the return code of executed command.
		:return: The number of the error.
		:rtype: int
		"""
		return self.__errno

	@property
	def strerror(self) -> str:
		"""
		Replies the error message.
		:return: The error message.
		:rtype: str
		"""
		return self.__strerror

	@override
	def __str__(self) -> str:
		return self.strerror


class Runner(ABC):
	"""
	Definition of an abstract implementation of a command and script runner.
	"""

	@staticmethod
	def check_runner_status(standard_error, script_exception : Any, return_code : int = 0):
		"""
		Helper function that generate the correct running behavior regarding the status of a command.
		:param standard_error: Standard error output.
		:param script_exception: Exception during script execution.
		:param return_code: The return code.
		"""
		if script_exception:
			raise script_exception
		elif return_code != 0:
			if standard_error:
				raise Exception(standard_error)
			else:
				raise Exception(T("Error when running the command. Return code is %d") % return_code)

	@staticmethod
	def check_runner_exit_code(code : int):
		"""
		Helper function that generate the correct running behavior regarding the exit code of a command.
		:param code: exit code of a command.
		:type code: int
		"""
		if code != 0:
			raise Exception(T("Errorneous command with exit code %d") % code)

	@staticmethod
	def run_python(script : str, intercept_error : bool = False, local_variables : dict = None, show_script_on_error : bool = True) -> tuple[str,str,Any,int]:
		"""
		Run a Python script in the current process.
		:param script: The Python script to run.
		:type script: str
		:param intercept_error: Indicates if all the exception are intercepted
		                       and put inside the returned value. If False,
		                       the exceptions are not intercepted, and they are
		                       raised by this function. Default value is: False.
		:type intercept_error: bool
		:param local_variables: Dictionnary of the predefined elmeents (imports or local variables)
		:type local_variables: dict
		:param show_script_on_error: Indicates if the script must be output on the standard error output in case of an error. Default is True.
		:type show_script_on_error: bool
		:return: A quadruplet containing the standard output, the
				 error output, the error and the exit code.
		:rtype: (str,str,exception,int)
		"""
		script = script + "\n"
		code_out = io.StringIO()
		code_err = io.StringIO()
		saved_stdout = sys.stdout
		saved_stderr = sys.stderr
		sys.stdout = code_out
		sys.stderr = code_err
		exception = None
		try:
			if intercept_error:
				try:
					exec(script, None, local_variables)
				except BaseException as e:
					exception = e
			else:
				try:
					exec(script, None, local_variables)
				except BaseException as err:
					if show_script_on_error:
						saved_stderr.write(str(err))
						saved_stderr.write(Runner.__format_script(script))
					raise err
		finally:
			sys.stdout = saved_stdout
			sys.stderr = saved_stderr
		sout = code_out.getvalue()
		serr = code_err.getvalue()
		code_out.close()
		code_err.close()
		return sout, serr, exception, 0 if exception is None else 255

	@staticmethod
	def __format_script(script : str) -> str:
		lines = script.split("\n")
		nlines = len(lines)
		pattern = "%d" % nlines
		s = len(pattern)
		pattern = "%" + str(s) + "d %s"
		for i in range(nlines):
			nl = str(pattern) % ((i+1),  lines[i])
			lines[i] = nl
		return "\n" + ("\n".join(lines))


	@staticmethod
	def run_command(*cmd : str) -> tuple[str,str,Any,int]:
		"""
		Run an external command in a subprocess.
		:param cmd: The command line to run.
		:type cmd: list[str]
		:return: A quadruplet containing the standard output, the
				 error output, and the exception, the return code.
		:rtype: tuple[str,str,Any,int]
		"""
		return Runner.run_command_to(None, *cmd)

	@staticmethod
	def run_command_to(redirect_stdout_to : str | None, *cmd : str) -> tuple[str,str,Any,int]:
		"""
		Run an external command in a subprocess.
		:param redirect_stdout_to: Specify the path of the file that must receive the standard output.
		:type redirect_stdout_to: str
		:param cmd: The command line to run.
		:type cmd: list
		:return: A quadruplet containing the standard output, the
				 error output, and the exception, the return code.
		:rtype: tuple[str,str,Any,int]
		"""
		if redirect_stdout_to is not None:
			with open(redirect_stdout_to, "w") as stdout_file:
				out = subprocess.Popen(cmd, shell=False, stdout=stdout_file, stderr=subprocess.PIPE)
				sout, serr = out.communicate()
				return_code = out.returncode
		else:
			out = subprocess.Popen(cmd, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
			sout, serr = out.communicate()
			return_code = out.returncode
		if return_code != 0:
			sex = CommandExecutionError(return_code, str(serr))
		else:
			sex = None
		if sout is not None and isinstance(sout, bytes):
			sout = sout.decode()
		if serr is not None and isinstance(serr, bytes):
			serr = serr.decode()
		return sout or '', serr or '', sex, return_code

	@staticmethod
	def run_command_without_redirect(*cmd : str) -> int:
		"""
		Run an external command in a subprocess without redirecting the input and outputs, and wait for the termination of the subprocess.
		:param cmd: The command line to run.
		:type cmd: list
		:return: exit code
		:rtype: int
		"""
		completed_process = subprocess.run(cmd)
		if completed_process:
			return completed_process.returncode
		return 255

	@staticmethod
	def start_command_without_redirect(*cmd : str) -> bool:
		"""
		Run an external command in a subprocess without redirecting the input and outputs, and do not wait for the termination of the subprocess.
		:param cmd: The command line to run.
		:type cmd: list
		:return: True if the command was launched, False otherwise
		:rtype: bool
		"""
		proc = subprocess.Popen(cmd, shell=False)
		return proc is not None
	
	@staticmethod
	def normalize_command(*cmd : str) -> list[str]:
		"""
		Ensure that the command (the first element of the list) is a command with an absolute path.
		:param cmd: The command line to run.
		:type cmd: str
		:rtype: list[str]
		"""
		c = cmd[0]
		if not os.path.isabs(c):
			for p in os.getenv("PATH").split(os.pathsep):
				fn = os.path.join(p, c)
				if os.path.exists(fn):
					cmd = list(cmd[1:])
					cmd.insert(0, fn)
					return cmd
		return cmd

	@staticmethod
	def run_script(script : str, *interpreter : str) -> tuple[str,str,Any,int]:
		"""
		Run a script with the given interpreter.
		The script is passed to the interpreter on the standard input.
		The command line of the interpreter must be specified in order to
		run the interpreter and read the script from the standard input.
		:param script: The script to run.
		:type script: str
		:param interpreter: The command line of the interpreter to use.
		:type interpreter: str
		:return: A quadruplet containing the standard output, the
				 error output, the exception, the return code.
		:rtype: tuple[str,str,Any,int]
		"""
		out = subprocess.Popen(interpreter, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		sin = script.encode("ascii")
		sout, serr = out.communicate(input = sin)
		if out.returncode != 0:
			sex = CommandExecutionError(out.returncode,  str(serr))
		else:
			sex = None
		if sout is not None and isinstance(sout, bytes):
			sout = sout.decode()
		if serr is not None and isinstance(serr, bytes):
			serr = serr.decode()
		return sout or '', serr or '', sex, out.returncode


