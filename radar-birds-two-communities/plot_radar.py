"""One radar scan, two communities: weather vs birds (FMI Korpo radar, 13 Sep 2023).

Data (open):
  raw polar volume  s3://fmi-opendata-radar-volume-hdf5/2023/09/13/fikor/202309132015_fikor_PVOL.h5  (FMI, CC BY 4.0)
  bird profiles     s3://aloftdata/baltrad/daily/fikor/2023/fikor_vpts_2023091{3,4}.csv  (aloft, Desmet et al. 2025, CC BY 4.0)
Classification here is a simple co-polar correlation threshold (RHOHV < 0.95 = non-meteorological,
as used in bioRad/vol2bird); the aloft profiles use the full vol2bird algorithm.
"""
import numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from radar_lib import read_scan, xy
from pathlib import Path
HERE = Path(__file__).parent

plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 18})
BLUE, ORANGE = "#0072B2", "#E69F00"   # Okabe-Ito

s = read_scan(str(HERE / "data" / "202309132015_fikor_PVOL.h5"), 1.5, ["TH", "RHOHV"])
X, Y = xy(s)
r = (s["rstart"] + (np.arange(s["nbins"]) + .5) * s["rscale"]) / 1000
th = np.where(r[None, :] < 5, np.nan, s["TH"])
cls = np.full(th.shape, np.nan)
ok = np.isfinite(th) & np.isfinite(s["RHOHV"])
cls[ok & (s["RHOHV"] >= 0.95)] = 0
cls[ok & (s["RHOHV"] < 0.95)] = 1
within = r[None, :] <= 60
fbio = np.nansum((cls == 1) & within) / np.sum(np.isfinite(cls) & within)
print(f"biological share of echoes within 60 km: {fbio:.0%}")

d = pd.concat(pd.read_csv(HERE / "data" / f"fikor_vpts_2023091{i}.csv") for i in (3, 4))
d["t"] = pd.to_datetime(d.datetime)
d = d[(d.t >= "2023-09-13T15:00Z") & (d.t <= "2023-09-14T06:00Z")]
p = d.groupby(["t", "height"])[["dens", "ff", "dd"]].mean().reset_index()
g = p.groupby("t")
vid = g.apply(lambda x: (x.dens.fillna(0) * 0.2).sum(), include_groups=False)
mtr = g.apply(lambda x: (x.dens.fillna(0) * x.ff.fillna(0) * 3.6 * 0.2).sum(), include_groups=False)
print(f"peak {vid.max():.0f} birds/km2 at {vid.idxmax()}, night traffic {(mtr*0.25).sum():.0f} birds per km of front")
grid = p.pivot(index="height", columns="t", values="dens")

fig = plt.figure(figsize=(22, 7.6), layout="constrained")
gs = fig.add_gridspec(1, 3, width_ratios=[1, 0.86, 1.3])
lim = 120
ax = fig.add_subplot(gs[0])
m = ax.pcolormesh(X, Y, th, cmap="cividis", vmin=-15, vmax=35, rasterized=True)
cb = fig.colorbar(m, ax=ax, fraction=0.046, pad=0.02); cb.ax.set_title("dBZ", fontsize=16)
ax.set_title("a · What the radar records", loc="left", fontweight="bold")
ax2 = fig.add_subplot(gs[1])
ax2.pcolormesh(X, Y, cls, cmap=ListedColormap([BLUE, ORANGE]), vmin=0, vmax=1, rasterized=True)
ax2.legend(handles=[Patch(color=BLUE, label="rain → weather keeps"),
                    Patch(color=ORANGE, label="“clutter” → ecology keeps")],
           loc="lower left", fontsize=14, framealpha=.9)
ax2.set_title("b · Same scan, two communities", loc="left", fontweight="bold")
for a in (ax, ax2):
    a.set_aspect("equal"); a.set_xlim(-lim, lim); a.set_ylim(-lim, lim)
    a.plot(0, 0, "k+", ms=14, mew=2)
    for rr in (50, 100):
        a.add_patch(plt.Circle((0, 0), rr, fill=False, ls=":", lw=1, color="0.3"))
    a.set_xlabel("km east")
ax.set_ylabel("km north"); ax2.set_yticklabels([])
ax3 = fig.add_subplot(gs[2])
T = grid.columns.tz_convert(None)
m3 = ax3.pcolormesh(T, grid.index / 1000, grid.values, cmap="cividis", vmin=0, vmax=40, shading="nearest", rasterized=True)
cb3 = fig.colorbar(m3, ax=ax3, fraction=0.04, pad=0.02); cb3.ax.set_title("birds/km³", fontsize=16)
ax3.axvline(pd.Timestamp("2023-09-13 20:15"), color=ORANGE, lw=2.5, ls="--")
ax3.set_ylim(0, 3); ax3.set_ylabel("height (km)")
ax3.xaxis.set_major_locator(matplotlib.dates.HourLocator(byhour=range(0, 24, 3)))
ax3.xaxis.set_major_formatter(matplotlib.dates.DateFormatter("%H:%M"))
ax3.set_xlabel("UTC, night of 13–14 Sep 2023")
ax3.set_title("c · The “clutter” as bird migration", loc="left", fontweight="bold")
ax3.text(0.02, 0.96, f"peak ≈ {vid.max():.0f} birds/km², heading south\n≈ {(mtr*0.25).sum()/1000:.0f},000 birds crossed each km of front",
         transform=ax3.transAxes, va="top", fontsize=15, bbox=dict(fc="white", ec="none", alpha=.85))
fig.text(0.0, -0.04, "FMI Korpo radar (fikor), 1.5° scan 20:15 UTC · FMI open data (CC BY 4.0) · bird profiles: aloft / vol2bird (Desmet et al. 2025) · "
         "(b) simple ρhv < 0.95 split, for illustration", fontsize=12, color="0.35")
fig.savefig(HERE / "figure" / "radar_two_communities.png", dpi=130, bbox_inches="tight")
