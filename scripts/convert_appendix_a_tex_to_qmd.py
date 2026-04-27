"""
Regenerate appendix-a.qmd from Appendix A Math for PCRA.tex.
Requires: pip install pypandoc-binary
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

try:
    import pypandoc
except ImportError as e:  # pragma: no cover
    print("Install: pip install pypandoc-binary", file=sys.stderr)
    raise e

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "Appendix A Math for PCRA.tex"
OUT = ROOT / "appendix-a.qmd"

# Author (year) strings for in-text \citet keys in this appendix
CITET: dict[str, str] = {
    "Gentle2017": "Gentle (2017)",
    "Strang2016": "Strang (2016)",
    "LuenbergerYe2008": "Luenberger and Ye (2008)",
    "Steele2004": "Steele (2004)",
    "LuShiou2002": "Lu and Shiu (2002)",
    "LvHuang2007": "Lü and Huang (2007)",
    "HendersonSearle1981": "Henderson and Searle (1981)",
    "Hager1989": "Hager (1989)",
    "Stevens1998": "Stevens (1998)",
    "Stevens1997": "Stevens (1997)",
    "Hayashi2000": "Hayashi (2000)",
    "CornuejolsEtAl2018": "Cornuéjols, Peña, and Tutuncu (2018)",
    "Kwan2007": "Kwan (2007)",
    "Kwan2018": "Kwan (2018)",
    "MarkowitzStarerFramGerber2020": "Markowitz, Starer, Fram, and Gerber (2020)",
}

YAML = """---
title: "Appendix A: Mathematical Tools for PCRA"
subtitle: "Vectors, Matrices, Functions, and Optimization (full text)"
---

::: {{.callout-important appearance="minimal"}}
**Copyright notice.** Planned for publication in 2026 by R. Douglas Martin, Thomas K. Philips, Bernd Scherer, and Kirk Li. All rights reserved. © Copyright 2025.
:::

::: {{.callout-note appearance="minimal"}}
A PDF build of the Springer-style appendix is still available: [Download Appendix A — Mathematical Tools for PCRA](Appendix%20A%20Math%20for%20PCRA.pdf){{target="_blank"}}. This page is the same material rendered for the web.
:::

""".replace(
    '](Appendix%20A%20Math%20for%20PCRA.pdf){{target="_blank"}}',
    '](Appendix%20A%20Math%20for%20PCRA.pdf){target="_blank"}',
)

FRONT = """# Overview

The introduction below is followed by the full web version of the appendix, converted from the same LaTeX source as the book PDF.

---
"""

# List item 1: inner-product "non-negativity" is malformed in the book LaTeX; pandoc output must be replaced.
BROKEN_NON_NEQ = re.compile(
    r"1\.\s+Non--negativity:\s*\$\\mathrm\{\\mathbf\{\\left\\langle.*?(?=\n2\.\s+Commutativity:)",
    re.DOTALL,
)
FIXED_NON_NEQ = (
    r"1.  Non-negativity: $\left\langle \mathrm{\mathbf{u}},\,\mathbf{0}\right\rangle=0$ for all "
    r"$\mathbf{u}$, and $\left\langle \mathrm{\mathbf{u}},\,\mathrm{\mathbf{u}}\right\rangle>0$ if "
    r"$\mathrm{\mathbf{u}}\ne\mathbf{0}$."
)


def postprocess_md(s: str) -> str:
    s = re.sub(r"\{reference-type=\"eqref\" reference=\"[^\"]+\"\}", "", s)
    s = s.replace("\\nicefrac{", "\\tfrac{")
    s = s.replace("^{\\lyxmathsym{\\textdegree}}", "^{\\circ}")
    s = s.replace(
        " Orthogonality is equivalent to condition that $\\theta=90^{\\circ}$$.",
        " Orthogonality is equivalent to condition that $\\theta=90^{\\circ}$.",
    )
    s = s.replace("$X\\lyxmathsym{–}Y$", r"$X$--$Y$")
    s, n = BROKEN_NON_NEQ.subn(lambda _: FIXED_NON_NEQ + "\n", s, count=1)
    if n == 0 and "Non--negativity: $\\mathrm{\\mathbf{\\left\\langle" in s:
        print("Warning: non-negativity list item not auto-fixed; check manually.", file=sys.stderr)
    return s


def main() -> None:
    text = SRC.read_text(encoding="utf-8")
    start = text.find("This Appendix contains")
    end = text.find(r"\end{appendices}")
    if start < 0 or end < 0 or end <= start:
        raise SystemExit("Could not find appendix body markers in .tex file.")
    body = text[start:end].strip()

    def _citet(m: re.Match[str]) -> str:
        k = m.group(1)
        if k not in CITET:
            return f"[citation: {k}]"
        return CITET[k]

    body = re.sub(r"\\citet\{([^}]+)\}", _citet, body)
    out_md = pypandoc.convert_text(
        f"""\\documentclass[11pt]{{article}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{amsmath,amssymb,amsfonts}}
\\DeclareMathOperator{{\\argmax}}{{arg\\,max}}
\\DeclareMathOperator{{\\argmin}}{{arg\\,min}}
\\usepackage{{xcolor}}
\\allowdisplaybreaks[1]
\\begin{{document}}
{body}
\\end{{document}}""",
        to="markdown",
        format="latex",
        extra_args=["--wrap=none"],
    )

    if "[citation:" in out_md:
        print("Warning: unresolved cite keys; search [citation:", file=sys.stderr)

    out_md = postprocess_md(out_md)
    OUT.write_text(
        YAML + FRONT + out_md + "\n", encoding="utf-8", newline="\n"
    )
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
