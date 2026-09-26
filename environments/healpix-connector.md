# Beni analysis environment (beni-pipeline/*.py)

The Beni analysis scripts use **healpix-connector** (MIT) at commit
`e777663cc5f08d5c543da16f02c5eaa08640ff03` (reports `__version__` 0.0.1; released as v0.1.0),
run in its own pixi `test` environment (healpix-geo 0.4.1, rasterio, requests, numpy):

    git clone https://github.com/annefou/healpix-connector && cd healpix-connector
    git checkout e777663cc5f08d5c543da16f02c5eaa08640ff03 && pixi install -e test
    export HEALPIX_CONNECTOR=$PWD            # the scripts add $HEALPIX_CONNECTOR/src to sys.path
    cd ../esa-frontiers-figures/beni-pipeline && $HEALPIX_CONNECTOR/.pixi/envs/test/bin/python beni_biomass_gbif.py

Known issue: `read_window` misplaces pixels (~2° west, silently) when the requested bbox extends beyond
the GeoTIFF; `beni_biomass_fh.py` works around it with `clipped_bbox()`. Report/fix upstream.
