# Slide 33 (backup) (`fill-gaps`) — filling satellite SST gaps with the scattering transform (FOSCAT)

Copernicus Marine passive-microwave L3S SST (2026-04-01) on HEALPix nside 32; gaps (between orbits, low quality;
~28% of ocean cells) filled by a smooth spherical-harmonic fit vs the cross-scattering transform (FOSCAT),
checked against the L4 analysis. From `annefou/fiesta-scattering-sst` (MIT, commit 21f8f95), with one added line
saving the maps.

    copernicusmarine login                     # free account; credentials stay in ~/.copernicusmarine
    python 01_sst_gap_filling_save_maps.py     # ~3 min CPU -> results/sst_maps.npz, results/*.json
    python 02_plot.py                          # -> figure/sst_slide16.png   (env: ../environments/foscat.yml)

Shipped: `results/sst_maps.npz` (Copernicus Marine derived product; credit "Generated using E.U. Copernicus Marine
Service Information"). Checked 2026-09-26: plot byte-identical; full re-run RMSE 0.985 K vs 11.46 K (published 0.989 K;
FOSCAT optimisation is not bit-deterministic). Caveat: texture statistics come from the same L4 used for validation.
