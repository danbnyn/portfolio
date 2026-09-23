# Figure data and interpretation

These are **mock diagnostics and declared synthetic measurements, not inference
results**. Full provenance, adopted units and raw-input SHA256 are in
`provenance.json`; analysis instructions are in the root README.

`scene.csv` retains the fixed 12 × 12 arcmin, H < 24 scene, original host and row
identifiers, simulation redshift-space coordinates and synthetic-measurement
parameters. `source_row` is a zero-based parsed CSV row index, not a text line
number (the input has blank lines). `galaxy_id` should be interpreted with its
host identifier, not assumed globally unique.

The source PDZ has three components in s = log(1+z). Measurement shifts are
[-0.25, 0, +0.25], probabilities [0.04, 0.92, 0.04], and width multipliers
[1.5, 1, 1.5]. Its magnitude-dependent base width is recorded per object. The
source prior is uniform in s on 0 < z < 3.2; the corresponding density in z is
proportional to 1/(1+z). The whole truncated mixture is normalized once; its
components are not separately renormalized. The full PDZ is defined by these
parameters, not by one redshift estimate or by the 25-node 3D display.

`profiles-per-halo.csv` contains all 339 × 18 individual annular measurements;
`profile-centres.csv` describes the conditioning centres. `total_n`, `primary_n`
and `environment_n` are integer counts in the **same** projected annulus and
redshift-space cylinder. `random_mean_n` averages 12 matched random apertures.
Surface densities divide each row's counts by `annulus_area_cmpc2_h2` before
averaging halos. `other_central_n` uses a separate true-distance spherical-shell
geometry; its density ratio divides by `shell_volume_cmpc3_h3` and then by
`central_reference_density`. Do not interchange these geometries.

`reference-redshift.csv` is a smoothed histogram of the entire selected mock,
normalized as a teaching redshift reference. It is not an independent survey
calibration. `interactive-data.js` stores the compact plotted arrays, exact PDZ
bin integrals and deterministic quadrature nodes; it is rebuilt from these CSVs
by `tools/make_figures.py`.

SVG files are the static scientific views. PNGs are inspection/preview versions
of those same views, not extra scientific results. The three figure groups are:
scene (sky, redshift space, PDZ map, interactive 3D), cluster-centric profiles
(projected galaxies and real-space halo centres), and a PDZ response explorer.
