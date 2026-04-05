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
from argparse import Namespace
from collections import deque
from dataclasses import field
from dataclasses import dataclass
from enum import IntEnum, unique
from typing import override

from sortedcontainers import SortedSet

from autolatex2.cli.abstract_actions import AbstractMakerAction
from autolatex2.make.filedescription import FileDescription
from autolatex2.tex.utils import FileType
from autolatex2.utils.extprint import eprint
import autolatex2.utils.utilfunctions as genutils
from autolatex2.utils.i18n import T

@unique
class _DependencyStatus(IntEnum):
	"""
	Status of a node during DFS traversal
	"""
	UNVISITED = 0
	VISITING = 1
	VISITED = 2


@dataclass
class _TreeNode:
	"""
	Node in the dependency tree.
	"""
	filename: str
	timestamp : float | None
	dependencies : list['_TreeNode'] = field(default_factory=list)
	depth: int = 0
	is_cycle: bool = False
	problem: str | None = None
	is_problem: str | None = None
	is_obsolete : bool = False


class _DependencyTreeBuilder:
	"""
	Builds a dependency tree from a dictionary of file descriptions
	"""

	def __init__(self, dependencies : dict[str, FileDescription]):
		"""
        Initialize the dependency tree builder.
		:param dependencies: the list of all known file descriptions.
		:type dependencies: dict[str, FileDescription]
        """
		self._dependencies = dependencies
		self._status : dict[str,_DependencyStatus] = {}
		self._tree_nodes : dict[str,_TreeNode] = {}
		self._cycles: list[list[str]] = []

	# noinspection DuplicatedCode
	def build_tree(self, root_filename: str) -> _TreeNode | None:
		"""
        Build a dependency tree starting from root_filename.
		:param root_filename: The root file to build the tree from.
		:type root_filename: str
		:return: The root of the dependency tree, or None if root not found.
		:rtype: Optional[_TreeNode]
        """
		if root_filename not in self._dependencies:
			raise ValueError(T("Root file '%s' not found in computed dependencies") % root_filename)
		# Reset state
		self._status = {name: _DependencyStatus.UNVISITED for name in self._dependencies}
		self._tree_nodes = {}
		self._cycles = []
		# Build tree with cycle detection
		root_node = self._build_node(root_filename, depth=0, path=[root_filename])
		return root_node

	# noinspection DuplicatedCode
	def _build_node(self, filename: str, depth: int, path: list[str]) -> _TreeNode:
		"""
        Recursively build a tree node with cycle detection.
        :param filename: Current filename to process.
        :type filename: str
        :param depth: Current depth in the tree.
        :type depth: int
        :param path: Current path for cycle detection.
        :type path: list[str]
		:return: Node representing this file
		:rtype: _TreeNode
        """
		# Check for cycles
		if self._status.get(filename) == _DependencyStatus.VISITING:
			# Cycle detected
			cycle_start = path.index(filename)
			cycle = path[cycle_start:] + [filename]
			self._cycles.append(cycle)

			# Create a node marking the cycle
			node = _TreeNode(
				filename=filename,
				timestamp=genutils.get_file_last_change(filename),
				dependencies=[],
				depth=depth,
				is_cycle=True,
			)
			self._tree_nodes[filename] = node
			return node

		# If already processed and not a cycle, return cached node
		if filename in self._tree_nodes:
			return self._tree_nodes[filename]

		# Mark as visiting
		self._status[filename] = _DependencyStatus.VISITING

		# Get file description
		file_desc = self._dependencies[filename]

		# Create node
		node = _TreeNode(
			filename=filename,
			timestamp=genutils.get_file_last_change(filename),
			dependencies=[],
			depth=depth
		)

		# Cache node before processing dependencies (handles self-references)
		self._tree_nodes[filename] = node

		# Process dependencies
		seen_deps: set[str] = set()  # Track to avoid duplicates at same level

		node.is_obsolete = node.timestamp is None

		for dep in file_desc.dependencies:
			if dep not in self._dependencies:
				# Dependency not found - create a placeholder node
				missing_node = _TreeNode(
					filename=dep,
					timestamp=genutils.get_file_last_change(dep),
					dependencies=[],
					depth=depth + 1,
					is_cycle=False,
					problem=T('not defined in file descriptions')
				)
				node.dependencies.append(missing_node)
				continue

			# Skip if already processed at this level (duplicate)
			if dep in seen_deps:
				continue
			seen_deps.add(dep)

			# Recursively build dependency node
			dep_node = self._build_node(dep, depth + 1, path + [filename])
			node.dependencies.append(dep_node)

			# Propagate the timestamp if parent and child are source types
			if (file_desc.file_type.is_source_type() and self._dependencies[dep].file_type.is_source_type() \
				and self._is_obsolete_timestamp(node.timestamp, dep_node.timestamp)):
				node.timestamp = dep_node.timestamp
				dep_node.is_obsolete = False
			# Determine if the current is obsolete
			elif not node.is_obsolete and (dep_node.is_obsolete or self._is_obsolete_timestamp(node.timestamp, dep_node.timestamp)):
				node.is_obsolete = True

		# Mark as visited
		self._status[filename] = _DependencyStatus.VISITED

		return node

	# noinspection PyMethodMayBeStatic
	def _is_obsolete_timestamp(self, parent_timestamp : float | None, child_timestamp : float | None) -> bool:
		if parent_timestamp is None or child_timestamp is None:
			return True
		assert parent_timestamp is not None and child_timestamp is not None
		return parent_timestamp < child_timestamp

	def get_cycles(self) -> list[list[str]]:
		"""
		Return all detected cycles in the dependency graph.
		"""
		return self._cycles

	def has_cycles(self) -> bool:
		"""
		Check if any cycles were detected.
		"""
		return len(self._cycles) > 0


