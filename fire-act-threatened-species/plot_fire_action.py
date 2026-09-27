"""Slide figure: 2024 fires (ESA Fire CCI) and threatened-species records in the Beni — could responders know
where the endangered species were? Colour-blind safe: burned share in YlOrRd; records in black / dark blue."""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import PolyCollection
from matplotlib.lines import Line2D

S = R = Path(__file__).parent.parent / "beni-pipeline" / "results"
FIG = Path(__file__).parent / "figure"
f = np.load(S / "fire_cells.npz"); p = np.load(R / "fire_action_points.npz"); a = json.load(open(R / "fire_action.json"))
plt.rcParams.update({"font.size": 15, "font.family": "DejaVu Sans"})
fig = plt.figure(figsize=(17, 7.4))
ax = fig.add_axes([0.03, 0.1, 0.5, 0.82])
vlon = np.where(f["vlon11"] > 180, f["vlon11"] - 360, f["vlon11"])
polys = [np.column_stack([lo, la]) for lo, la in zip(vlon, f["vlat11"])]
pc = PolyCollection(polys, array=100 * f["burned_frac11"], cmap="YlOrRd", clim=(0, 100), edgecolor="none")
ax.add_collection(pc)
fig.colorbar(pc, ax=ax, fraction=0.04, pad=0.02, label="area burned in 2024 (%)")
bl = p["blurred"] & (p["sp"] == "Ara glaucogularis")
for lo, la, u in zip(p["lon"][bl], p["lat"][bl], p["unc"][bl]):
    r_lat = u / 1000 / 110.57; r_lon = u / 1000 / (111.32 * np.cos(np.radians(la)))
    t = np.linspace(0, 2 * np.pi, 80)
    ax.plot(lo + r_lon * np.cos(t), la + r_lat * np.sin(t), color="#1B3A5C", lw=0.8, alpha=0.35)
pr = p["precise"]
ax.scatter(p["lon"][pr], p["lat"][pr], s=40, c="#111111", edgecolors="#FFFFFF", linewidths=0.8, zorder=5)
ax.set_xlim(-67.5, -64.5); ax.set_ylim(-15.5, -12.5); ax.set_aspect(1 / np.cos(np.radians(-14)))
ax.set_xlabel("Longitude"); ax.set_ylabel("Latitude")
ax.legend(handles=[Line2D([], [], marker="o", ls="", mfc="#111111", mec="#FFFFFF", ms=8, label="threatened species, located ≤3 km"),
                   Line2D([], [], color="#1B3A5C", lw=1.5, label="blue-throated macaw (CR): blurred, ≥31 km")],
          loc="lower left", fontsize=12, framealpha=0.95)
ax.set_title("2024 fires and threatened species, Beni\nWGS84 HEALPix (~3.2 km)", fontsize=15)

bx = fig.add_axes([0.64, 0.16, 0.33, 0.66])
n_prec, n_unk, n_bl = a["precise_le_3km_records"], a["no_uncertainty_records"], a["blurred_records"]
n_oth = a["records"] - n_prec - n_unk - n_bl
labels = ["located\n≤ 3 km", "blurred\n(≥31 km)", "no precision\ndeclared", "other"]
vals = [n_prec, n_bl, n_unk, n_oth]
cols = ["#111111", "#1B3A5C", "#BDBDBD", "#E0E0E0"]
bx.bar(labels, vals, color=cols)
for i, v in enumerate(vals):
    bx.text(i, v + 40, f"{v:,}", ha="center", fontsize=15, fontweight="bold")
bx.set_ylabel("threatened-species records (GBIF)")
bx.spines[["top", "right"]].set_visible(False)
bx.set_title(f"{a['threatened_species_with_records_in_burned_cells']} of {a['threatened_species_total']} threatened species recorded in cells that burned;\n"
             f"only {n_prec} of {a['records']:,} records precise enough to act on", fontsize=14)
fig.text(0.01, 0.01, "ESA Fire_cci SYN v1.1 (2024); GBIF.org threatened taxa (IUCN CR/EN/VU); burned cell = >25% burned; "
         "macaw circle: 'coordinate uncertainty increased to protect threatened taxon'.", fontsize=10.5, color="#555")
fig.savefig(FIG / "beni_fire_action.png", dpi=110)
print("saved")
