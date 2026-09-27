"""Figure: 2024 burned area (ESA Fire CCI) and biodiversity records since the fires, Beni."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection

HERE = Path(__file__).parent.parent / "beni-pipeline"  # derived per-cell results live there
FIG = Path(__file__).parent / "figure"
FIG.mkdir(exist_ok=True)
f = np.load(HERE / "results/fire_cells.npz")
c = np.load(HERE / "results/cells.npz")
post = np.load(HERE / "results/post_fire_counts.npy")
s = json.load(open(HERE / "results/postfire_summary.json"))
fs = json.load(open(HERE / "results/fire_summary.json"))

plt.rcParams.update({"font.size": 15, "font.family": "DejaVu Sans"})
fig, axes = plt.subplots(1, 2, figsize=(15.5, 7.0), gridspec_kw={"width_ratios": [1.25, 1]})

ax = axes[0]
p11 = [np.column_stack([lo, la]) for lo, la in zip(f["vlon11"], f["vlat11"])]
ok = np.isfinite(f["burned_frac11"])
pc = PolyCollection([p for p, k in zip(p11, ok) if k], array=100 * f["burned_frac11"][ok], cmap="YlOrRd",
                    clim=(0, 100), edgecolor="none")
ax.add_collection(pc)
fig.colorbar(pc, ax=ax, fraction=0.046, pad=0.02, label="area burned in 2024 (%)")
p9 = [np.column_stack([lo, la]) for lo, la in zip(c["vlon"], c["vlat"])]
gap = (f["burned_frac9"] > 0.25) & (post == 0)
ax.add_collection(PolyCollection([p for p, k in zip(p9, gap) if k], facecolor="none", edgecolor="#004F8F",
                                 linewidth=1.6))
ax.plot([], [], color="#004F8F", linewidth=2, label="burned >25%, no biodiversity record since")
ax.legend(loc="lower right", fontsize=12, frameon=True)
ax.set_xlim(-67.5, -64.5); ax.set_ylim(-15.5, -12.5); ax.set_aspect(1 / np.cos(np.radians(-14)))
ax.set_title(f"ESA Fire CCI (Sentinel-3), 2024: {fs['burned_share_of_observed_burnable_pct']:.0f}% of the area burned\n"
             "HEALPix WGS84 (~3.2 km); outlines ~12.7 km", fontsize=15)

ax = axes[1]
heavy = f["burned_frac9"] > 0.25
before = c["counts"] > 0
cats = [("records since\nOct 2024", int((heavy & (post > 0)).sum()), "#0072B2"),
        ("records before,\nnone since", int((heavy & (post == 0) & before).sum()), "#BDBDBD"),
        ("never any\nrecord", int((heavy & (post == 0) & ~before).sum()), "#4D4D4D")]
ax.bar([k for k, _, _ in cats], [v for _, v, _ in cats], color=[col for _, _, col in cats])
for i, (_, v, _) in enumerate(cats):
    ax.text(i, v + 2, str(v), ha="center", fontsize=16, fontweight="bold")
ax.set_ylabel("cells burned >25% in 2024")
ax.set_title(f"{s['heavily_burned_cells']} heavily burned cells:\n"
             f"{s['heavily_burned_without_record_since_pct']:.0f}% not re-observed on the ground", fontsize=15)
ax.spines[["top", "right"]].set_visible(False)

fig.text(0.01, 0.005, "ESA Fire_cci SYN burned area v1.1 (doi:10.5285/d441079fc77f49fabeb41330612b252f); "
         f"GBIF.org, records with eventDate 2024-10-01 to 2026-09-30, retrieved 2026-09-26. Grid via healpix-connector.",
         fontsize=10.5, color="#555")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(FIG / "beni_fire_where.png", dpi=110)
print("saved")
