import pandas as pd
from config import INPUT_DIR, INCLUDED_STATUSES, BASE_COLS, COMPRA_AGIL_EXTRA_COLS, FILES


def load_and_filter(tipo: str) -> pd.DataFrame:
    fname = FILES[tipo]
    path  = INPUT_DIR / fname
    usecols = BASE_COLS + (COMPRA_AGIL_EXTRA_COLS if tipo == "compra_agil" else [])

    print(f"[{tipo}] Reading {fname} ...")
    df = pd.read_csv(path, encoding="utf-8-sig", usecols=usecols, low_memory=False)
    print(f"[{tipo}] {len(df):,} rows loaded")

    # --- EstadoOC filter -------------------------------------------------
    before = len(df)
    df = df[df["EstadoOC"].isin(INCLUDED_STATUSES)].copy()
    dropped = before - len(df)
    print(f"[{tipo}] EstadoOC filter: {dropped:,} rows removed, {len(df):,} kept")

    # --- ProveedorSeleccionado filter (compra_agil only) -----------------
    if tipo == "compra_agil":
        before = len(df)
        df = df[df["ProveedorSeleccionado"] != "NO"].copy()
        print(f"[{tipo}] ProveedorSeleccionado filter: {before - len(df):,} rows removed, {len(df):,} kept")

        unexpected = df[df["ProveedorSeleccionado"] != "SI"]
        if not unexpected.empty:
            print(f"[{tipo}] ⚠️  {unexpected['codigoOC'].nunique():,} orders have a ProveedorSeleccionado value other than SI or NO — investigate")

        # RUT mismatch check — flag but keep
        mismatches = df[df["ProveedorRUT"] != df["RUTProveedorCotizacion"]]
        if not mismatches.empty:
            print(
                f"[{tipo}] ⚠️  RUT mismatch on {mismatches['codigoOC'].nunique():,} orders "
                f"({len(mismatches):,} rows) — ProveedorRUT != RUTProveedorCotizacion. "
                f"Rows kept but flagged."
            )
        else:
            print(f"[{tipo}] ✅ RUT check passed — no mismatches")

        df = df.drop(columns=["ProveedorSeleccionado", "RUTProveedorCotizacion"])

    # --- Amount field coercion -------------------------------------------
    df["MontoNetoItemCLP"] = pd.to_numeric(df["MontoNetoItemCLP"], errors="coerce")
    null_amounts = df["MontoNetoItemCLP"].isna().sum()
    if null_amounts:
        print(f"[{tipo}] ⚠️  {null_amounts:,} rows with null MontoNetoItemCLP — coercing to 0")
    df["MontoNetoItemCLP"] = df["MontoNetoItemCLP"].fillna(0)

    # --- Null check on key dimensions ------------------------------------
    for col in ["RubroN1", "TamanoProveedor", "comuna_canonica", "anio_semestre"]:
        n = df[col].isna().sum()
        if n:
            print(f"[{tipo}] ⚠️  {n:,} null values in '{col}' — rows kept, will appear as NaN in aggregations")

    df["tipo_compra"] = tipo
    df = df.drop(columns=["EstadoOC"])
    print(f"[{tipo}] Done — {len(df):,} rows ready\n")
    return df


def load_all() -> pd.DataFrame:
    frames = [load_and_filter(tipo) for tipo in FILES]
    combined = pd.concat(frames, ignore_index=True)
    print(f"Combined: {len(combined):,} total rows across {combined['tipo_compra'].nunique()} modalities\n")
    return combined
