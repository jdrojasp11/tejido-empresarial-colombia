# Guía del tablero en Power BI

El pipeline de Python deja los datos listos para Power BI en `data/processed/`
(en formato estrella). Sigue estos pasos para construir el tablero.

## 1. Obtener los datos

Ejecuta primero el pipeline (genera los CSV y la base SQLite):

```bash
python src/run_all.py
```

Archivos generados en `data/processed/`:

| Archivo | Rol |
|---|---|
| `fact_financiero.csv` | Tabla de hechos (50.000 filas empresa-año) |
| `dim_empresa.csv` | Dimensión empresa (15.032 filas) |
| `dim_sector.csv` | Dimensión sector (6 filas) |
| `dim_geografia.csv` | Dimensión geografía (región/departamento/ciudad) |
| `dim_anio.csv` | Dimensión año (2021–2025) |

> Alternativa: conectarse a la base SQLite `data/warehouse.db` con el driver
> **ODBC SQLite** (Obtener datos > ODBC). La vía más sencilla es importar los CSV.

## 2. Cargar y modelar

1. **Obtener datos > Texto/CSV** e importa los 5 archivos de `data/processed/`.
2. En el Editor de Power Query revisa tipos: `id_*` y `anio` como **Entero**,
   `ingresos`/`ganancia`/`activos`/`pasivos`/`patrimonio` como **Decimal**,
   `ciiu` como **Texto**.
3. Crea las relaciones (Vista de modelo):

| Desde | Hacia | Cardinalidad |
|---|---|---|
| `fact_financiero[id_empresa]` | `dim_empresa[id_empresa]` | Muchos a uno |
| `fact_financiero[anio]` | `dim_anio[anio]` | Muchos a uno |
| `dim_empresa[id_sector]` | `dim_sector[id_sector]` | Muchos a uno |
| `dim_empresa[id_geografia]` | `dim_geografia[id_geografia]` | Muchos a uno |

4. Crea las medidas de `powerbi/medidas_dax.md`.

## 3. Diseño de páginas sugerido

### Página 1 - Panorama general

- **Tarjetas (KPI):** Ingresos, Utilidad, `Margen %`, Num Empresas.
- **Columnas:** Ingresos por `dim_anio[anio]` (evolución 2021–2025).
- **Barras:** Ingresos por `dim_sector[macrosector]`.

### Página 2 - Sectores y riesgo

- **Barras (Top N):** Ingresos por `dim_geografia[ciudad]`.
- **Barras:** `Margen %` por `dim_sector[macrosector]`.
- **Barras:** `Endeudamiento %` por `dim_sector[macrosector]`.
- **Donut:** Num Empresas por `dim_sector[macrosector]`.

### Página 3 - Concentración (opcional)

- **Tabla Top 20:** `razon_social`, Ingresos, Utilidad, `Margen %`.
- **Línea/área:** cuota acumulada del ingreso (Pareto).

### Página 4 - Empresas en pérdida (opcional)

- **Barras:** empresas con pérdida por año.
- **Tabla:** empresas con pérdida más grande (último año).

## 4. Formato e interacciones

- Segmentaciones globales: `anio`, `macrosector`, `region`.
- Tema visual con un color principal (ej. azul `#1F4E79`) y rojo `#C0392B` para
  pérdidas.
- Formato condicional de barras de margen (rojo si es negativo).
- Narración inteligente en la página 1.

## 5. Publicar

- Archivo > Publicar > área de trabajo.
- Para actualización automática, programa la ejecución del pipeline (Task
  Scheduler / cron) y la actualización del dataset en el servicio.
