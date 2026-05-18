import json
import sys

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

from config import OUTPUT_DIR, PARQUET_DIR, PARQUET_COLS, FILES, INCLUDED_STATUSES
from load import load_all
from aggregate import spending_by_period, spending_by_category, spending_by_vendor_size


def write_csv(df: pd.DataFrame, name: str) -> None:
    path = OUTPUT_DIR / name
    df.to_csv(path, index=False, encoding="utf-8-sig")
    size_kb = path.stat().st_size / 1024
    print(f"  {name} — {len(df):,} rows, {size_kb:.1f} KB")


def write_parquet(df: pd.DataFrame, tipo: str) -> None:
    subset = (
        df[df["tipo_compra"] == tipo][PARQUET_COLS]
        .sort_values(["comuna_canonica", "anio_semestre"])
        .reset_index(drop=True)
    )
    path = PARQUET_DIR / f"{tipo}.parquet"
    pq.write_table(
        pa.Table.from_pandas(subset, preserve_index=False),
        path,
        compression="snappy",
        row_group_size=50_000,
    )
    size_mb = path.stat().st_size / 1_048_576
    print(f"  {tipo}.parquet — {len(subset):,} rows, {size_mb:.1f} MB")


def write_metadata(df: pd.DataFrame) -> None:
    meta = {
        "generated_at": pd.Timestamp.now().isoformat(),
        "status_filter": {
            "included": INCLUDED_STATUSES,
            "excluded": ["Enviada a Proveedor", "En Proceso", "Solicitud de Cancelacion"],
            "rationale": (
                "Only orders with confirmed spend are included. "
                "Aceptada = accepted by supplier. "
                "Recepcion Conforme = goods/services received and approved."
            ),
        },
        "amount_field": {
            "column": "MontoNetoItemCLP",
            "description": "Net amount per line item, normalised to CLP. Item-level — additive across rows without double-counting.",
            "note": "MontoTotalOC is an order-level total repeated on every line item; summing it causes double-counting.",
            "tax": "Pre-tax (IVA not included).",
        },
        "compra_agil_filter": {
            "column": "ProveedorSeleccionado",
            "rule": "Rows where ProveedorSeleccionado = NO are excluded (losing quotes, not actual spend).",
            "rut_mismatch": "Orders where ProveedorRUT != RUTProveedorCotizacion are flagged in logs but kept.",
        },
        "semestre_range": {
            "start": str(df["anio_semestre"].min()),
            "end": str(df["anio_semestre"].max()),
            "note": "compra_agil starts 2020-1; other modalities start 2015-1.",
        },
        "municipalities": sorted(df["comuna_canonica"].dropna().unique().tolist()),
        "modalities": sorted(df["tipo_compra"].unique().tolist()),
        "sources": list(FILES.values()),
    }
    path = OUTPUT_DIR / "metadata.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f"  metadata.json written")


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PARQUET_DIR.mkdir(parents=True, exist_ok=True)

    df = load_all()

    print("Writing pre-aggregated CSVs ...")
    write_csv(spending_by_period(df),     "spending_by_period.csv")
    write_csv(spending_by_category(df),   "spending_by_category.csv")
    write_csv(spending_by_vendor_size(df),"spending_by_vendor_size.csv")

    print("\nWriting Parquet files ...")
    for tipo in FILES:
        write_parquet(df, tipo)

    print("\nWriting metadata ...")
    write_metadata(df)

    print("\nDone. All outputs in:", OUTPUT_DIR)


if __name__ == "__main__":
    sys.exit(main())
