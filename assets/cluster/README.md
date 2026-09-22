# Cluster article figures

These files support the first research note. They are not inference results.

| Files | Basis | Intended lesson |
| --- | --- | --- |
| `scene-sky`, `scene-hosts`, `scene-redshift` | Same 2,737 rows from the supplied Flagship export | Projection and host identity are different information |
| `conditional-mean` | Explicit schematic curves | Conditioning and three-dimensional exclusion change the expected external mean |
| `poisson-cox` | One-cell probability calculation | Random intensity adds variance beyond Poisson sampling |
| `prior-short`, `prior-long`, `prior-modes` | Explicit 64-cell Gaussian covariances, common seeded white drivers | Covariance determines the spatial freedom of a positive field |
| `redshift-likelihoods` | Synthetic curves, not catalogue measurements | One uncertain redshift law belongs to one galaxy |

Each name has an SVG used by the site and a PNG preview. Figure generation uses
ordinary Matplotlib defaults, with distinct marker shapes and line styles as well
as its default colours. No font files are distributed.

`scene.csv` preserves a unique zero-based `source_row` index from the raw data
rows. It does not assume the exported `galaxy_id` is globally unique. Host IDs
remain integers. `provenance.json` records the raw input checksum, export cuts,
fixed additional selection, illustrative host IDs and counts. The large raw
catalogue and the private contact line in its header are not copied here.

`illustration-models.json` gives teaching-model specifications. The full executable
formulas are in `../../tools/make_figures.py`. Running that script without an
argument uses `scene.csv`; use `--catalogue` to reproduce the subset from the
original compressed export. `../../tools/check_math.py` checks identities and
subset properties, not the scientific performance of the refinement method.

## Required acknowledgement from the export

This work has made use of CosmoHub (Tallada et al. 2020; Carretero et al. 2018), developed by PIC (maintained by IFAE and CIEMAT) in collaboration with ICE-CSIC. It received funding from the Spanish government (grant EQC2021-007479-P funded by MCIN/AEI/10.13039/501100011033), the EU NextGeneration/PRTR (PRTR-C17.I1), and the Generalitat de Catalunya.

Full bibliographic references are in the article’s references section.
