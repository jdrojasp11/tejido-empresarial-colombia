import re
import sqlite3
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from config import DB_PATH, FIGURES_DIR, PROCESSED_DIR, SQL_DIR

plt.rcParams.update({
    "figure.dpi": 120,
    "savefig.bbox": "tight",
    "font.size": 10,
    "axes.titlesize": 13,
    "axes.titleweight": "bold",
    "axes.grid": True,
    "grid.alpha": 0.3,
    "figure.facecolor": "white",
})

AZUL = "#1f4e79"
ROJO = "#c0392b"
NARANJA = "#e67e22"
VERDE = "#2e7d32"
GRIS = "#7f8c8d"
PALETA = [AZUL, NARANJA, ROJO, VERDE, "#8e44ad", GRIS, "#16a085", "#d35400"]


def leer_consultas(ruta: Path) -> dict:
    texto = ruta.read_text(encoding="utf-8")
    bloques = re.split(r"^--\s*name:\s*", texto, flags=re.MULTILINE)[1:]
    consultas = {}
    for bloque in bloques:
        nombre = bloque.splitlines()[0].strip()
        sql = "\n".join(bloque.splitlines()[1:]).strip().rstrip(";")
        consultas[nombre] = sql
    return consultas


def ejecutar_todas(conexion, consultas: dict) -> dict:
    return {nombre: pd.read_sql_query(sql, conexion) for nombre, sql in consultas.items()}


def _guardar(fig, nombre: str) -> None:
    FIGURES_DIR.mkdir(parents=True, exist_ok=True)
    fig.savefig(FIGURES_DIR / nombre, dpi=120)
    plt.close(fig)
    print(f"  Figura -> reports/figures/{nombre}")


def _corto(texto: str, n: int = 30) -> str:
    return texto if len(texto) <= n else texto[: n - 1] + "…"


def fig_tendencia(datos: dict) -> None:
    df = datos["resumen_anual"]
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar(df["anio"].astype(str), df["ingresos"], color=AZUL, alpha=0.85, label="Ingresos")
    ax.set_title("Ingresos operacionales de las 10.000 empresas mas grandes")
    ax.set_xlabel("Anio")
    ax.set_ylabel("Billones de COP")
    ax2 = ax.twinx()
    ax2.plot(df["anio"].astype(str), df["margen_pct"], marker="o", color=NARANJA, linewidth=2, label="Margen")
    ax2.set_ylabel("Margen neto (%)", color=NARANJA)
    ax2.grid(False)
    ax.legend(loc="upper left")
    ax2.legend(loc="upper right")
    _guardar(fig, "fig1_tendencia_anual.png")


def fig_top_empresas(datos: dict) -> None:
    df = datos["top_empresas"].head(12).sort_values("ingresos")
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh([_corto(r) for r in df["razon_social"]], df["ingresos"], color=AZUL, alpha=0.85)
    ax.set_title("Top 12 empresas por ingresos operacionales (ultimo anio)")
    ax.set_xlabel("Billones de COP")
    for y, v in zip(range(len(df)), df["ingresos"]):
        ax.text(v + 0.5, y, f"{v:,.2f}".replace(",", "."), va="center", fontsize=8, color=GRIS)
    _guardar(fig, "fig2_top_empresas.png")


def fig_por_sector(datos: dict) -> None:
    df = datos["por_sector"].sort_values("ingresos")
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.barh(df["macrosector"], df["ingresos"], color=VERDE, alpha=0.9)
    ax.set_title("Ingresos por macrosector (ultimo anio)")
    ax.set_xlabel("Billones de COP")
    for y, v in zip(range(len(df)), df["ingresos"]):
        ax.text(v + 2, y, f"{v:,.0f}".replace(",", "."), va="center", fontsize=8, color=GRIS)
    _guardar(fig, "fig3_por_sector.png")


def fig_por_ciudad(datos: dict) -> None:
    df = datos["por_ciudad"].head(12).sort_values("ingresos")
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(df["ciudad"], df["ingresos"], color=NARANJA, alpha=0.9)
    ax.set_title("Top 12 ciudades por ingresos de sus grandes empresas")
    ax.set_xlabel("Billones de COP")
    _guardar(fig, "fig4_por_ciudad.png")


def fig_margen_sector(datos: dict) -> None:
    df = datos["por_sector"].sort_values("margen_pct")
    fig, ax = plt.subplots(figsize=(9, 4.8))
    colores = [ROJO if v < 0 else AZUL for v in df["margen_pct"]]
    ax.barh(df["macrosector"], df["margen_pct"], color=colores, alpha=0.9)
    ax.set_title("Margen neto agregado por macrosector")
    ax.set_xlabel("Margen neto (%)")
    ax.axvline(0, color=GRIS, linewidth=1)
    _guardar(fig, "fig5_margen_sector.png")


