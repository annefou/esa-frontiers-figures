"""Figure: from genome to space on one WGS84 HEALPix grid (Beni lowlands)."""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection
from matplotlib.colors import LogNorm

HERE = Path(__file__).parent.parent / "beni-pipeline"  # derived per-cell results live there
FIG = Path(__file__).parent / "figure"
FIG.mkdir(exist_ok=True)
d = np.load(HERE / "results/g2s_cells.npz")
s = json.load(open(HERE / "results/g2s_summary.json"))
polys = [np.column_stack([lo, la]) for lo, la in zip(d["vlon"], d["vlat"])]

plt.rcParams.update({"font.size": 14, "font.family": "DejaVu Sans"})
fig, axes = plt.subplots(1, 4, figsize=(18.5, 5.9))


def base(ax):
    ax.add_collection(PolyCollection(polys, facecolor="#F1F3F5", edgecolor="#DDE1E5", linewidth=0.2))


def counts(ax, v, cmap, title, label):
    base(ax)
    m = v > 0
    pc = PolyCollection([p for p, k in zip(polys, m) if k], array=v[m], cmap=cmap,
                        norm=LogNorm(vmin=1, vmax=max(10, v.max())), edgecolor="none")
    ax.add_collection(pc)
    fig.colorbar(pc, ax=ax, fraction=0.046, pad=0.02, label=label)
    ax.set_title(title, fontsize=14)


counts(axes[0], d["seq_n"], "Purples",
       f"GENOME\nDNA-sequenced records: {s['genome']['records']}\nin {s['genome']['cells_with_any_pct']:.0f}% of cells",
       "records per cell (log)")
counts(axes[1], d["host_n"], "OrRd",
       f"SPECIES · ONE HEALTH\nMachupo reservoir (Calomys callosus)\n{s['one_health_host']['records']:,} records, "
       f"{s['one_health_host']['top_cell_share_pct']:.0f}% in one cell", "records per cell (log)")
hot = np.argmax(d["host_n"])
cx, cy = d["vlon"][hot].mean(), d["vlat"][hot].mean()
axes[1].annotate("San Joaquín, 1963–64\nmuseum specimens\n“±1.16 m”", xy=(cx, cy), xytext=(-67.35, -14.9),
                 fontsize=12, arrowprops=dict(arrowstyle="->", color="#333", lw=1.4))

ax = axes[2]; base(ax)
ok = (d["frac9"] >= 0.8) & np.isfinite(d["fh9"])
pc = PolyCollection([p for p, k in zip(polys, ok) if k], array=d["fh9"][ok], cmap="YlGn", clim=(0, 25), edgecolor="none")
ax.add_collection(pc); fig.colorbar(pc, ax=ax, fraction=0.046, pad=0.02, label="forest height (m)")
ax.set_title(f"ECOSYSTEM\nBIOMASS forest height (2026)\n{int(ok.sum())} of {len(polys)} cells observed", fontsize=14)

ax = axes[3]; base(ax)
pc = PolyCollection(polys, array=d["bio12"], cmap="GnBu", edgecolor="none")
ax.add_collection(pc); fig.colorbar(pc, ax=ax, fraction=0.046, pad=0.02, label="annual precipitation (mm)")
ax.set_title("ENVIRONMENT\nCHELSA climate 1981–2010\nall cells", fontsize=14)

for ax in axes:
    ax.set_xlim(-67.5, -64.5); ax.set_ylim(-15.5, -12.5); ax.set_aspect(1 / np.cos(np.radians(-14)))
    ax.set_xticks([-67, -66, -65]); ax.set_yticks([-15, -14, -13]); ax.tick_params(labelsize=11)

fig.text(0.5, 0.035, f"Same 610 cells (HEALPix WGS84, ~12.7 km). Cells with all four layers: {s['all_four_layers_cells']}.",
         ha="center", fontsize=15, fontweight="bold", color="#004F8F")
fig.text(0.01, 0.005, "GBIF.org (retrieved 2026-09-26), incl. Field Museum mammal collection doi:10.15468/n4zgxw; ESA BIOMASS L2A FP_FH (ESA MAAP); "
         "CHELSA v2.1 doi:10.16904/envidat.228. Grid via healpix-connector.", fontsize=10, color="#555")
fig.tight_layout(rect=(0, 0.06, 1, 1))
fig.savefig(FIG / "beni_genome_to_space.png", dpi=110)
print("saved")
