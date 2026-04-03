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
import re
import subprocess
import sys
from typing import override

from setuptools import setup, find_packages
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


def is_unix():
	return platform.system() in ('Linux', 'Darwin', 'FreeBSD', 'OpenBSD', 'NetBSD')



class PostBuildCommand(build_py):
	"""
	Custom build process that update the date in the STY files, ensure the version number in the root VERSION
	file corresponds to those from src/, generate the manual pages.
	"""
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.unixman = False
		self.install_layout = 'deb'

	@override
	def initialize_options(self):
		super().initialize_options()
		self.unixman = is_unix()

	@override
	def finalize_options(self):
		super().finalize_options()
		if self.unixman is None:
			self.unixman = is_unix()

	@override
	def run(self):
		print("Updating the LaTeX sty file")
		PostBuildCommand.update_sty_file()
		print("Updating the LaTeX Beamer sty file")
		PostBuildCommand.update_beamer_sty_file()
		print("Updating the VERSION file")
		self.update_version_file()
		super().run()
		if self.unixman:
			print("Building manual page")
			PostBuildCommand.pod2man()

	@staticmethod
	def pod2man(in_pod : str = None, out_man : str = None, out_gz : str = None):
		if not in_pod:
			in_pod = os.path.join(CURRENT_DIR, 'docs', 'autolatex.pod')
		if not out_man:
			out_man = os.path.join(CURRENT_DIR, 'build', 'man', 'man1', 'autolatex.1')
		if not out_gz:
			out_gz = out_man + '.gz' #usr/share/man/man1
		print("\tcreating %s and %s" % (out_man,out_gz))
		os.makedirs(os.path.dirname(out_man), exist_ok=True)
		rc = subprocess.call(['pod2man', '--center=AutoLaTeX', '--name=' + PROGRAM_NAME, '--release=' + PROGRAM_VERSION, in_pod, out_man])
		if rc == 0:
			with open(out_man, 'rb') as f_in:
				with gzip.open(out_gz, 'wb') as f_out:
					shutil.copyfileobj(f_in, f_out)
		else:
			sys.exit(rc)

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
		now = datetime.now()
		year = int(now.year)
		month = int(now.month)
		day = int(now.day)
		content = re.sub('autolatex@package@ver\\{[^}]+}',
						 'autolatex@package@ver{%s/%s/%s}' % (f'{year:04d}', f'{month:02d}', f'{day:02d}'),
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
		now = datetime.now()
		year = int(now.year)
		month = int(now.month)
		day = int(now.day)
		content = re.sub('autolatexbeamer@package@ver\\{[^}]+}',
						 'autolatexbeamer@package@ver{%s/%s/%s}' % (f'{year:04d}', f'{month:02d}', f'{day:02d}'),
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

		pod_path = os.path.join(str(path), 'share', 'doc', 'autolatex-base')
		pod_path = os.path.normpath(pod_path)

		man_path = os.path.join(str(path), 'share', 'man', 'man1')
		man_path = os.path.normpath(man_path)

		src_pod_file = os.path.join(CURRENT_DIR, 'docs', 'autolatex.pod')
		pod_file = os.path.join(pod_path, 'autolatex.pod')
		if os.path.isfile(src_pod_file):
			os.makedirs(os.path.dirname(pod_file), exist_ok=True)
			self.copy_file(src_pod_file, pod_file, level=self.verbose)

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


# Setup
setup(
	cmdclass ={
		'build_py': PostBuildCommand,
		'install': PostInstallCommand,
		'sdist': CustomSourceDistributionCommand,
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
