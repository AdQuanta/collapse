# Build and verification

## Environment

- Manuscript date: 2026-08-14.
- REVTeX class: `revtex4-2` with APS/PRL options.
- Letter layout: `reprint` (double column).
- Supplement layout: `onecolumn`, `10pt`, and `notitlepage` (single column).
- Compiler used for the verified PDFs:
  `C:\Users\matan\AppData\Local\Programs\MiKTeX\miktex\bin\x64\pdflatex.exe`.
- Bibliography processor:
  `C:\Users\matan\AppData\Local\Programs\MiKTeX\miktex\bin\x64\bibtex.exe`.

The source uses only standard REVTeX/AMS/TikZ/graphics packages.  A conventional
TeX Live installation with REVTeX 4.2 may be used in place of MiKTeX.

## Rebuild the figures

From the repository root:

```powershell
.venv\Scripts\python.exe manuscript\scripts\build_figures.py
```

The script verifies the primary raw-data digest before rendering and writes:

- `manuscript/figures/full_sphere_matched.pdf` and `.png`;
- `manuscript/figures/matched_field_scaling.pdf` and `.png`;
- `manuscript/figures/figure_manifest.json`.

It launches no simulation and overwrites no campaign data.

## Build the Letter

Run from `manuscript`:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

## Build the Supplemental Material

Run from `manuscript`:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
bibtex supplement
pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
pdflatex -interaction=nonstopmode -halt-on-error supplement.tex
```

## Verified outputs

- `manuscript/main.pdf`: 4 pages, double column, four main-text figures.
- `manuscript/supplement.pdf`: 5 pages, single column, one supplemental figure.
- Final logs contain no overfull boxes, undefined references, or undefined
  citations.
- All 9 pages were rendered to PNG and visually inspected.  No clipping,
  overlap, broken equation, or illegible table/figure was found.

The Letter's final page contains the remaining references and therefore has
unused white space; this does not affect the four-page PRL length.

## Focused scientific checks

```powershell
.venv\Scripts\python.exe -m py_compile manuscript\scripts\build_figures.py
.venv\Scripts\python.exe manuscript\scripts\build_figures.py
```

The generated manifest records the raw hash, binning, occupancy, full-sphere
residuals, harmonic parity, and binning sensitivity.  Further run-level checks
and limitations are in `NUMERICAL_PROVENANCE.md` and `AUDIT.md`.

## Submission guidance checked

The package was structured against the APS PRL author guidance, the APS length
guide (3750 words for a Letter), the APS Supplemental Material instructions,
and the REVTeX 4.2 author guide.  Author identity, affiliation, funding, and
contribution placeholders must be replaced before submission.
