import sqlite3
import sys
import unicodedata
from pathlib import Path

import pandas as pd

from config import (
    ALIAS_CIUDAD, ALIAS_DEPARTAMENTO, ALIAS_REGION, COLUMNAS, DB_PATH, PROCESSED_DIR,
    RAW_DIR, SECTORES, SOURCES, SQL_DIR,
)


def quitar_acentos(texto: str) -> str:
    if texto is None:
        return ""
    normal = unicodedata.normalize("NFKD", str(texto))
    return "".join(c for c in normal if not unicodedata.combining(c))


def canon(valor) -> str:
    limpio = quitar_acentos(str(valor)).upper().replace(".", "").replace(",", " ").strip()
    return " ".join(limpio.split())


def limpiar_texto(valor) -> str:
    return " ".join(str(valor).strip().split())


def parse_monto(valor):
    """Convierte textos como '$ 100.59', '-$ 0.82' (billones de COP) a float."""
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return None
    s = str(valor).replace("\u00a0", " ").strip()
    if s == "" or s.lower() == "nan":
        return None
    negativo = "-" in s
    s = s.replace("$", "").replace(" ", "").replace("-", "").replace(",", "")
    if s == "":
        return None
    try:
        numero = float(s)
    except ValueError:
        return None
    return -numero if negativo else numero


def normalizar_ciudad(valor) -> str:
    clave = canon(valor)
    if clave in ALIAS_CIUDAD:
        return ALIAS_CIUDAD[clave]
    return limpiar_texto(valor).title()


def normalizar_departamento(valor) -> str:
    clave = canon(valor)
    if clave in ALIAS_DEPARTAMENTO:
        return ALIAS_DEPARTAMENTO[clave]
    return limpiar_texto(valor).title()


def normalizar_region(valor) -> str:
    clave = canon(valor)
    if clave in ALIAS_REGION:
        return ALIAS_REGION[clave]
    return limpiar_texto(valor).title()


def normalizar_ciiu(valor) -> str | None:
    if valor is None or (isinstance(valor, float) and pd.isna(valor)):
        return None
    try:
        numero = int(float(valor))
    except (ValueError, TypeError):
        return None
    return f"{numero:04d}"


def cargar_empresas() -> pd.DataFrame:
    ruta = RAW_DIR / SOURCES["empresas"]["file"]
    print(f"  Leyendo {ruta.name}...")
    df = pd.read_csv(ruta, encoding="utf-8-sig", low_memory=False)
    df = df.rename(columns=COLUMNAS)
    df = df[[c for c in COLUMNAS.values() if c in df.columns]].copy()
    print(f"  Registros crudos: {len(df):,}")

    df["anio"] = pd.to_numeric(df["anio"], errors="coerce")
    df = df[df["anio"].notna()].copy()
    df["anio"] = df["anio"].astype(int)

    df["nit"] = pd.to_numeric(df["nit"], errors="coerce")
    df = df[df["nit"].notna()].copy()
    df["nit"] = df["nit"].astype("int64")

    for campo in ["ingresos", "ganancia", "activos", "pasivos", "patrimonio"]:
        df[campo] = df[campo].map(parse_monto)

    df["razon_social"] = df["razon_social"].map(limpiar_texto)
    df["supervisor"] = df["supervisor"].map(limpiar_texto)
    df["macrosector"] = df["macrosector"].map(lambda v: limpiar_texto(v).upper())
    df["ciiu"] = df["ciiu"].map(normalizar_ciiu)
    df["ciudad"] = df["ciudad"].map(normalizar_ciudad)
    df["departamento"] = df["departamento"].map(normalizar_departamento)
    df["region"] = df["region"].map(normalizar_region)

    df = df.drop_duplicates(subset=["nit", "anio"], keep="first").copy()
    print(f"  Empresas-anio validos: {len(df):,}")
    return df


