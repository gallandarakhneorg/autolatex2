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

from autolatex2.tex.beamer import Beamer
from autolatex2tests.abstract_base_test import AbstractBaseTest


class TestBeamer(AbstractBaseTest):

	INVALID_SOURCE : str = """
    \\node<-2,1-3> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4325.pdf}};%
    \\node<(-2,4-> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4255.pdf}};%
    
    \\node<1-3,1-3> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4325.pdf}};%
    \\node<(1-3,4-> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4255.pdf}};%
    
    \\node<5-,1-3> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4325.pdf}};%
    \\node<(5-,4-> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4255.pdf}};%
	"""

	VALID_SOURCE: str = """
	    \\node<> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_layer1.pdf}};%
	    \\node<1> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_layer1.pdf}};%
	    \\node<-2> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4185.pdf}};%
	    \\node<1-3> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4325.pdf}};%
	    \\node<4-> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4255.pdf}};%

	    \\node<,> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_layer1.pdf}};%
	    \\node<,1> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_layer1.pdf}};%
	    \\node<,-2> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4185.pdf}};%
	    \\node<,1-3> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4325.pdf}};%
	    \\node<,4-> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4255.pdf}};%

	    \\node<6,> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_layer1.pdf}};%
	    \\node<6,1> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_layer1.pdf}};%
	    \\node<6,-2> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4185.pdf}};%
	    \\node<6,1-3> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4325.pdf}};%
	    \\node<6,4-> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4255.pdf}};%

	    \\node<-2,> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_layer1.pdf}};%
	    \\node<-2,1> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_layer1.pdf}};%
	    \\node<-2,-2> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4185.pdf}};%
	    \\node<-2,1-3> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4325.pdf}};%
	    \\node<-2,4-> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4255.pdf}};%

	    \\node<1-3,> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_layer1.pdf}};%
	    \\node<1-3,1> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_layer1.pdf}};%
	    \\node<1-3,-2> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4185.pdf}};%
	    \\node<1-3,1-3> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4325.pdf}};%
	    \\node<1-3,4-> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4255.pdf}};%

	    \\node<5-,> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_layer1.pdf}};%
	    \\node<5-,1> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_layer1.pdf}};%
	    \\node<5-,-2> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4185.pdf}};%
	    \\node<5-,1-3> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4325.pdf}};%
	    \\node<5-,4-> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4255.pdf}};%

	    \\node<5-,2-4> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4255.pdf}};%
	    \\node<3-18,-2> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4255.pdf}};%
	    \\node<5-8,2-18> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4255.pdf}};%
	    \\node<5-48,18-24> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4255.pdf}};%
	    \\node<48-5> (X) {\\includegraphics[width=289.91769em]{/home/sgalland/git/mas-lesson/chapters/simulation/examples/imgs/auto/jaak_ant_steps_g4255.pdf}};%
		"""

	DATA : list[dict[str,str|list[range]]] = [
		# Set 0
		{
			'i': '',
			'r': [range(1, Beamer.MAX_SLIDE)],
			's': [range(1, Beamer.MAX_SLIDE)],
			'f': '1-',
		},
		{
			'i': '1',
			'r': [range(1, 2)],
			's': [range(1, 2)],
			'f': '1',
		},
		{
			'i': '-2',
			'r': [range(1, 3)],
			's': [range(1, 3)],
			'f': '1-2',
		},
		{
			'i': '1-3',
			'r': [range(1, 4)],
			's': [range(1, 4)],
			'f': '1-3',
		},
		{
			'i': '4-',
			'r': [range(4, Beamer.MAX_SLIDE)],
			's': [range(4, Beamer.MAX_SLIDE)],
			'f': '4-',
		},
		# Set 1
		{
			'i': ',',
			'r': [range(1, Beamer.MAX_SLIDE)],
			's': [range(1, Beamer.MAX_SLIDE)],
			'f': '1-',
		},
		{
			'i': ',1',
			'r': [range(1, 2)],
			's': [range(1, 2)],
			'f': '1',
		},
		{
			'i': ',-2',
			'r': [range(1, 3)],
			's': [range(1, 3)],
			'f': '1-2',
		},
		{
			'i': ',1-3',
			'r': [range(1, 4)],
			's': [range(1, 4)],
			'f': '1-3',
		},
		{
			'i': ',4-',
			'r': [range(4, Beamer.MAX_SLIDE)],
			's': [range(4, Beamer.MAX_SLIDE)],
			'f': '4-',
		},
		# Set 2
		{
			'i': '6,',
			'r': [range(6, 7)],
			's': [range(6, 7)],
			'f': '6',
		},
		{
			'i': '6,1',
			'r': [range(6, 7),range(1, 2)],
			's': [range(1, 2), range(6, 7)],
			'f': '1,6',
		},
		{
			'i': '6,-2',
			'r': [range(6, 7), range(1, 3)],
			's': [range(1, 3), range(6, 7)],
			'f': '1-2,6',
		},
		{
			'i': '6,1-3',
			'r': [range(6, 7), range(1, 4)],
			's': [range(1, 4), range(6, 7)],
			'f': '1-3,6',
		},
		{
			'i': '6,4-',
			'r': [range(6, 7), range(4, Beamer.MAX_SLIDE)],
			's': [range(4, Beamer.MAX_SLIDE)],
			'f': '4-',
		},
		# Set 3
		{
			'i': '-2,',
			'r': [range(1, 3)],
			's': [range(1, 3)],
			'f': '1-2',
		},
		{
			'i': '-2,1',
			'r': [range(1, 3), range(1, 2)],
			's': [range(1, 3)],
			'f': '1-2',
		},
		{
			'i': '-2,-2',
			'r': [range(1, 3), range(1, 3)],
			's': [range(1, 3)],
			'f': '1-2',
		},
		{
			'i': '-2,1-3',
			'r': [range(1, 3), range(1, 4)],
			's': [range(1, 4)],
			'f': '1-3',
		},
		{
			'i': '-2,4-',
			'r': [range(1, 3), range(4, Beamer.MAX_SLIDE)],
			's': [range(1, 3), range(4, Beamer.MAX_SLIDE)],
			'f': '1-2,4-',
		},
		# Set 4
		{
			'i': '1-3,',
			'r': [range(1, 4)],
			's': [range(1, 4)],
			'f': '1-3',
		},
		{
			'i': '1-3,1',
			'r': [range(1, 4), range(1, 2)],
			's': [range(1, 4)],
			'f': '1-3',
		},
		{
			'i': '1-3,-2',
			'r': [range(1, 4), range(1, 3)],
			's': [range(1, 4)],
			'f': '1-3',
		},
		{
			'i': '1-3,1-3',
			'r': [range(1, 4), range(1, 4)],
			's': [range(1, 4)],
			'f': '1-3',
		},
		{
			'i': '1-3,4-',
			'r': [range(1, 4), range(4, Beamer.MAX_SLIDE)],
			's': [range(1, Beamer.MAX_SLIDE)],
			'f': '1-',
		},
		# Set 5
		{
			'i': '5-,',
			'r': [range(5, Beamer.MAX_SLIDE)],
			's': [range(5, Beamer.MAX_SLIDE)],
			'f': '5-',
		},
		{
			'i': '5-,1',
			'r': [range(5, Beamer.MAX_SLIDE), range(1, 2)],
			's': [range(1, 2), range(5, Beamer.MAX_SLIDE)],
			'f': '1,5-',
		},
		{
			'i': '5-,-2',
			'r': [range(5, Beamer.MAX_SLIDE), range(1, 3)],
			's': [range(1, 3), range(5, Beamer.MAX_SLIDE)],
			'f': '1-2,5-',
		},
		{
			'i': '5-,1-3',
			'r': [range(5, Beamer.MAX_SLIDE), range(1, 4)],
			's': [range(1, 4), range(5, Beamer.MAX_SLIDE)],
			'f': '1-3,5-',
		},
		{
			'i': '5-,4-',
			'r': [range(5, Beamer.MAX_SLIDE), range(4, Beamer.MAX_SLIDE)],
			's': [range(4, Beamer.MAX_SLIDE)],
			'f': '4-',
		},
		# Set 6
		{
			'i': '5-,2-4',
			'r': [range(5, Beamer.MAX_SLIDE), range(2, 5)],
			's': [range(2, Beamer.MAX_SLIDE)],
			'f': '2-',
		},
		{
			'i': '3-18,-2',
			'r': [range(3, 19), range(1, 3)],
			's': [range(1, 19)],
			'f': '1-18',
		},
		{
			'i': '5-8,2-18',
			'r': [range(5, 9), range(2, 19)],
			's': [range(2, 19)],
			'f': '2-18',
		},
		{
			'i': '5-48,18-24',
			'r': [range(5, 49), range(18, 25)],
			's': [range(5, 49)],
			'f': '5-48',
		},
		{
			'i': '48-5',
			'r': [range(5, 49)],
			's': [range(5, 49)],
			'f': '5-48',
		},
	]

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)

	def test_extract_frames(self):
		i = 0
		for data in TestBeamer.DATA:
			actual = Beamer.extract_frames(str(data['i']))
			self.assertIsNotNone(actual, f"Expecting a list of ranges for '{data['i']}' at value index {i}")
			self.assertEqual('\n'.join([f"{r.start}-{r.stop}" for r in data['r']]),
							 '\n'.join([f"{r.start}-{r.stop}" for r in actual]),
							 f"Not same raw frame specifications for '{data['i']}' at value index {i}")
			i += 1

	def test_merge_frame_ranges(self):
		i = 0
		for data in TestBeamer.DATA:
			ipt : list[range] = data['r']
			actual = Beamer.merge_frame_ranges(ipt)
			self.assertIsNotNone(actual, f"Expecting a list of ranges for '{data['i']}' at value index {i}")
			self.assertEqual('\n'.join([f"{r.start}-{r.stop}" for r in data['s']]),
							 '\n'.join([f"{r.start}-{r.stop}" for r in actual]),
							 f"Not same raw frame specifications for '{data['i']}' at value index {i}")
			i += 1

	def test_extract_and_merge_frames_valid_source(self):
		actual = Beamer.extract_and_merge_frames(TestBeamer.VALID_SOURCE, prefix='\\node')
		expecteds = TestBeamer.DATA.copy()
		i = 0
		for actual_data in actual:
			expected = expecteds.pop(0)
			self.assertEqual('\n'.join([f"{r.start}-{r.stop}" for r in expected['s']]),
							 '\n'.join([f"{r.start}-{r.stop}" for r in actual_data]),
							 f"Not same raw frame specifications for '{expected['i']}' at value index {i}")
			i += 1

	def test_extract_and_merge_frames_invalid_source(self):
		with self.assertRaises(ValueError):
			Beamer.extract_and_merge_frames(TestBeamer.INVALID_SOURCE, prefix='\\node')

	def test_parse_frames_invalid0(self):
		self.assertIsNone(Beamer.parse_frames('xyz'))

	def test_parse_frames_invalid1(self):
		self.assertIsNone(Beamer.parse_frames(''))

	def test_parse_frames_invalid2(self):
		self.assertIsNone(Beamer.parse_frames('xyz < abc'))

	def test_parse_frames_invalid3(self):
		self.assertIsNone(Beamer.parse_frames('xyz > abc'))

	def test_parse_frames_valids(self):
		i = 0
		for data in TestBeamer.DATA:
			ipt = f'xyz label <{data["i"]}> abc'
			actual = Beamer.parse_frames(ipt)
			self.assertIsNotNone(actual, f"Expecting a range string for '{data['i']}' at value index {i}")
			self.assertEqual(data['f'], actual,
							 f"Not same raw frame specifications for '{data['i']}' at value index {i}")
			i += 1



if __name__ == '__main__':
	unittest.main()

