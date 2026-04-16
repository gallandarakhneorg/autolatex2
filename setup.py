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

import shutil
from datetime import datetime
import logging
import gzip
import platform
import os
import glob
import re
import subprocess
import sys
from typing import override

from setuptools import setup, find_packages, Command
from setuptools.command.build_py import build_py
from setuptools.command.install import install
from setuptools.command.sdist import sdist as sourcedist

# Read the program information
CURRENT_DIR = os.path.normpath(os.path.dirname(__file__))
with open(os.path.join(CURRENT_DIR, 'src', 'autolatex2', 'VERSION'), 'r', encoding='utf-8') as fh:
	line = fh.read()
	m = re.match('^([^ ]+)\\s+(.*?)\\s*$', line)
	if m:
		PROGRAM_NAME = m.group(1)
		PROGRAM_VERSION = m.group(2)
	else:
		raise Exception("Cannot read VERSION file")

now = datetime.now()
COPYRIGHT_YEAR = str(now.year)
PUB_YEAR = int(now.year)
PUB_MONTH = int(now.month)
PUB_DAY = int(now.day)
PUB_DATE_SLASH = f'{PUB_YEAR:04d}/{PUB_MONTH:02d}/{PUB_DAY:02d}'
PUB_DATE_DASH = f'{PUB_YEAR:04d}-{PUB_MONTH:02d}-{PUB_DAY:02d}'


def is_unix():
	return platform.system() in ('Linux', 'Darwin', 'FreeBSD', 'OpenBSD', 'NetBSD')


def has_pandoc():
	if shutil.which('pandoc'):
		return True
	return False


