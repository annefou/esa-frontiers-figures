"""Step 9: the Beni per-cell results as self-describing Zarr stores (CF attributes + HEALPix grid declaration).

Steps 1-8 pass NumPy .npz arrays to each other: names only, no units or meaning. This step writes the results
that the slides use as three Zarr stores, one per HEALPix depth, where every variable declares what it is:

    results/beni_healpix_d9.zarr    610 cells   (~12.7 km)  biomass, forest height, GBIF counts, fire, climate, AOA
    results/beni_healpix_d11.zarr   10,781 cells (~3.2 km)  burned fraction, pre-fire biomass, rainfall
    results/beni_healpix_d12.zarr   29,986 cells (~1.6 km)  BIOMASS forest height, its quality, acquisitions

- Grid: `cell_ids` carries the xdggs convention (grid_name, level, indexing_scheme, ellipsoid), so any
  xdggs / healpix-geo reader rebuilds the exact WGS84 cells from the IDs.
- Checked with cfchecker 4.1.0 against CF-1.8 and standard name table v95: 0 errors, 0 warnings
  (the checker reads netCDF; see check_cf.py).
- Variables: CF standard_name where the CF table (v95) has one (canopy_height, burned_area_fraction,
  air_temperature, precipitation_amount, number_of_observations); where it has none (above-ground
  biomass, GBIF record counts, the BIOMASS quality value), long_name + units + a comment saying so.
- Flags: masks carry flag_values / flag_meanings, the CF way to declare what a code means.
- Record-level data (GBIF points) are not here: they are Darwin Core records, not grid cells.

Values are copied unchanged from the .npz files (asserted below). Env: ../environments/plot.yml.
"""
import json
from pathlib import Path

import numpy as np
import xarray as xr

HERE = Path(__file__).parent
R = HERE / "results"
S = json.load(open(R / "summary.json"))
BBOX = S["region"]["bbox_lonlat"]

DOI = {
    "cci_biomass": "doi:10.5285/6429d1aafe1e43b9b414e4a5a7f8b903",
    "fire_cci": "doi:10.5285/d441079fc77f49fabeb41330612b252f",
    "chelsa": "doi:10.1038/sdata.2017.122",
    "aoa": "doi:10.1111/2041-210X.13650",
}
NO_STD = "No CF standard name exists for this quantity (CF standard name table v95, checked 2026-09-29)."
AGB_DEFINITION = ("Oven-dry weight of the woody parts (stem, bark, branches and twigs) of all living trees excluding "
                  "stump and roots, per unit area (ESA CCI Biomass v7.0 dataset description, CEDA catalogue)")
AGB_RELATED = ("Related, not identical: http://purl.obolibrary.org/obo/AGRO_00000546 'aboveground biomass' "
               "(includes stump, seeds and foliage); http://vocab.nerc.ac.uk/collection/EXV/current/EXV049/ "
               "'Above-ground biomass' (GCOS essential climate variable, no definition of its own). "
               "ENVO has 'biomass' only as a synonym of ENVO:01000155 'organic material' (a material, not a quantity per area).")


def cell_coord(ids, level):
    return xr.Variable("cells", ids.astype(np.uint64), {
        "long_name": "HEALPix cell index", "units": "1",
        "grid_name": "healpix", "level": int(level), "indexing_scheme": "nested", "ellipsoid": "WGS84",
        "comment": "Equal-area HEALPix on the WGS84 ellipsoid (healpix-geo, authalic mapping). "
                   "Cell geometry is fully defined by (level, cell id); see xdggs.",
    })


def global_attrs(title, level, cell_km, summary):
    return {
        "Conventions": "CF-1.8",
        "title": title,
        "summary": summary,
        "institution": "LifeWatch ERIC",
        "creator_name": "Anne Fouilloux",
        "project": "ESA Frontiers of Science 2026 talk; ESA GRID4EARTH",
        "source": "esa-frontiers-figures/beni-pipeline (steps 1-8), exported by 09_export_zarr.py",
        "history": "Source products binned into WGS84 HEALPix cells with healpix-connector v0.1.0 "
                   "(area-weighted binning of pixel centres); exported to Zarr 2026-09-29.",
        "geospatial_lon_min": BBOX[0], "geospatial_lat_min": BBOX[1],
        "geospatial_lon_max": BBOX[2], "geospatial_lat_max": BBOX[3],
        "dggs_name": "HEALPix", "dggs_level": int(level), "dggs_cell_size_km": cell_km,
        "license": "Derived data; each source keeps its own terms, see DATA_LICENSES.md in the repository",
        "references": "https://github.com/annefou/esa-frontiers-figures",
    }


def flag(values, meanings, long_name):
    return {"long_name": long_name, "flag_values": np.array(values, dtype=np.int8), "flag_meanings": meanings}


