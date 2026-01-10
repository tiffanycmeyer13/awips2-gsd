"""
wkt_to_shapefile.py

Convert WKT geometry (or a list of WKTs) to an ESRI Shapefile.

Requirements:
  pip install shapely fiona

Examples:
  # Single WKT string
  python wkt_to_shapefile.py \
      --wkt "POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))" \
      --out polygons.shp --epsg 4326

  # Text file with one WKT per line (all same geom type)
  python wkt_to_shapefile.py \
      --input wkts.txt --out lines.shp --epsg 3857

  # If the input has mixed geometry types, split to multiple shapefiles
  python wkt_to_shapefile.py \
      --input wkts.txt --out features.shp --split-mixed

Other notes:

  Install deps: pip install shapely fiona.

  Shapefiles can’t store EMPTY or GeometryCollection geometries; the script errors in those cases.

  If your input has mixed geometry types (e.g., some Points and some Lines), use --split-mixed 
  and it will create multiple shapefiles like features_Point.shp, features_LineString.shp.

  CRS defaults to EPSG:4326; change with --epsg.

"""
import argparse
import os
from collections import defaultdict

import fiona
from fiona.crs import from_epsg
from shapely import wkt as shapely_wkt
from shapely.geometry import mapping


def read_wkts(wkt_string: str | None, input_path: str | None) -> list[str]:
    if wkt_string:
        return [wkt_string.strip()]
    wkts: list[str] = []
    with open(input_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            wkts.append(line)
    if not wkts:
        raise ValueError("No WKTs found in the input file.")
    return wkts


def load_geoms(wkts: list[str]):
    geoms = []
    for i, w in enumerate(wkts, start=1):
        try:
            g = shapely_wkt.loads(w)
        except Exception as e:
            raise ValueError(f"Invalid WKT on line {i}: {e}") from e
        if g.is_empty:
            # Shapefiles can't store EMPTY geometries; skip or error.
            raise ValueError(f"Geometry on line {i} is EMPTY; shapefile cannot store it.")
        geoms.append(g)
    return geoms


def geom_type_for_fiona(geom):
    """
    Returns a geometry type name that Fiona expects in the schema['geometry'].
    """
    # Shapely's geom.geom_type already matches ('Point', 'LineString', 'Polygon', 'MultiPoint', ...)
    gt = geom.geom_type
    # Shapefiles cannot store GeometryCollection directly
    if gt == "GeometryCollection":
        raise ValueError("GeometryCollection is not supported by the Shapefile driver.")
    return gt


def ensure_outpath(path: str) -> str:
    # Create parent folder if needed
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    # Ensure .shp extension
    if not path.lower().endswith(".shp"):
        path = f"{path}.shp"
    return path


def write_shapefile(out_path: str, geoms, epsg: int):
    """
    Write all geometries of the SAME type to a single shapefile.
    """
    out_path = ensure_outpath(out_path)
    gtype = geom_type_for_fiona(geoms[0])
    # schema: simple id attribute; you can extend as needed.
    schema = {
        "geometry": gtype,
        "properties": {"id": "int"},
    }
    crs = from_epsg(epsg) if epsg else None

    with fiona.open(out_path, "w", driver="ESRI Shapefile", schema=schema, crs=crs) as dst:
        for idx, geom in enumerate(geoms, start=1):
            if geom_type_for_fiona(geom) != gtype:
                raise ValueError(
                    f"Mixed geometry types detected. Expected '{gtype}', got '{geom.geom_type}'. "
                    "Use --split-mixed to write separate shapefiles per type."
                )
            dst.write({"geometry": mapping(geom), "properties": {"id": idx}})

    print(f"Wrote {len(geoms)} feature(s) to {out_path}")


def write_split_by_type(base_out_path: str, geoms, epsg: int):
    """
    Split mixed input into multiple shapefiles, one per geometry type.
    """
    buckets: dict[str, list] = defaultdict(list)
    for g in geoms:
        gtype = geom_type_for_fiona(g)
        buckets[gtype].append(g)

    if not buckets:
        raise ValueError("No geometries to write.")

    written = []
    base_no_ext, _ = os.path.splitext(ensure_outpath(base_out_path))
    for gtype, geos in buckets.items():
        out_path = f"{base_no_ext}_{gtype}.shp"
        # Reuse single-type writer
        write_shapefile(out_path, geos, epsg)
        written.append((gtype, out_path))

    print("Split output:")
    for gtype, out_path in written:
        print(f"  {gtype}: {out_path}")


def main():
    ap = argparse.ArgumentParser(description="Convert WKT geometry(ies) to an ESRI Shapefile.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--wkt", help="A single WKT geometry string.")
    src.add_argument("--input", help="Path to a UTF-8 text file with one WKT per line.")
    ap.add_argument("--out", required=True, help="Output shapefile path (e.g., out.shp).")
    ap.add_argument("--epsg", type=int, default=4326, help="EPSG code for the output CRS (default: 4326).")
    ap.add_argument(
        "--split-mixed",
        action="store_true",
        help="If input contains mixed geometry types, write one shapefile per type (suffix added).",
    )
    args = ap.parse_args()

    wkts = read_wkts(args.wkt, args.input)
    geoms = load_geoms(wkts)

    if args.split_mixed:
        write_split_by_type(args.out, geoms, args.epsg)
    else:
        write_shapefile(args.out, geoms, args.epsg)


if __name__ == "__main__":
    main()