class PostBuildCommand(build_py):
	"""
	Custom build process that update the date in the STY files, ensure the version number in the root VERSION
	file corresponds to those from src/, generate the manual pages.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.isunix = None
		self.unixman = None
		self.pandoc = None
		self.install_layout = 'deb'

	@override
	def initialize_options(self):
		super().initialize_options()
		self.isunix = is_unix()
		self.unixman = self.isunix
		self.pandoc = has_pandoc()

	@override
	def finalize_options(self):
		super().finalize_options()
		if self.isunix is None:
			self.isunix = is_unix()
		if self.unixman is None:
			self.unixman = self.isunix
		if self.pandoc is None:
			self.pandoc = has_pandoc()

	@staticmethod
	def replace_variables_in_file(input_file : str, **variables : str) -> str:
		"""
		Replace the variables in the input file. A variable is represented by "{{ variable_name }}" in
		the input file.
		:param input_file: path of the input file.
		:param variables: mapping from variable names to their values.
		:return: the path to the result file.
		"""
		with open(input_file, 'r') as f:
			content = f.read()
		pattern = r'\{\{\s*(\w+)\s*\}\}'
		def replacer(match):
			key = match.group(1)
			if key in variables:
				return str(variables[key])
			else:
				return match.group(0)
		content = re.sub(pattern, replacer, content)
		filtered_file = os.path.join(CURRENT_DIR, 'filtered_markdown.md')
		with open(filtered_file, 'w') as f:
			f.write(content)
		return filtered_file

	@staticmethod
	def replace_standard_variables_in_file(input_file : str) -> str:
		"""
		Replace the variables in the input file with the standard variables.
		:param input_file: path of the input file.
		:return: the path to the result file.
		"""
		return PostBuildCommand.replace_variables_in_file(input_file,
		                                                  python_version='3.12',
		                                                  program_name=f'{PROGRAM_NAME}',
		                                                  readable_name='AutoLaTeX',
		                                                  program_version=f'{PROGRAM_VERSION}',
														  pub_date=f'{PUB_DATE_DASH}',
		                                                  copyright_year=f'{COPYRIGHT_YEAR}')

	@override
	def run(self):
		print("Updating the LaTeX sty file")
		PostBuildCommand.update_sty_file()
		print("Updating the LaTeX Beamer sty file")
		PostBuildCommand.update_beamer_sty_file()
		print("Updating the VERSION file")
		self.update_version_file()
		super().run()
		print("Building final Markdown documentation")
		PostBuildCommand.md2md()
		if self.pandoc:
			print("Refreshing README")
			PostBuildCommand.md2readme()
		else:
			print("WARN: Skipping README updating because 'pandoc' cannot be found")
		if self.pandoc:
			print("Building ROFF man page")
			PostBuildCommand.md2man()
		else:
			print("WARN: Skipping ROFF man page creation because 'pandoc' cannot be found")
		if self.pandoc:
			print("Building PDF documentation")
			PostBuildCommand.md2pdf()
		else:
			print("WARN: Skipping PDF creation because 'pandoc' cannot be found")
		if self.isunix:
			PostBuildCommand.create_development_launcher()


	@staticmethod
	def md2md(in_md : str = None, out_md : str = None):
		if not in_md:
			in_md = os.path.join(CURRENT_DIR, 'docs', 'autolatex.md')
		if not out_md:
			out_md = os.path.join(CURRENT_DIR, 'build', 'doc', 'autolatex-base', 'autolatex.md')
		os.makedirs(os.path.dirname(out_md), exist_ok=True)
		in_filtered = PostBuildCommand.replace_standard_variables_in_file(in_md)
		try:
			shutil.copyfile(in_filtered, out_md)
		finally:
			os.unlink(in_filtered)


	@staticmethod
	def md2man(in_md : str = None, out_man : str = None, out_gz : str = None):
		program = shutil.which('pandoc')
		if program:
			if not in_md:
				in_md = os.path.join(CURRENT_DIR, 'docs', 'autolatex.md')
			if not out_man:
				out_man = os.path.join(CURRENT_DIR, 'build', 'man', 'man1', 'autolatex.1')
			if not out_gz:
				out_gz = out_man + '.gz' #usr/share/man/man1
			print("\tcreating %s and %s" % (out_man, out_gz))
			os.makedirs(os.path.dirname(out_man), exist_ok=True)
			in_filtered = PostBuildCommand.replace_standard_variables_in_file(in_md)
			try:
				rc = subprocess.call([program, in_filtered,
									  '-s',
									  '-t', 'man',
									  '-o', out_man,
									  '--variable', f'title={PROGRAM_NAME}',
									  '--variable', 'section=1',
									  '--variable', 'header=AutoLaTeX',
									  '--variable', f'footer={PROGRAM_VERSION}'])
			finally:
				os.unlink(in_filtered)
			if rc == 0:
				with open(out_man, 'rb') as f_in:
					with gzip.open(out_gz, 'wb') as f_out:
						shutil.copyfileobj(f_in, f_out)
			else:
				sys.exit(rc)
		else:
			print("WARNING: pandoc cannot be find in PATH. Skipping the generation of the ROFF man page")

	@staticmethod
	def md2pdf(in_md : str = None, out_pdf : str = None):
		program0 = shutil.which('pandoc')
		if program0:
			program1 = shutil.which('libreoffice')
			if program1:
				if not in_md:
					in_md = os.path.join(CURRENT_DIR, 'docs', 'autolatex.md')
				if not out_pdf:
					out_pdf = os.path.join(CURRENT_DIR, 'build', 'doc', 'autolatex-base', 'autolatex.pdf')
				out_pdf_basename, out_pdf_ext = os.path.splitext(out_pdf)
				out_odt = out_pdf_basename + '.odt'
				os.makedirs(os.path.dirname(out_odt), exist_ok=True)
				print("\tgenerating ODT in %s" % out_odt)
				in_filtered = PostBuildCommand.replace_standard_variables_in_file(in_md)
				try:
					rc = subprocess.call([program0, in_filtered,
										  '-s',
										  '-t', 'odt',
										  '-o', out_odt])
				finally:
					os.unlink(in_filtered)
				if rc == 0:
					try:
						rc = subprocess.call([program1,
											  '--headless',
											  '--nologo',
											  '--convert-to', 'pdf',
											  '--outdir', os.path.dirname(out_pdf),
											  out_odt])
						if rc != 0:
							sys.exit(rc)
					finally:
						os.unlink(out_odt)
				else:
					sys.exit(rc)
			else:
				print("WARNING: libreoffice cannot be find in PATH. Skipping the generation of the PDF documentation")
		else:
			print("WARNING: pandoc cannot be find in PATH. Skipping the generation of the ODT/PDF documentation")

	@staticmethod
	def md2readme(in_md : str = None, out_readme : str = None):
		program = shutil.which('pandoc')
		if program:
			if not in_md:
				in_md = os.path.join(CURRENT_DIR, 'docs', 'autolatex.md')
			if not out_readme:
				out_readme = os.path.join(CURRENT_DIR, 'README')
			in_filtered = PostBuildCommand.replace_standard_variables_in_file(in_md)
			try:
				rc = subprocess.call([program, in_filtered,
					'-s',
					'-t', 'plain',
					'-o', out_readme])
				if rc != 0:
					sys.exit(rc)
			finally:
				os.unlink(in_filtered)
		else:
			print("WARNING: pandoc cannot be find in PATH. Skipping the refreshing of README")

	# noinspection DuplicatedCode
	@staticmethod
	def update_sty_file(in_sty: str = None, out_sty: str = None):
		if not in_sty:
			in_sty = os.path.join(CURRENT_DIR, 'src', 'autolatex2', 'tex', 'autolatex.sty')
		if not out_sty:
			out_sty = os.path.join(CURRENT_DIR, 'src', 'autolatex2', 'tex', 'autolatex.sty')
		print("\treading %s" % in_sty)
		with open(in_sty, 'rt') as f_in:
			content = f_in.read()
		content = re.sub('autolatex@package@ver\\{[^}]+}',
						 'autolatex@package@ver{%s}' % PUB_DATE_SLASH,
						 content, re.DOTALL)
		content = re.sub('autolatexversion\\{[^}]+}',
						 'autolatexversion{%s}' % str(PROGRAM_VERSION),
						 content, re.DOTALL)
		print("\twriting %s" % out_sty)
		with open(out_sty, 'wt') as f_out:
			f_out.write(content)

	# noinspection DuplicatedCode
	@staticmethod
	def update_beamer_sty_file(in_sty: str = None, out_sty: str = None):
		if not in_sty:
			in_sty = os.path.join(CURRENT_DIR, 'src', 'autolatex2', 'tex', 'autolatex-beamer.sty')
		if not out_sty:
			out_sty = os.path.join(CURRENT_DIR, 'src', 'autolatex2', 'tex', 'autolatex-beamer.sty')
		print("\treading %s" % in_sty)
		with open(in_sty, 'rt') as f_in:
			content = f_in.read()
		content = re.sub('autolatexbeamer@package@ver\\{[^}]+}',
						 'autolatexbeamer@package@ver{%s}' % PUB_DATE_SLASH,
						 content, re.DOTALL)
		print("\twriting %s" % out_sty)
		with open(out_sty, 'wt') as f_out:
			f_out.write(content)

	def update_version_file(self, in_version: str = None, out_version: str = None):
		if not in_version:
			in_version = os.path.join(CURRENT_DIR, 'src', 'autolatex2', 'VERSION')
		if not out_version:
			out_version = os.path.join(CURRENT_DIR, 'VERSION')
		print("\tcopying %s to %s" % (in_version, out_version))
		self.copy_file(in_version, out_version, level=self.verbose)

	@staticmethod
	def create_development_launcher():
		bash_code = "#!/usr/bin/env bash\nDIR=`dirname \"$0\"`\nPYTHONPATH=\"$DIR/src\" exec python3 -B -m autolatex2.cli.autolatex \"$@\""
		bash_script = os.path.join(CURRENT_DIR, 'autolatex.sh')
		with open(bash_script, 'wt') as f_out:
			f_out.write(bash_code)

class PostInstallCommand(install):
	"""
	Custom installation process that install the manual pages.
	"""

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.unixman = True
		self.is_local_layout = True
		# The following attributes correspond to CLI options
		self.install_layout = 'deb'
		self.verbose = 1

	@override
	def initialize_options(self):
		super().initialize_options()
		self.unixman = is_unix()

	@override
	def finalize_options(self):
		super().finalize_options()
		layout = self.install_layout
		if layout is not None:
			self.is_local_layout = str(layout) != 'deb'
		else:
			self.is_local_layout = True
		if self.unixman is None:
			self.unixman = is_unix()

	@override
	def run(self):
		super().run()
		if self.unixman:
			print("Installing manual page")
			self.install_man()

	def install_man(self):
		if self.root:
			pfx = self.prefix[1:] if self.prefix and str(self.prefix).startswith(os.path.sep) else self.prefix
			path = os.path.join(self.root, str(pfx))
		else:
			path = self.prefix
		if self.is_local_layout:
			path = os.path.join(str(path), 'local')

		doc_md_path = os.path.join(str(path), 'share', 'doc', 'autolatex-base')
		doc_md_path = os.path.normpath(doc_md_path)

		man_path = os.path.join(str(path), 'share', 'man', 'man1')
		man_path = os.path.normpath(man_path)

		src_doc_md_file = os.path.join(CURRENT_DIR, 'docs', 'autolatex.md')
		doc_md_file = os.path.join(doc_md_path, 'autolatex.md')
		if os.path.isfile(src_doc_md_file):
			os.makedirs(os.path.dirname(doc_md_file), exist_ok=True)
			self.copy_file(src_doc_md_file, doc_md_file, level=self.verbose)

		src_mangz_file = os.path.join(CURRENT_DIR, 'build', 'man', 'man1', 'autolatex.1.gz')
		mangz_file = os.path.join(man_path, 'autolatex.1.gz')
		if os.path.isfile(src_mangz_file):
			os.makedirs(os.path.dirname(mangz_file), exist_ok=True)
			self.copy_file(src_mangz_file, mangz_file, level=self.verbose)


class CustomSourceDistributionCommand(sourcedist):
	"""
	Custom source distribution building that renames the root directory inside the archive in order to be
	compliant with the CTAN standards.
	"""

	DELETION_CANDIDATES = [
		os.path.join('src', 'autolatex.egg-info', 'dependency_links.txt')
	]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def make_distribution(self):
		"""
		Override the distribution creation to use a custom base directory name.
		"""
		with self._remove_os_link():
			# Set the desired name for the root directory inside the archive
			base_dir = PROGRAM_NAME
			full_base_dir = self.distribution.get_fullname()
			full_base_name = os.path.join(self.dist_dir, full_base_dir)

			logging.warning("CTAN standards: use base directory name '%s'" % base_dir)

			self.make_release_tree(base_dir, self.filelist.files)

			archive_files = []
			# Ensure tar format is processed last (to avoid accidental overwrites)
			if 'tar' in self.formats:
				self.formats.append(self.formats.pop(self.formats.index('tar')))

			# CTAN standard: Remove empty files from the source archive
			for deletion_candidate in CustomSourceDistributionCommand.DELETION_CANDIDATES:
				if os.path.isfile(deletion_candidate) and os.path.getsize(deletion_candidate) <= 1: # 1 byte is assumed to be empty
					logging.warning("CTAN standards: deleting empty %s" % deletion_candidate)
					full_path = deletion_candidate
					if not os.path.isabs(full_path):
						full_path = os.path.join(os.getcwd(), base_dir, full_path)
					#logging.warning("CTAN standards: %s" % full_path)
					os.unlink(full_path)

			for fmt in self.formats:
				file = self.make_archive(
					full_base_name, fmt, base_dir=base_dir, owner=self.owner, group=self.group
				)
				archive_files.append(file)
				self.distribution.dist_files.append(('sdist', '', file))

			self.archive_files = archive_files

			if not self.keep_temp:
				shutil.rmtree(base_dir, ignore_errors=True)


class CustomCleanCommand(Command):
	"""
	Custom clean command to tidy up the project root.
	"""

	user_options = [
		('all', 'a', 'Remove all temporary files, including Python cache files and extra folders'),
	]

	def initialize_options(self):
		self.all = False   # default value

	def finalize_options(self):
		pass

	def run(self):
		# The base build directories setuptools usually creates
		dirs_to_clean = [
			'build',
			'dist',
			'**/*.egg-info',
			'**/__pycache__',
		]

		# Custom files and directories to clean
		extra_paths = [
			'autolatex.sh',
			'filtered_markdown.md',
			'bin',
			'autolatex_*.dsc',
			'autolatex_*.tar.gz',
			'autolatex_*.buildinfo',
			'autolatex_*.changes',
			'autolatex*.deb'
		]

		if self.all:
			all_folders = dirs_to_clean + extra_paths
		else:
			all_folders = dirs_to_clean

		# Remove directories
		for pattern in all_folders:
			# Check if pattern contains a wildcard
			rec = '**' in pattern
			if rec or '*' in pattern:
				#print(f'\tcleaning: {pattern}')
				for path in glob.glob(pattern, recursive=rec):
					self._remove_path(path)
			else:
				self._remove_path(pattern)

	# noinspection PyMethodMayBeStatic
	def _remove_path(self, path):
		"""
		Safely remove a file or directory.
		"""
		try:
			#print(f"Removing: {path}")
			if os.path.isfile(path) or os.path.islink(path):
				os.unlink(path)
				print(f"Removed file: {path}")
			elif os.path.isdir(path):
				shutil.rmtree(path, ignore_errors=True)
				print(f"Removed directory: {path}")
		except Exception as e:
			print(f"Error removing {path}: {e}")


# Setup
setup(
	cmdclass ={
		'build_py': PostBuildCommand,
		'install': PostInstallCommand,
		'sdist': CustomSourceDistributionCommand,
		'clean': CustomCleanCommand,
	},
	name=PROGRAM_NAME,
	version=PROGRAM_VERSION,
	author="Stéphane Galland",
	author_email="galland@arakhne.org",
	description="AutoLaTeX is a tool for managing LaTeX documents",
	url="https://www.arakhne.org/autolatex",
	license='LGPL',
	project_urls={
		"Git": "https://github.com/gallandarakhneorg/autolatex2",
		"Bug Tracker": "https://github.com/gallandarakhneorg/autolatex2/issues",
	},
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: LGPL License",
		"Operating System :: OS Independent",
	],
	python_requires=">=3.12",
	install_requires=[
		"packaging",
		"sortedcontainers",
		"pyyaml",
	],
	package_dir={"":"src"},
	packages=find_packages(where='src'),
	entry_points=dict(
		console_scripts=[
			'autolatex=autolatex2.cli.autolatex:main'
		]
	),
	include_package_data = True,
	package_data={
		"": ["VERSION", "*.ist", "*.cfg", "*.transdef2", "*.sty"],
	},
)