def d9():
    c, f, g, fire, w = (np.load(R / n) for n in ("cells.npz", "fh_cells.npz", "g2s_cells.npz", "fire_cells.npz", "where_next.npz"))
    ids = c["cells"]
    assert np.array_equal(ids, g["cells"]) and np.array_equal(ids, fire["cells9"]) and len(w["use"]) == ids.size
    gb = S["gbif_all_taxa"]
    v = {
        "agb": (c["agb_mean"], {
            "long_name": "Above-ground biomass, cell mean of ESA CCI Biomass v7.0 (2023, 100 m)",
            "units": "Mg ha-1", "cell_methods": "area: mean",
            "definition": AGB_DEFINITION, "related_terms": AGB_RELATED,
            "comment": NO_STD + " Source variable 'agb' in ESA CCI Biomass v7.0 (netCDF, CF-1.7) carries only a long_name; "
                       "the definition above is in the dataset description, not in the file.",
            "source": "ESA CCI Biomass v7.0 " + DOI["cci_biomass"], "ancillary_variables": "agb_sd agb_within_cell_std"}),
        "agb_sd": (c["agb_sd_mean"], {
            "long_name": "Above-ground biomass per-pixel standard deviation from ESA CCI Biomass v7.0, cell mean",
            "units": "Mg ha-1", "cell_methods": "area: mean", "comment": NO_STD,
            "source": "ESA CCI Biomass v7.0 AGB_SD " + DOI["cci_biomass"]}),
        "agb_within_cell_std": (c["agb_within_std"], {
            "long_name": "Spread of 100 m above-ground biomass pixels within the cell",
            "units": "Mg ha-1", "cell_methods": "area: standard_deviation", "comment": NO_STD}),
        "canopy_height": (f["fh9"], {
            "standard_name": "canopy_height", "units": "m", "cell_methods": "area: mean",
            "long_name": "BIOMASS L2A forest height (FH), mean of the depth-12 cells observed",
            "comment": "Mapping by us: BIOMASS names this quantity 'forest height' (product FP_FH); we declare it as CF "
                       "canopy_height. Products with median quality < 1.0 excluded (see fh_summary.json).",
            "source": "ESA BIOMASS L2A FP_FH, BPS-Biomass L2a processor 4.4.4, 200 m, via ESA MAAP",
            "ancillary_variables": "canopy_height_observed_fraction"}),
        "canopy_height_observed_fraction": (f["frac9"], {
            "long_name": "Fraction of the cell's depth-12 children with a BIOMASS forest height value", "units": "1"}),
        "gbif_occurrence_count": (c["counts"], {
            "long_name": "Number of GBIF occurrence records with coordinates in the cell, all taxa", "units": "1",
            "comment": NO_STD + f" GBIF occurrence search per exact cell polygon, hasCoordinate=true, "
                       f"checklistKey={gb['checklist_key']}, retrieved {gb['retrieved_at']}. Measures sampling effort, not biodiversity."}),
        "gbif_mammal_count": (c["mammal_counts"], {
            "long_name": "Number of GBIF occurrence records of Mammalia assigned to the cell by their point", "units": "1",
            "comment": NO_STD + f" retrieved {S['gbif_mammals']['provenance']['retrieved_at']}."}),
        "gbif_sequenced_count": (g["seq_n"], {
            "long_name": "Number of GBIF occurrence records with a DNA sequence (isSequenced=true) in the cell", "units": "1",
            "comment": NO_STD}),
        "gbif_calomys_callosus_count": (g["host_n"], {
            "long_name": "Number of GBIF occurrence records of Calomys callosus (reservoir host of Machupo virus) in the cell",
            "units": "1", "comment": NO_STD}),
        "burned_area_fraction": (fire["burned_frac9"], {
            "standard_name": "burned_area_fraction", "units": "1",
            "long_name": "Fraction of observed, burnable 300 m pixels burned at least once in 2024",
            "cell_methods": "area: mean time: maximum",
            "comment": "Denominator: observed, burnable pixels. Fire_cci JD codes: day of year = burned; 0 = not burned; -1 = not observed (excluded); "
                       "-2 = not burnable (excluded). These code meanings are in the Fire_cci Product User Guide, "
                       "not in the source GeoTIFF.",
            "source": "ESA Fire_cci SYN burned area pixel v1.1 (Sentinel-3) " + DOI["fire_cci"],
            "ancillary_variables": "burned_confidence"}),
        "burned_confidence": (fire["conf9"], {
            "long_name": "Fire_cci confidence level of burned pixels, mean over the cell", "units": "percent",
            "comment": NO_STD}),
        "air_temperature": (g["bio1"], {
            "standard_name": "air_temperature", "units": "degC",
            "long_name": "Mean annual air temperature (CHELSA BIO1), 1981-2010 climatology",
            "cell_methods": "area: mean time: mean within years time: mean over years",
            "source": "CHELSA v2.1 " + DOI["chelsa"]}),
        "precipitation_amount": (g["bio12"], {
            "standard_name": "precipitation_amount", "units": "kg m-2",
            "long_name": "Annual precipitation amount (CHELSA BIO12), 1981-2010 climatology",
            "cell_methods": "area: mean time: sum within years time: mean over years",
            "source": "CHELSA v2.1 " + DOI["chelsa"]}),
        "aoa_considered": (w["use"].astype(np.int8), flag([0, 1], "not_considered considered",
            "Cell used in the area-of-applicability analysis (canopy height observed on >= 80% and all predictors finite)")),
    }
    for k in ("all_taxa", "mammals", "dna_sequenced"):
        v[f"dissimilarity_index_{k}"] = (w[f"di_{k}"], {
            "long_name": f"Dissimilarity index to cells with {k.replace('_', ' ')} GBIF records, in the space of "
                         "canopy height, above-ground biomass, BIO1 and BIO12 (standardised)",
            "units": "1", "aoa_threshold": float(w[f"thr_{k}"]),
            "comment": NO_STD + " After Meyer & Pebesma 2021 " + DOI["aoa"] + "; cells with a value above aoa_threshold "
                       "are outside the area of applicability of the in-situ records.",
            "ancillary_variables": "aoa_considered"})
    ds = xr.Dataset({k: ("cells", a, at) for k, (a, at) in v.items()}, coords={"cell_ids": cell_coord(ids, 9)})
    ds.attrs = global_attrs("Beni lowlands (Bolivia) on WGS84 HEALPix depth 9: EO, GBIF, fire and climate per cell",
                            9, 12.73, "Per-cell layers joined by cell ID for the ESA Frontiers talk, slides 9-13.")
    return ds


