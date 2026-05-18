from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INPUT_DIR    = PROJECT_ROOT.parent / "consolidados_municipales"
OUTPUT_DIR   = PROJECT_ROOT / "data" / "processed"
PARQUET_DIR  = OUTPUT_DIR / "parquet"

INCLUDED_STATUSES = ["Aceptada", "Recepcion Conforme"]

FILES = {
    "compra_agil":    "consolidado_compra_agil.csv",
    "convenio_marco": "consolidado_convenio_marco.csv",
    "licitacion":     "consolidado_licitacion.csv",
    "trato_directo":  "consolidado_trato_directo.csv",
}

# TODO: consolidado_compra_agil.csv is missing semester 2022-2 entirely.
# Re-download that semester and re-run the pipeline to fill the gap.
# The missing data causes a visible dip in the frontend narrative chart.

# Columns present in all four files
BASE_COLS = [
    "codigoOC",
    "EstadoOC",
    "MontoNetoItemCLP",
    "RubroN1",
    "TamanoProveedor",
    "ProveedorRUT",
    "anio_semestre",
    "comuna_canonica",
]

# compra_agil only — needed for ProveedorSeleccionado filter and RUT mismatch check
COMPRA_AGIL_EXTRA_COLS = ["ProveedorSeleccionado", "RUTProveedorCotizacion"]

# Columns written to Parquet (same schema across all four files for DuckDB-WASM)
PARQUET_COLS = [
    "codigoOC",
    "comuna_canonica",
    "anio_semestre",
    "tipo_compra",
    "MontoNetoItemCLP",
    "RubroN1",
    "TamanoProveedor",
    "ProveedorRUT",
]