def construir_dims(df: pd.DataFrame):
    # Sector
    presentes = [s for s in SECTORES if s in set(df["macrosector"])]
    restantes = sorted(set(df["macrosector"]) - set(presentes))
    orden_sector = presentes + restantes
    dim_sector = pd.DataFrame({
        "id_sector": range(1, len(orden_sector) + 1),
        "macrosector": orden_sector,
    })
    mapa_sector = dict(zip(dim_sector["macrosector"], dim_sector["id_sector"]))

    # Geografia
    geo = (df[["region", "departamento", "ciudad"]]
           .drop_duplicates()
           .sort_values(["region", "departamento", "ciudad"])
           .reset_index(drop=True))
    geo.insert(0, "id_geografia", range(1, len(geo) + 1))
    dim_geografia = geo
    mapa_geo = {(r.region, r.departamento, r.ciudad): r.id_geografia
                for r in dim_geografia.itertuples()}

    # Empresa (atributos del anio mas reciente para cada NIT)
    ultimo = df.sort_values("anio").drop_duplicates(subset=["nit"], keep="last")
    ultimo = ultimo.sort_values("razon_social").reset_index(drop=True)
    ultimo.insert(0, "id_empresa", range(1, len(ultimo) + 1))
    dim_empresa = pd.DataFrame({
        "id_empresa": ultimo["id_empresa"],
        "nit": ultimo["nit"],
        "razon_social": ultimo["razon_social"],
        "supervisor": ultimo["supervisor"],
        "ciiu": ultimo["ciiu"],
        "id_sector": ultimo["macrosector"].map(mapa_sector),
        "id_geografia": [mapa_geo[(r.region, r.departamento, r.ciudad)]
                         for r in ultimo.itertuples()],
    })
    mapa_empresa = dict(zip(dim_empresa["nit"], dim_empresa["id_empresa"]))

    # Anio
    dim_anio = pd.DataFrame({"anio": sorted(df["anio"].unique())})

    # Hechos
    fact = pd.DataFrame({
        "id_empresa": df["nit"].map(mapa_empresa),
        "anio": df["anio"],
        "ingresos": df["ingresos"].round(2),
        "ganancia": df["ganancia"].round(2),
        "activos": df["activos"].round(2),
        "pasivos": df["pasivos"].round(2),
        "patrimonio": df["patrimonio"].round(2),
    }).reset_index(drop=True)
    fact.insert(0, "id_registro", range(1, len(fact) + 1))
    fact["id_empresa"] = fact["id_empresa"].astype("int64")
    fact["anio"] = fact["anio"].astype("int64")
    return fact, dim_empresa, dim_sector, dim_geografia, dim_anio


def escribir_db(fact, dim_empresa, dim_sector, dim_geografia, dim_anio) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    esquema = (SQL_DIR / "01_schema.sql").read_text(encoding="utf-8")
    conexion = sqlite3.connect(DB_PATH)
    conexion.executescript(esquema)
    dim_sector.to_sql("dim_sector", conexion, if_exists="append", index=False)
    dim_geografia.to_sql("dim_geografia", conexion, if_exists="append", index=False)
    dim_anio.to_sql("dim_anio", conexion, if_exists="append", index=False)
    dim_empresa.to_sql("dim_empresa", conexion, if_exists="append", index=False)
    fact.to_sql("fact_financiero", conexion, if_exists="append", index=False)
    conexion.commit()
    conexion.execute("ANALYZE;")
    conexion.commit()
    conexion.close()
    print(f"  Base de datos: {DB_PATH.name} ({DB_PATH.stat().st_size / 1e6:.1f} MB)")


def exportar_para_powerbi(fact, dim_empresa, dim_sector, dim_geografia, dim_anio) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    dim_sector.to_csv(PROCESSED_DIR / "dim_sector.csv", index=False, encoding="utf-8-sig")
    dim_geografia.to_csv(PROCESSED_DIR / "dim_geografia.csv", index=False, encoding="utf-8-sig")
    dim_anio.to_csv(PROCESSED_DIR / "dim_anio.csv", index=False, encoding="utf-8-sig")
    dim_empresa.to_csv(PROCESSED_DIR / "dim_empresa.csv", index=False, encoding="utf-8-sig")
    fact.to_csv(PROCESSED_DIR / "fact_financiero.csv", index=False, encoding="utf-8-sig")
    fact.head(5000).to_csv(PROCESSED_DIR / "fact_financiero_muestra.csv", index=False, encoding="utf-8-sig")
    print(f"  CSV exportados en {PROCESSED_DIR}")


def main() -> None:
    print("ETL - construccion del modelo estrella (empresas de Colombia)")
    df = cargar_empresas()
    fact, dim_empresa, dim_sector, dim_geografia, dim_anio = construir_dims(df)
    escribir_db(fact, dim_empresa, dim_sector, dim_geografia, dim_anio)
    exportar_para_powerbi(fact, dim_empresa, dim_sector, dim_geografia, dim_anio)
    print(f"  Hechos: {len(fact):,} | empresas: {len(dim_empresa):,} | "
          f"sectores: {len(dim_sector)} | geografias: {len(dim_geografia):,} | anios: {len(dim_anio)}")
    print("ETL finalizado.")


if __name__ == "__main__":
    sys.exit(main())
