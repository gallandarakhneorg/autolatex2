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
General utilities.
"""

import glob
import logging
import os
import re
import subprocess
import sys
from typing import TypeVar, Any

from autolatex2.utils.i18n import T

if os.name == 'nt':
	import win32api
	import win32con

def get_java_version():
	"""
	Replies the version of Java environment that is currently installed.
	:return: The version of Java.
	:rtype: tuple
	"""
	try:
		# Run the 'java -version' command
		result = subprocess.run(['java', '-version'],
			stderr=subprocess.PIPE,
			stdout=subprocess.PIPE,
			text=True)
		# The version info is sent to stderr, not stdout
		version_output = result.stderr

		# Parse the version string (example: openjdk version "17.0.1")
		for line in version_output.splitlines():
			m = re.search(r'version "([^"]+?)"', line)
			if m:
				version = m.group(1)
				return tuple(str(version).split('.'))
	except FileNotFoundError:
		pass
	except Exception as e:
		raise e
	return None

def find_file_in_path(filename : str, use_environment_variable : bool = False) -> str | None:
	"""
	Search a file into the "sys.path" (filled with PYTHONPATH) variable.
	:param filename: The relative filename.
	:type filename: str
	:param use_environment_variable: Indicates if the PYTHONPATH environment variable should be preferred to sys.path.
	:type use_environment_variable: bool
	:return: The absolute path of the file, or None if the file was not found.
	:rtype: str
	"""
	if use_environment_variable:
		search_path = os.getenv("PYTHONPATH")
		if search_path:
			elements = search_path.split(os.pathsep)
		else:
			elements = list()
	else:
		elements = sys.path
	for root in elements:
		if not root:
			fn = os.path.join(os.curdir, filename)
		else:
			fn = os.path.join(root, filename)
		fn = os.path.abspath(fn)
		if os.path.exists(fn):
			return fn
	return None

def unlink_pattern(directory : str, file_pattern : str):
	"""
	Unlink all the files into the given directory that has a filename matching the given shell pattern.
	:param directory: The directory to explore.
	:type directory: str
	:param file_pattern: the shell pattern.
	:type file_pattern: str
	"""
	if os.path.isabs(file_pattern):
		pattern = file_pattern
	else:
		pattern = os.path.join(directory, file_pattern)
	file_list = glob.glob(pattern, recursive=False)
	if file_list:
		for file in file_list:
			message = T("Deleting %s") % str(file)
			logging.debug(message)
			unlink(file)

# noinspection PyBroadException
def unlink(name : str):
	"""
	Remove the file. Do not fail if the file does not exist.
	:param name: The filename.
	:type name: str
	"""
	try:
		os.unlink(name)
	except:
		pass

def basename(name : str, *ext : str) -> str:
	"""
	Replies the basename, without the given extensions.
	This function remove the directory name.
	:param name: The filename.
	:type name: str
	:param ext: The extensions to remove.
	:type ext: str
	:return: The name.
	:rtype: str
	"""
	bn = os.path.basename(name)
	for e in ext:
		if isinstance(e, list) or isinstance(e, tuple) or isinstance(e, set):
			for e2 in e:
				if bn.endswith(e2):
					i = len(e2)
					n = bn[0:-i]
					return n
		elif bn.endswith(e):
			i = len(e)
			n = bn[0:-i]
			return n
	return bn

def basename2(name : str, *ext : str) -> str:
	"""
	Replies the basename, without the given extensions.
	This function mimics the 'basename' command on Unix systems.
	This function does not remove the directory part.
	:param name: The filename.
	:type name: str
	:param ext: The extensions to remove.
	:type ext: list[str]
	:return: The name.
	:rtype: str
	"""
	bn = basename(name,  *ext)
	dn = os.path.dirname(name)
	if dn:
		return os.path.join(dn,  bn)
	return bn

def get_filename_extension_from(name : str, *ext : str) -> str|None:
	"""
	Replies the filename extension from the given filename that is one of the provided extensions.
	:param name: The filename.
	:type name: str
	:param ext: The extensions to search for.
	:type ext: list[str]
	:return: The extension, or None if no extension was found.
	:rtype: str|None
	"""
	for extension in ext:
		if name.endswith(extension):
			return extension
	return None


def ensure_filename_extension(name : str, *ext : str) -> str:
	"""
	Ensure that the given filename has the specified file extension. If there is multiple extensions
	provided, then the first one is selected as the reference.
	:param name: The filename.
	:type name: str
	:param ext: The extensions to search for.
	:type ext: list[str]
	:return: The filename with a correct extension.
	:rtype: str
	"""
	for extension in ext:
		if name.endswith(extension):
			return name
	return name + ext[0]


TO = TypeVar('TO')
def first_of(*values : list[TO]) -> TO:
	"""
	Replies the first non-null value in the given values.
	:param values: The array of values.
	:type values: list[T]
	:return: the first non-null value, or None.
	:rtype: T
	"""
	for value in values:
		if value is not None:
			return value
	return None

def is_hidden_file(filename : str) -> bool:
	"""
	Replies if the file with the given name is hidden.
	:param filename: The name of the file.
	:type filename: str
	:return: True if the file is hidden.
	:rtype: bool
	"""
	if os.name == 'nt':
		attribute = win32api.GetFileAttributes(filename)
		return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
	else:
		return filename.startswith('.')


# noinspection PyBroadException
def get_file_last_change(filename : str) -> float | None:
	"""
	Replies the time of the last change on the given file.
	"""
	try:
		t1 = os.path.getmtime(filename)
		t2 = os.path.getctime(filename)
		if t1 is None:
			return t2
		if t2 is None:
			return t1
		return t1 if t1 >= t2 else t2
	except:
		return None

def parse_cli(command_line : str, environment : dict[str,str] = None, exceptions : set[Any] = None, all_protect : bool = False) -> list[str]:
	"""
	Parse the given strings as command lines and extract each component.
	The components are separated by space characters. If you want a
	space character inside a component, you must enclose the component
	with quotes. To have quotes in components, you must protect them
	with the backslash character.
	This function expand the environment variables.
	
	Note: Every parameter that is an associative array is assumed to be an
	environment of variables that should be used prior to <code>os.environ</code> to expand the
	environment variables. The elements in the parameter are treated from the
	first to the last. Each time an environment was found, it is replacing any
	previous additional environment.
	:param command_line: the command line to parse.
	:type command_line: str
	:param environment: a dictionary of environment variables, mapping the variable names to their values.
	:type environment: dict[str,str]
	:param exceptions: The names of the environment variables to not expand.
	:type exceptions: set[Any]
	:param all_protect: Indicates if all arguments are protected.
	:type all_protect: bool
	:return: The CLI elements.
	:rtype: list
	"""
	r = list()
	command_line = command_line.strip()
	if command_line:
		protect = ''
		value = ''
		m = re.match(r'^(.*?)(["\']|\s+|\.|\$[a-zA-Z0-9_]+|\$\{[a-zA-Z0-9_]+})(.*)$', command_line, re.S)
		while m:
			prefix = m.group(1)
			sep = m.group(2)
			command_line = m.group(3)
			value += prefix
			if sep.startswith('\\'):
				value += sep[1:]
			else:
				varname = None
				if sep.startswith('${'):
					varname = sep[2:-1]
				elif sep.startswith('$'):
					varname = sep[1:]
				if varname:
					if all_protect or protect == '\'' or (exceptions and varname in exceptions):
						value += sep
					elif environment and varname in environment:
						value += environment[varname] or ''
					else:
						value += os.environ.get(varname) or ''
				elif sep == '"' or sep == '\'':
					if not protect:
						protect = sep
					elif protect == sep:
						protect = ''
					else:
						value += sep
				elif protect:
					value += sep
				elif value:
					r.append(value)
					value = ''
			m = re.match(r'^(.*?)(["\']|\s+|\.|\$[a-zA-Z0-9_]+|\$\{[a-zA-Z0-9_]+})(.*)$', command_line, re.S)
		if command_line:
			value += command_line
		if value:
			r.append(value)
	return r

def expand_env(command_line : list, environment : dict[str,Any], exceptions : set[str] = None) -> list[str]:
	"""
	Parse the given strings as command lines and extract each component.
	The components are separated by space characters. If you want a
	space character inside a component, you must enclose the component
	with quotes. To have quotes in components, you must protect them
	with the backslash character.
	This function expand the environment variables.
	
	Note: Every parameter that is an associative array is assumed to be an
	environment of variables that should be used prior to <code>os.environ</code> to expand the
	environment variables. The elements in the parameter are treated from the
	first to the last. Each time an environment was found, it is replacing any
	previous additional environment.
	:param command_line: the command line to parse.
	:type command_line: str
	:param environment: a dictionary of environment variables, mapping the variable names to their values.
	:type environment: dict[str,Any]
	:param exceptions: The names of the environment variables to not expand.
	:type exceptions: set
	:return: The CLI elements.
	:rtype: list
	"""
	r = list()
	for element in command_line:
		m = re.match(r'^(.*?)(\\.|\$[a-zA-Z0-9_]+|\$\{[a-zA-Z0-9_]+})(.*)$', element, re.S)
		while m:
			prefix = m.group(1)
			macro = m.group(2)
			rest = m.group(3)
			element = prefix
			if macro.startswith('\\'):
				element += macro[1:]
			else:
				if macro.startswith('${'):
					varname = macro[2:-1]
				else:
					varname = macro[1:]
				if exceptions and varname in exceptions:
					element += macro
				elif environment and varname in environment:
					element += str(environment[varname]) or ''
				else:
					element += os.environ.get(varname) or ''
			element += rest
			m = re.match(r'^(.*?)(\$[a-zA-Z0-9_]+|\$\{[a-zA-Z0-9_]+})(.*)$', element, re.S)
		r.append(element)
	return r

def abs_path(path : str, root : str) -> str:
	"""
	Make the path absolute if not yet.
	:param path: The path to make absolute.
	:type path: str
	:param root: The root folder to use if the path is not absolute.
	:type root: str
	:return: The absolute path.
	:rtype: str
	"""
	if os.path.isabs(path):
		return path
	return os.path.normpath(os.path.join(root, path))

def to_path_list(value : str,  root : str) -> list[str]:
	"""
	Convert a string to list of paths. According to the operating system, the path separator may be ':' or ';'
	:param value: the value to convert.
	:type value: str
	:param root: the root directory to use for making absolute the paths.
	:type root: str
	:return: the list value.
	:rtype: list
	"""
	if value:
		sep = os.pathsep
		paths = list()
		for p in value.split(sep):
			if os.path.isabs(p):
				paths.append(p)
			else:
				if root:
					pp = os.path.normpath(os.path.join(root,  p))
				else:
					pp = os.path.abspath(p)
				paths.append(pp)
		return paths
	return list()
