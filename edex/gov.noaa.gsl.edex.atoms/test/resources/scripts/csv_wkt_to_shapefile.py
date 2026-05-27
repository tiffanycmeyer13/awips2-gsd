"""
csv_wkt_to_shapefile.py

Convert a CSV file with a WKT geometry column + attributes into an ESRI Shapefile.

Requirements:
  pip install shapely fiona pandas

Example:
  csv_wkt_to_shapefile.py \
      --input data.csv --wkt_col geometry \
      --out output.shp --epsg 4326

  python csv_wkt_to_shapefile.py --input data.csv --wkt_col geometry --out polygons.shp --epsg 4326

Example CSV file:
  id,name,value,geometry
  1,A,100.0,"POLYGON ((0 0, 1 0, 1 1, 0 1, 0 0))"
  2,B,200.5,"POLYGON ((2 0, 3 0, 3 1, 2 1, 2 0))"
  3,C,300.0,"POLYGON ((4 0, 5 0, 5 1, 4 1, 4 0))"

"""
import argparse
import os

import pandas as pd
import fiona
from fiona.crs import from_epsg
from shapely import wkt as shapely_wkt
from shapely.geometry import mapping


def ensure_outpath(path: str) -> str:
    parent = os.path.dirname(os.path.abspath(path))
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    if not path.lower().endswith(".shp"):
        path = f"{path}.shp"
    return path


def detect_fiona_type(value):
    """Map Python types to Fiona schema types."""
    if isinstance(value, (int, bool)):
        return "int"
    if isinstance(value, float):
        return "float"
    return "str"


def main():
    ap = argparse.ArgumentParser(description="Convert CSV with WKT to shapefile")
    ap.add_argument("--input", required=True, help="Input CSV file (must contain WKT column).")
    ap.add_argument("--wkt_col", required=True, help="Name of the column containing WKT geometries.")
    ap.add_argument("--out", required=True, help="Output shapefile path.")
    ap.add_argument("--epsg", type=int, default=4326, help="EPSG code (default: 4326).")
    args = ap.parse_args()

    # Read CSV
    df = pd.read_csv(args.input)

    if args.wkt_col not in df.columns:
        raise ValueError(f"WKT column '{args.wkt_col}' not found in CSV.")

    # Convert WKT column to shapely geometries
    geoms = []
    for idx, w in enumerate(df[args.wkt_col], start=1):
        try:
            geom = shapely_wkt.loads(w)
        except Exception as e:
            raise ValueError(f"Invalid WKT at row {idx}: {e}") from e
        geoms.append(geom)

    # Drop WKT column to leave only attributes
    attrs_df = df.drop(columns=[args.wkt_col])

    # Build schema from first row
    sample = attrs_df.iloc[0].to_dict() if not attrs_df.empty else {}
    schema = {
        "geometry": geoms[0].geom_type,
        "properties": {k: detect_fiona_type(v) for k, v in sample.items()},
    }

    crs = from_epsg(args.epsg) if args.epsg else None
    out_path = ensure_outpath(args.out)

    with fiona.open(out_path, "w", driver="ESRI Shapefile", schema=schema, crs=crs) as dst:
        for i, (geom, row) in enumerate(zip(geoms, attrs_df.to_dict("records")), start=1):
            dst.write({
                "geometry": mapping(geom),
                "properties": row
            })

    print(f"Wrote {len(geoms)} features to {out_path}")


if __name__ == "__main__":
    main()

