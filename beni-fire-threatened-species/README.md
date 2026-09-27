# Slide 13 (`fire-act`) — 2024 fires and threatened-species records in the Beni: could responders know where they are?

    python plot_fire_action.py     # env: ../environments/plot.yml -> figure/

Reads `../beni-pipeline/results/fire_cells.npz` (shipped), `fire_action.json` (shipped) and
`fire_action_points.npz` (NOT shipped). To rebuild the points, run in `../beni-pipeline/`:

    python 08a_get_threatened_records.py   # GBIF API: IUCN CR, EN, VU records in the Beni bbox
    python 08b_beni_fire_action.py         # healpix-connector env -> fire_action.json + fire_action_points.npz

The record-level files hold the locations of threatened species and are deliberately not published here:
the slide's point is that exact sites should reach the right hands, not a public file. The GBIF API is live,
so a re-run gives slightly different counts. Checked 2026-09-27: from the 2026-09-26 GBIF extract, the
analysis reproduces `fire_action.json` exactly and the plot is byte-identical to the deck image in `reference/`.