class MakerAction(AbstractMakerAction):

	id : str = 'showdependencies'

	alias : list[str] = [ 'dependencies', 'dependency', 'deps' ]

	help : str = T('Show the dependency relationships of files from the main LaTeX document.')

	# noinspection DuplicatedCode
	@override
	def _add_command_cli_arguments(self, command_name : str, command_help : str | None,
								   command_aliases : list[str] | None):
		"""
		Callback for creating the CLI arguments (positional and optional).
		:param command_name: The name of the command.
		:type command_name: str
		:param command_help: The help text for the command.
		:type command_help: str | None
		"""
		super()._add_command_cli_arguments(command_name, command_help, command_aliases)

		self.parse_cli.add_argument('--noauxfile',
			action='store_true',
			help=T('Don\'t read the auxiliary files for building the dependency tree'))

		self.parse_cli.add_argument('--times',
			action='store_true',
			help=T('Show the change times for each file'))

		self.parse_cli.add_argument('--list',
			action='store_true',
			help=T('Show the dependency as a list'))

	# noinspection DuplicatedCode
	@override
	def run(self, cli_arguments : Namespace) -> bool:
		"""
		Callback for running the command.
		:param cli_arguments: the successfully parsed CLI arguments.
		:type cli_arguments: Namespace
		:return: True if the process could continue. False if an error occurred and the process should stop.
		:rtype: bool
		"""
		try:
			maker = self._internal_create_maker()
			for root_file in maker.root_files:
				dependencies = maker.compute_dependencies(root_file, not cli_arguments.noauxfile)
				if cli_arguments.list:
					deps, problems = self._build_dependency_set(dependencies)
					self._show_dependency_set(deps, problems)
				else:
					deps = self._build_dependency_tree(dependencies)
					self._show_dependency_tree(deps, cli_arguments.times)
		except BaseException as ex:
			logging.error(str(ex))
			return False
		return True

	# noinspection PyMethodMayBeStatic,DuplicatedCode
	def _build_dependency_set(self, dependencies : tuple[str, dict[str, FileDescription]]) -> tuple[SortedSet,dict[str,str]]:
		"""
		Build the set of all the files that are required for building the document.
		:param dependencies: the detailed description of the dependency relationships per file.
		:type dependencies: tuple[str, dict[str, FileDescription]]
		:return: the set of filenames of the dependencies.
		:rtype: tuple[str,dict[str,FileDescription]]
		"""
		problems : dict[str,str] = dict()
		deps = SortedSet()
		queue = deque()
		queue.append(dependencies[0])
		while queue:
			current_file = queue.popleft()
			if current_file in dependencies[1]:
				if current_file not in deps:
					description = dependencies[1][current_file]
					deps.add(description.output_filename)
					for d in description.dependencies:
						queue.append(d)
			else:
				problems[current_file] = T('not defined in file descriptions')
		return deps, problems

	# noinspection PyMethodMayBeStatic
	def _build_dependency_tree(self, dependencies : tuple[str, dict[str, FileDescription]]) -> _TreeNode | None:
		"""
		Build the dependency tree of all the files that are required for building the document.
		:param dependencies: the detailed description of the dependency relationships per file. The first element of
		 the tuple is the root file in the dependency tree.
		:type dependencies: tuple[str, dict[str, FileDescription]]
		:return: the root of the dependency tree
		:rtype: Optional[_TreeNode]
		"""
		builder = _DependencyTreeBuilder(dependencies[1])
		return builder.build_tree(dependencies[0])

	# noinspection PyMethodMayBeStatic
	def _show_dependency_set(self, dependencies : SortedSet, problems : dict[str,str]):
		"""
		Show the set of all the files that are required for building the document.
		:param dependencies: the set of filenames of the dependencies.
		:type dependencies: set[str]
		:param problems: the set of problems that were found for the dependencies.
		:type problems: dict[str,str]
		"""
		for dep in dependencies:
			error_marker = f" ❌ {problems[dep]}" if dep in problems and problems[dep] else ""
			obsolete = " ⌛" if dep.is_obsolete else ""
			eprint(f"{dep}{obsolete}{error_marker}")

	# noinspection PyMethodMayBeStatic
	def _show_dependency_tree(self, node : _TreeNode|None, show_timestamps : bool, indent: str = "",
			   is_last: bool = True):
		"""
		Show the provided dependency tree.
		:param node: the node to show.
		:type node: _TreeNode | None
		:param indent: Current indentation string.
		:type indent: str
		:param is_last: Whether this is the last child.
		:type is_last: bool
		"""
		if node is not None:
			# Print current node
			marker = "└── " if is_last else "├── "
			cycle_marker = " 🔄" if node.is_cycle else ""
			error_marker = f" ❌ {node.problem}" if node.problem is not None else ""
			timestamp = f" ({node.timestamp})" if show_timestamps else ""
			obsolete = " ⌛" if node.is_obsolete else ""
			eprint(f"{indent}{marker}{node.filename}{obsolete}{timestamp}{cycle_marker}{error_marker}")

			# Process children
			if node.dependencies:
				child_indent = indent + ("    " if is_last else "│   ")
				for i, child in enumerate(node.dependencies):
					is_last_child = (i == len(node.dependencies) - 1)
					self._show_dependency_tree(child, show_timestamps, child_indent, is_last_child)