def fig_endeudamiento(datos: dict) -> None:
    df = datos["por_sector"].sort_values("endeudamiento_pct")
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.barh(df["macrosector"], df["endeudamiento_pct"], color="#8e44ad", alpha=0.9)
    ax.set_title("Endeudamiento (pasivos / activos) por macrosector")
    ax.set_xlabel("Pasivos / Activos (%)")
    _guardar(fig, "fig6_endeudamiento.png")


def fig_concentracion(datos: dict) -> None:
    df = datos["concentracion"].copy()
    df["pct_ingresos"] = df["ingresos_acumulados"] / df["ingresos_total"].iloc[0] * 100
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(df["posicion"], df["pct_ingresos"], color=AZUL, linewidth=2.4)
    ax.fill_between(df["posicion"], df["pct_ingresos"], color=AZUL, alpha=0.15)
    for pos in (10, 100, 500):
        fila = df[df["posicion"] == pos]
        if not fila.empty:
            x = fila["posicion"].iloc[0]
            y = fila["pct_ingresos"].iloc[0]
            ax.scatter([x], [y], color=ROJO, zorder=5)
            ax.annotate(f"Top {pos}: {y:.0f}%", (x, y), textcoords="offset points",
                        xytext=(6, -12), fontsize=8, color=ROJO)
    ax.set_title("Concentracion del ingreso: cuota acumulada de las mayores empresas")
    ax.set_xlabel("Numero de empresas (ordenadas por ingresos, ultimo anio)")
    ax.set_ylabel("% acumulado de ingresos")
    ax.set_xlim(0, int(df["posicion"].max()) + 1)
    ax.set_ylim(0, 100)
    _guardar(fig, "fig7_concentracion.png")


def guardar_kpis(datos: dict) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    for nombre, tabla in datos.items():
        tabla.to_csv(PROCESSED_DIR / f"kpi_{nombre}.csv", index=False, encoding="utf-8-sig")
    print(f"  KPIs exportados en {PROCESSED_DIR} (kpi_*.csv)")


def imprimir_resumen(datos: dict) -> None:
    print("\n================= RESUMEN EJECUTIVO =================")
    res = datos["resumen_anual"]
    ult = res.iloc[-1]
    print(f"Anios analizados: {int(res['anio'].min())} - {int(res['anio'].max())}")
    print(f"Ultimo anio ({int(ult['anio'])}): {int(ult['empresas']):,} empresas | "
          f"ingresos {ult['ingresos']:,.2f} billones | margen {ult['margen_pct']:.2f}%")

    print("\nEvolucion de ingresos totales (billones):")
    print(res[["anio", "empresas", "ingresos", "ganancia", "margen_pct"]].to_string(index=False))

    print("\nTop 5 empresas por ingresos (ultimo anio):")
    print(datos["top_empresas"].head(5)[["razon_social", "macrosector", "ingresos", "margen_pct"]]
          .to_string(index=False))

    print("\nIngresos por macrosector (ultimo anio):")
    print(datos["por_sector"][["macrosector", "empresas", "ingresos", "margen_pct", "endeudamiento_pct"]]
          .to_string(index=False))

    print("\nTop 5 ciudades por ingresos:")
    print(datos["por_ciudad"].head(5)[["ciudad", "empresas", "ingresos"]].to_string(index=False))

    conc = datos["concentracion"]
    for pos in (10, 100):
        fila = conc[conc["posicion"] == pos]
        if not fila.empty:
            share = fila["ingresos_acumulados"].iloc[0] / fila["ingresos_total"].iloc[0] * 100
            print(f"Concentracion: Top {pos} empresas = {share:.1f}% de los ingresos totales")
    print("=====================================================")


def main() -> None:
    if not DB_PATH.exists():
        raise SystemExit("No existe data/warehouse.db. Ejecuta primero el ETL (run_all.py).")
    consultas = leer_consultas(SQL_DIR / "02_kpi_queries.sql")
    conexion = sqlite3.connect(DB_PATH)
    try:
        datos = ejecutar_todas(conexion, consultas)
    finally:
        conexion.close()

    print("Generando figuras y KPIs...")
    fig_tendencia(datos)
    fig_top_empresas(datos)
    fig_por_sector(datos)
    fig_por_ciudad(datos)
    fig_margen_sector(datos)
    fig_endeudamiento(datos)
    fig_concentracion(datos)
    guardar_kpis(datos)
    imprimir_resumen(datos)
    print("\nAnalitica finalizada.")


if __name__ == "__main__":
    sys.exit(main())
