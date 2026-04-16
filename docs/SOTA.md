# AutoLaTeX and other TeX makers (2026 update)

*2026-04-16*

This document provides an up-to-date comparison of freely accessible and open-source LaTeX build tools. It includes all tools from the original 2016 state of the art, as well as newer tools found on CTAN, GitHub, and other package repositories.

| Maker | Type | Date | Supported Tools | Detect Changes (TeX) | Detect Changes (BibTeX) | Detect Changes (Images) | To PS/PDF/PNG | To TeX | To PSTeX/PDFTeX | Export to Elsevier | Editor plugins |
|-------|------|------|-----------------|----------------------|-------------------------|-------------------------|----------------|--------|-----------------|--------------------|----------------|
| [AutoLaTeX (Python)](https://www.ctan.org/pkg/autolatex) | Python | 2026-04-14 | latex, pdflatex, xelatex, lualatex, bibtex, biber, makeindex, makeglossaries, dvips | ✓ | ✓ | ✓ | asta, asml, dia, dot, fig, ggb, gxl, odg, plot, svg, vsdx, xmi | c/c++, java, matlab, ml, perl, python, ruby, sql, svg layers | fig, plot, dia, svg, svg layers | ✓ | |
| [AutoLaTeX (Perl)](https://www.ctan.org/pkg/autolatex) | Perl | 2022-02-11 | latex, pdflatex, xelatex, lualatex, bibtex, biber, makeindex, makeglossaries, dvips | ✓ | ✓ | ✓ | asta, asml, dia, dot, fig, ggb, gxl, odg, plot, svg, vsdx, xmi | c/c++, java, matlab, ml, perl, python, ruby, sql, svg layers | fig, plot, dia, svg, svg layers | ✓ | Gedit3, Gtk3, Sublime Text 3 (LaTeXTools plugin) |
| [arara](https://ctan.org/pkg/arara) | Java | 2025-06-29 | latex, pdflatex, xelatex, lualatex, bibtex, biber, makeindex, makeglossaries, dvips, dvipdfm, ... (user-defined) | X<sup>1</sup> | X<sup>1</sup> | ? | – | – | – | – | Vim (vimtex), VS Code (LaTeX Workshop), TeXstudio, TeXworks, Emacs (AUCTeX), Sublime Text, IntelliJ IDEA (TeXiFy IDEA) |
| [latexmk](https://www.ctan.org/pkg/latexmk/) | Perl | 2015 | latex, dvips, dvipdf, xelatex, pdflatex, bibtex, makeindex | ✓ | ✓ | ✓ | – | – | – | – | Built‑in (TeXworks, TeXShop, etc.), VS Code, Vim, Emacs, TeXstudio, Overleaf, Sublime Text |
| [Rubber](https://launchpad.net/rubber/) | Python | 2024-12-09 | pdflatex, etex, aleph, omega, vtex, bibtex, makeindex, metapost, dvips, dvipdfm, pdftex | ✓ | ✓ | ✓ | – | – | – | – | None dedicated; integrates with TeX Live, MiKTeX |
| [l3build](https://ctan.org/pkg/l3build) | Lua | 2025-05-08 | (La)TeX, pdfTeX, XeTeX, LuaTeX, etc. (primarily for building LaTeX packages) | ✓ | ✓ | – | – | – | – | – | None dedicated (for package developers) |
| [llmk](https://ctan.org/pkg/llmk) | Lua | 2023-12-26 | latex, pdflatex, xelatex, lualatex, dvips, dvipdfm, bibtex, biber, makeindex | ✓ | ✓ | ✓ | – | – | – | – | None dedicated |
| [latexrun](https://github.com/aclements/latexrun) | Python | 2024-11-08 | pdflatex, xelatex, lualatex, latex, tex, pdftex, biber, makeglossaries | ✓ | ✓ | – | – | – | – | – | None dedicated |
| [texforge](https://github.com/texforge/texforge) | Rust | 2025 (active) | Tectonic engine (LaTeX) | ✓ | – | – | – | – | – | – | None dedicated |
| [Tectonic](https://tectonic-typesetting.github.io/) | Rust | 2023-05-15 | Tectonic engine (self‑contained) | ✓ | – | – | – | – | – | – | None dedicated |
| [clatex](https://github.com/mapk0t/clatex) | Bash | 2025 (active) | latex, pdflatex, bibtex, makeglossaries | ✓ | – | – | – | – | – | – | None dedicated |
| [pandoc](https://pandoc.org/) | Haskell | 2026-03-17 | pdflatex, lualatex, xelatex, etc. (via --pdf-engine) | – | – | – | – | – | – | – | None dedicated |
| [latex-action](https://github.com/xu-cheng/latex-action) | GitHub Action | 2026 (active) | latex, pdflatex, xelatex, lualatex, bibtex, biber, makeindex, etc. (Docker‑based) | ✓ | ✓ | – | – | – | – | – | GitHub Actions |
| [go-make](https://www.ctan.org/pkg/go-make) | Perl | 1993 | latex, dvips, bibtex, makeindex | ✓ | ✓ | ✓ | – | – | – | – | – |
| [latex-make](https://www.ctan.org/pkg/latex-make) | Makefile | 2003 | latex, pdflatex, dvips, ps2pdf, bibtex, makeindex | ✓ | – | ✓ | fig | – | – | – | – |
| [latexn](https://www.ctan.org/pkg/latexn) | csh | 1997 | dvi | latex, bibtex, makeindex | – | – | – | – | – | – | – |
| [make-latex](https://www.ctan.org/pkg/make-latex) | Makefile | 1993 | latex, dvips, bibtex | ✓ | ✓ | ✓ | fig, plot | – | fig | – | – |
| [mk](https://www.ctan.org/pkg/mk) | Ruby | 2012 | latex, xelatex, pdflatex, texi2dvi | ✓ | ✓ | ✓ | – | – | – | – | – |
| [rake2latex](https://www.ctan.org/pkg/rake4latex) | Ruby | 2001 | pdflatex, xelatex, lualatex, bibtex, makeindex | ✓ | ✓ | – | – | – | – | – | – |
| [ShLaTeX](https://www.ctan.org/pkg/shlatex) | Bash/C | 2003 | latex, pdflatex, dvips, ps2pdf, bibtex, makeindex | ✓ | ✓ | ✓ | – | – | – | – | – |
| [texi2dvi](https://www.ctan.org/pkg/texi2dvi) | Sh | 2013 | latex, dvips, dvipdf, pdflatex, bibtex, makeindex | ✓ | ✓ | – | – | – | – | – | – |
| [cluttex](https://github.com/tvondra/cluttex) | Bash | 2025-03-23 | latex, pdflatex, xelatex, lualatex, bibtex, biber, makeindex, makeglossaries | ✓ | ✓ | – | – | – | – | – | – |
| [latex-runner](https://github.com/onlyswimmer/latex-runner) | Python | 2025-08-26 | latex, pdflatex, xelatex, lualatex | ✓ | – | – | – | – | – | – | Vim |
| [texbld](https://github.com/satabin/texbld) | Python | 2022-06-19 | dockerized build system | ✓ | ✓ | – | – | – | – | – | – |
| [latex-build](https://github.com/mrzool/latex-build) | Makefile | 2025-04-04 | latex, pdflatex, xelatex, lualatex, bibtex, biber, makeindex | ✓ | – | – | – | – | – | – | – |
| [makelatex](https://github.com/Ragnaroek/makelatex) | Rust | 2023-06-16 | pdflatex | ✓ | – | – | – | – | – | – | – |

The columns are:

- *Maker:* the name of the TeX maker (with a link to its homepage or CTAN/GitHub page)
- *Type:* the language of implementation
- *Date:* the last update date (from CTAN, GitHub, or the project’s metadata)
- *Supported Tools:* the tools that are used/invoked to produce the output
- *Detect Changes:* indicates whether the tool can detect changes in source files:
  - TeX files (`.tex`),
  - BibTeX files (`.bib`), and
  - included image files (`.png`, `.jpg`, `.pdf`, `.ps`, `.eps`…)
- *Automatic File Conversions:* indicates whether the tool can produce a picture that can be included in a TeX document from a source format that cannot be directly included:
  - To PS/PDF/PNG: conversion to one of these three formats,
  - To TeX: creation of a TeX file from the source file,
  - To PSTeX/PDFTeX: production of a PS or PDF file with embedded TeX macros
- *Export to Elsevier:* indicates whether the tool can prepare a document for submission to Elsevier (single TeX file, all figures in the same directory, bibliography inlined)
- *Editor Plugin:* indicates if a dedicated plugin or built-in support is available for popular editors

## Notes

1. *arara:* does not automatically detect changes like `latexmk`, but uses explicit directives. It supports automatic image conversion via its "convert" rule.

## Methodology

All tools were identified from:

- The original 2016 CTAN-based table,
- Current CTAN packages (2020–2026),
- GitHub searches for "latex build", "latex make", "latexmk alternative", and similar keywords,
- Package repositories such as PyPI, RubyGems, and Rust’s crates.io.

The "too old" constraint was waived, so tools with last updates from 1993 to 2003 are still included for historical completeness.