def d11():
    fire, fr = np.load(R / "fire_cells.npz"), np.load(R / "fire_result.npz")
    ids = fire["cells11"]
    assert np.array_equal(ids, fr["cells"]) and np.allclose(fire["burned_frac11"], fr["burned"], equal_nan=True)
    v = {
        "burned_area_fraction": (fr["burned"], {
            "standard_name": "burned_area_fraction", "units": "1",
            "long_name": "Fraction of observed, burnable 300 m pixels burned at least once in 2024",
            "cell_methods": "area: mean time: maximum",
            "comment": "Denominator: observed, burnable pixels (Fire_cci JD >= 0).",
            "source": "ESA Fire_cci SYN burned area pixel v1.1 " + DOI["fire_cci"]}),
        "agb": (fr["agb"], {
            "long_name": "Pre-fire above-ground biomass (ESA CCI Biomass v7.0, 2023), cell mean",
            "units": "Mg ha-1", "cell_methods": "area: mean", "comment": NO_STD + " Only cells >90% covered.",
            "definition": AGB_DEFINITION, "related_terms": AGB_RELATED,
            "source": "ESA CCI Biomass v7.0 " + DOI["cci_biomass"]}),
        "precipitation_amount": (fr["rain"], {
            "standard_name": "precipitation_amount", "units": "kg m-2",
            "long_name": "Annual precipitation amount (CHELSA BIO12), 1981-2010 climatology, sampled at the cell",
            "source": "CHELSA v2.1 " + DOI["chelsa"]}),
        "analysis_mask": (fr["m"].astype(np.int8), flag([0, 1], "excluded included",
            "Cell used in the fire vs biomass and rainfall analysis (all three layers finite)")),
    }
    ds = xr.Dataset({k: ("cells", a, at) for k, (a, at) in v.items()}, coords={"cell_ids": cell_coord(ids, 11)})
    ds.attrs = global_attrs("Beni lowlands (Bolivia) on WGS84 HEALPix depth 11: 2024 burning, pre-fire biomass, rainfall",
                            11, 3.18, "Descriptive association only (one region, one fire year).")
    return ds


def d12():
    f = np.load(R / "fh_cells.npz")
    v = {
        "canopy_height": (f["fh"], {
            "standard_name": "canopy_height", "units": "m", "cell_methods": "area: mean",
            "long_name": "BIOMASS L2A forest height (FH), pixel-count-weighted mean over repeat acquisitions",
            "comment": "Mapping by us: BIOMASS 'forest height' declared as CF canopy_height.",
            "source": "ESA BIOMASS L2A FP_FH, BPS-Biomass L2a processor 4.4.4, 200 m, via ESA MAAP",
            "ancillary_variables": "biomass_quality number_of_acquisitions"}),
        "biomass_quality": (f["qual"], {
            "long_name": "BIOMASS L2A quality layer value, cell mean", "units": "1",
            "comment": NO_STD + " The meaning of the quality values is not declared in the product files; "
                       "the pipeline drops products whose median quality is < 1.0 (see fh_summary.json)."}),
        "number_of_acquisitions": (f["n_acq"], {
            "standard_name": "number_of_observations", "units": "1",
            "long_name": "Number of BIOMASS acquisitions averaged in the cell"}),
    }
    ds = xr.Dataset({k: ("cells", a, at) for k, (a, at) in v.items()}, coords={"cell_ids": cell_coord(f["fine_ids"], 12)})
    ds.attrs = global_attrs("Beni lowlands (Bolivia) on WGS84 HEALPix depth 12: BIOMASS forest height",
                            12, 1.59, "BIOMASS L2A forest height, 16 products from April-August 2026.")
    return ds


if __name__ == "__main__":
    for name, ds in (("d9", d9()), ("d11", d11()), ("d12", d12())):
        out = R / f"beni_healpix_{name}.zarr"
        ds.to_zarr(out, mode="w", consolidated=True)
        print(f"{out.name}: {ds.sizes['cells']} cells, {len(ds.data_vars)} variables")
