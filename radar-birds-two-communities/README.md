# Slide 12 (`radar-birds`) — Weather radar: one scan, two communities

FMI Korpo radar (fikor), night of 13–14 September 2023: the echo weather services remove as clutter is the bird
migration ecologists keep.

    bash download.sh               # FMI open radar volume + aloft bird profiles (CC BY 4.0)
    python plot_radar.py           # env: ../environments/plot.yml (+ h5py) -> figure/

- The night was chosen as the strongest night-time bird density among six Finnish radars, May and Sep 2023.
- Daily aloft files hold three 5-min profiles per 15-min timestamp; they are averaged.
- Panel b uses a simple RHOHV < 0.95 split (illustration only); panel c is vol2bird output from aloft
  (Desmet et al. 2025).
- Results: 74 % of echoes within 60 km non-meteorological; peak ≈ 36 birds/km²; ≈ 8,000 birds per km of front
  overnight, heading ~185°.
