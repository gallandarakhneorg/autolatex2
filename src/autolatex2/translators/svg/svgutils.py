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

import re
import os
import xml.etree.ElementTree as Xml
from typing import Callable

from mistune.directives import include

from autolatex2.tex.beamer import Beamer
from autolatex2.utils.runner import Runner, ScriptOutput
import autolatex2.utils.utilfunctions as genutils
from autolatex2.utils.i18n import T


class SvgUtils:

    @staticmethod
    def create_pdftex_for_layered_svg(svg_file : str,
                                      out_file_with_extension : str,
                                      out_file_without_extension : str,
                                      out_dir : str,
                                      out_extensions : list[str],
                                      pdf_mode : bool,
                                      is_tex_mode : bool,
                                      exporter : Callable[[str, str, str, str | None], ScriptOutput] | None,
                                      extra_parameter : str | None = None):
        """
        Generate the '.pdf_t' file from a SVG that contains layers.
        :param svg_file: the input SVG file.
        :type svg_file: str
        :param out_file_with_extension: the output file with extension.
        :type out_file_with_extension: str
        :param out_file_without_extension: the output file without extension.
        :type out_file_without_extension: str
        :param out_dir: the output directory.
        :type out_dir: str
        :param out_extensions: the output file extensions.
        :type out_extensions: list[str]
        :param pdf_mode: indicates if the generation mode is PDF; Otherwise Postscript.
        :type pdf_mode: bool
        :param is_tex_mode: indicates if the generation mode is for embedded TeX macros.
        :type is_tex_mode: bool
        :param exporter: a lambda that is used for creating the image of a layer. Arguments are:
            * identifier: the identifier of the layer;
            * svg_file: the path of the svg file to read;
            * output_file: the path to the PDF/PS file to create for the layer;
            * extra_param: the extra parameters passed to with function
            The lambda returns the result of the script run.
        :type exporter: Callable[[str,str,str,str|None], ScriptOutput] | None
        :param extra_parameter: any extra parameter value to pass to "pdf_exporter".
        :type extra_parameter: str | None
        """
        if pdf_mode:
            ext1 = '.pdftex_t'
            ext2 = '.pdf'
            ext3 = '.pdf_tex'
        else:
            ext1 = '.pstex_t'
            ext2 = '.eps'
            ext3 = '.ps_tex'

        xml_tree = Xml.parse(svg_file)
        xml_root = xml_tree.getroot()

        image_inclusions = list()

        if re.match('^(?:\\{.*?})?svg$', xml_root.tag, re.S):
            if 'width' in xml_root.attrib:
                width = xml_root.attrib['width'] or '0'
                width = float(re.sub(r'\D+$', '', width))
            else:
                width = 0.0
            if width <= 0.0:
                width = 100.0
            elif width > 1000.0:
                width = 1000.0

            layer_index = 1

            for element in xml_root:
                if (re.match('^(?:\\{.*?})?g$', element.tag, re.S)
                        and '{http://www.inkscape.org/namespaces/inkscape}groupmode' in element.attrib
                        and element.attrib['{http://www.inkscape.org/namespaces/inkscape}groupmode'] == 'layer'
                        and ( 'style' not in element.attrib or element.attrib['style'] != 'display:none')):

                    if ('{http://www.inkscape.org/namespaces/inkscape}label' not in element.attrib
                            or not element.attrib['{http://www.inkscape.org/namespaces/inkscape}label']):
                        label = ''
                    else:
                        label = element.attrib['{http://www.inkscape.org/namespaces/inkscape}label'].strip()

                    if 'id' not in element.attrib or not element.attrib['id']:
                        identifier = ''
                    else:
                        identifier = element.attrib['id'].strip()

                    overlay_spec = Beamer.parse_frames_start(label)
                    if not overlay_spec:
                        overlay_spec = str(layer_index)
                    else:
                        frame_spec, min_frame = overlay_spec
                        overlay_spec = frame_spec
                        layer_index = min_frame

                    output_basename = out_file_without_extension + "_" + identifier
                    figure_file = os.path.join(out_dir, output_basename + ext2)

                    if exporter:
                        assert exporter is not None
                        runner_output = exporter(identifier, svg_file, figure_file, extra_parameter)
                        Runner.check_runner_status(runner_output)

                    if is_tex_mode:
                        includable_file = os.path.join(out_dir, output_basename + ext3)
                    else:
                        includable_file = "%s%s" % (str(output_basename), str(ext2))

                    image_inclusions.append(
                        "\\node<%s> (X) {\\includegraphics[width=%sem]{%s}};%%" % (str(overlay_spec),
                                                                                     str(width),
                                                                                     str(includable_file)))

                    layer_index += 1

        if not image_inclusions:
            raise Exception(T("No layer in the SVG file: %s") % svg_file)

        with open(genutils.basename_with_path(out_file_with_extension, *out_extensions) + ext1, 'wt') as out_file:
            out_file.write("\\begin{tikzpicture}%\n")
            for inclusion in image_inclusions:
                out_file.write(inclusion)
                out_file.write("\n")
            out_file.write("\\end{tikzpicture}%\n")
