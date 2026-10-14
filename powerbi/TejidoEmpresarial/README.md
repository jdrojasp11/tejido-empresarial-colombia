# Tablero Power BI (formato PBIP)

Proyecto **Power BI** en formato **PBIP** (Power BI Project), la versión basada en
texto de un `.pbix`. Se puede abrir directamente con **Power BI Desktop** y es
ideal para control de versiones en Git.

```
TejidoEmpresarial/
├── TejidoEmpresarial.pbip                 # abrir este archivo en Power BI Desktop
├── TejidoEmpresarial.SemanticModel/       # modelo (estrella) + medidas DAX
│   ├── definition.pbism
│   └── definition/
│       ├── database.tmdl
│       ├── model.tmdl
│       ├── expressions.tmdl               # parametro RutaDatos
│       ├── relationships.tmdl
│       └── tables/*.tmdl
└── TejidoEmpresarial.Report/              # paginas y visuales del tablero
    ├── definition.pbir
    └── definition/
        ├── report.json
        └── pages/*/...
```

## Como abrirlo

1. Asegurate de haber ejecutado el pipeline (`python src/run_all.py`) para que
   existan los CSV en `data/processed/`.
2. En **Power BI Desktop**: `Archivo > Abrir` y selecciona
   `powerbi/TejidoEmpresarial/TejidoEmpresarial.pbip`.
3. Al cargar, Power BI leera los CSV usando el parametro **`RutaDatos`**.

## Cambiar la ubicacion de los datos

El modelo lee los CSV desde una ruta absoluta guardada en el parametro
**`RutaDatos`** (por defecto la carpeta del repositorio en la maquina donde se
genero). Si clonas el repo en otra ruta:

- En Power BI: `Transformar datos > Administrar parametros`, edita **`RutaDatos`**
   a la ruta de tu `data/processed`, luego `Actualizar`.

## Modelo

- `fact_financiero` -> `dim_empresa`, `dim_anio`.
- `dim_empresa` -> `dim_sector`, `dim_geografia`.

### Medidas DAX

| Medida | Descripcion |
|---|---|
| `Ingresos Totales` | Suma de ingresos operacionales (billones de COP) |
| `Utilidad` | Suma de la ganancia (perdida) neta |
| `Margen` | `Utilidad / Ingresos` |
| `ROA` | `Utilidad / Activos` |
| `Endeudamiento` | `Pasivos / Activos` |
| `NumEmpresas` | Empresas distintas (NIT) en el contexto |

## Paginas

- **Panorama general:** tarjetas de KPIs (Ingresos, Utilidad, Margen, NumEmpresas),
  evolucion anual de ingresos e ingresos por macrosector.
- **Sectores y riesgo:** ingresos por ciudad (Top N), margen y endeudamiento por
  macrosector, y composicion del numero de empresas por sector.
