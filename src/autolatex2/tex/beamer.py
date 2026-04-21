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
Beamer tools.
"""

import re
import sys

from autolatex2.utils.i18n import T

class Beamer:
	"""
	Tools for LaTeX Beamer.
	"""

	MAX_SLIDE = sys.maxsize



	@staticmethod
	def merge_frame_ranges(ranges : list[range]) -> list[range]:
		"""
        Merge a list of ranges that may overlap or be adjacent.
		:param ranges: list of range objects.
		:rtype ranges: list[range]
        :returns: a new list of merged range objects, sorted by start, with no overlaps.
        Adjacent ranges (e.g., range(1,5) and range(5,10)) are merged into one.
        :rtype: list[range]
        """
		if ranges and len(ranges) > 1:
			# Convert each range to a tuple (start, stop) for easier handling
			intervals = [(r.start, r.stop) for r in ranges]
			# Sort by start, then by stop (though stop isn't strictly needed for sorting)
			intervals.sort(key=lambda x: (x[0], x[1]))

			merged = []
			cur_start, cur_stop = intervals[0]

			for start, stop in intervals[1:]:
				if start <= cur_stop:  # Overlap or adjacent
					if stop > cur_stop:
						cur_stop = stop  # Extend the current merged range
				else:
					# No overlap, store the current merged range and start a new one
					merged.append(range(cur_start, cur_stop))
					cur_start, cur_stop = start, stop

			# Append the last range
			merged.append(range(cur_start, cur_stop))
			return merged
		return ranges


	@staticmethod
	def extract_frames(specification : str) -> list[range]:
		"""
		Analyze the provided string that is a frame specification and extract the sequence of ranges that match.
		This function does not merge adjacent or intersecting ranges.
		:param specification: the frame specification without '<' and '>'.
		:type specification: str
		:return: the sequences of ranges that match.
		:rtype: list[range]
		"""
		sp = specification.strip()
		ranges = []
		if sp:
			parts = [p.strip() for p in sp.split(',') if p.strip()]

			for part in parts:
				if not part:
					# Empty - all slides
					ranges.append(range(1, Beamer.MAX_SLIDE))
				elif '-' not in part:
					# Single slide, e.g. "1"
					try:
						slide = int(part)
					except BaseException:
						raise ValueError(T("Invalid slide number: '%s'") % part)
					ranges.append(range(slide, slide + 1))
				else:
					# Range with possible missing start or end
					start_str, end_str = part.split('-', 1)
					start_str = start_str.strip()
					end_str = end_str.strip()

					# Determine start
					if not start_str:
						start = 1
					else:
						try:
							start = int(start_str)
						except BaseException:
							raise ValueError(T("Invalid start number: '%s'") % start_str)

					# Determine end (inclusive)
					if not end_str:
						end_inclusive = Beamer.MAX_SLIDE - 1
					else:
						try:
							end_inclusive = int(end_str)
						except BaseException:
							raise ValueError(T("Invalid end number: '%s'") % end_str)

					if start > end_inclusive:
						tmp = start
						start = end_inclusive
						end_inclusive = tmp

					# Convert to half-open range
					ranges.append(range(start, end_inclusive + 1))
		if ranges:
			return ranges
		return [ range(1, Beamer.MAX_SLIDE) ]

	@staticmethod
	def extract_and_merge_frames(text : str, prefix : str = '') -> list[list[range]]:
		"""
		Extract from the given text all the frame specifications.
		:param text: the text to parse for searching for '<*>'.
		:type text: str
		:param prefix: the text that is expected to be present before the frame specification, with
		possible spaces in the between.
		:type prefix: str
		:return: the list of the sequences of ranges that match.
		:rtype: list[list[range]]
		"""
		specifications = list()
		for frame_specification in re.finditer(re.escape(prefix) + r'\s*<\s*(.*?)\s*>', text, re.S + re.DOTALL):
			recognized = Beamer.extract_frames(frame_specification.group(1))
			recognized = Beamer.merge_frame_ranges(recognized)
			if recognized:
				specifications.append(recognized)
		return specifications

	@staticmethod
	def __frame_to_str(r : range) -> str:
		if r:
			if r.stop == Beamer.MAX_SLIDE:
				return str(r.start) + '-'
			if r.start + 1 == r.stop:
				return str(r.start)
			return "%d-%d" % (r.start, r.stop - 1)
		return ''

	@staticmethod
	def parse_frames(text : str, prefix : str = '') -> str | None:
		"""
		Extract a single frame specification from the given text.
		:param text: the text to parse for searching for '<*>'.
		:type text: str
		:param prefix: the text that is expected to be present before the frame specification, with
		possible spaces in the between.
		:type prefix: str
		:return: the extracted specification, without the '<' and '>', or None if there is no frame specification.
		:rtype: str | None
		"""
		result = Beamer.parse_frames_start(text, prefix=prefix)
		if result is not None:
			frames, min_value = result
			return frames
		return None

	@staticmethod
	def parse_frames_start(text : str, prefix : str = '') -> tuple[str,int] | None:
		"""
		Extract a single frame specification from the given text and reply this specification and the
		minimum frame number inside.
		:param text: the text to parse for searching for '<*>'.
		:type text: str
		:param prefix: the text that is expected to be present before the frame specification, with
		possible spaces in the between.
		:type prefix: str
		:return: the extracted specification, without the '<' and '>', or None if there is no frame specification.
		:rtype: tuple[str,int] | None
		"""
		m = re.search(re.escape(prefix) + r'<\s*(.*?)\s*>', text, re.S + re.DOTALL)
		if m:
			frame_ranges = Beamer.extract_frames(m.group(1))
			frame_ranges = Beamer.merge_frame_ranges(frame_ranges)
			if frame_ranges:
				res = ''
				min_value = None
				for r in frame_ranges:
					if min_value is None:
						min_value = r.start
					s = Beamer.__frame_to_str(r)
					if s:
						if res:
							res += ','
						res += s
				if res:
					assert min_value is not None
					return res, int(min_value)
		return None
