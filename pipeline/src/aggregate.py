import pandas as pd


def _agg(df: pd.DataFrame, dims: list[str]) -> pd.DataFrame:
    result = (
        df.groupby(dims, sort=True, dropna=False)
        .agg(
            monto_neto_clp=("MontoNetoItemCLP", "sum"),
            n_items=("MontoNetoItemCLP", "count"),
            n_ordenes=("codigoOC", "nunique"),
        )
        .reset_index()
        .rename(columns={"comuna_canonica": "municipalidad"})
    )
    result["monto_neto_clp"] = result["monto_neto_clp"].round(0).astype("int64")
    return result


def spending_by_period(df: pd.DataFrame) -> pd.DataFrame:
    return _agg(df, ["comuna_canonica", "anio_semestre", "tipo_compra"])


def spending_by_category(df: pd.DataFrame) -> pd.DataFrame:
    return _agg(df, ["comuna_canonica", "anio_semestre", "tipo_compra", "RubroN1"])


def spending_by_vendor_size(df: pd.DataFrame) -> pd.DataFrame:
    result = (
        df.groupby(["comuna_canonica", "anio_semestre", "tipo_compra", "TamanoProveedor"], sort=True, dropna=False)
        .agg(
            monto_neto_clp=("MontoNetoItemCLP", "sum"),
            n_items=("MontoNetoItemCLP", "count"),
            n_ordenes=("codigoOC", "nunique"),
            n_proveedores=("ProveedorRUT", "nunique"),
        )
        .reset_index()
        .rename(columns={"comuna_canonica": "municipalidad"})
    )
    result["monto_neto_clp"] = result["monto_neto_clp"].round(0).astype("int64")
    return result
