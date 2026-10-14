# Diccionario de datos

Modelo en estrella construido por `src/etl.py` a partir de los datos abiertos de
la Superintendencia de Sociedades. Se materializa en SQLite (`data/warehouse.db`)
y en CSV (`data/processed/`).

**Unidad monetaria:** todas las cifras de dinero están en **billones de pesos
colombianos (COP)**, tal como las publica la fuente.

## Diagrama del modelo

```
   dim_sector          dim_geografia
         \                  /
          \                /
           \              /
            dim_empresa
                 |
                 |  (1:N)
                 |
        fact_financiero  ------  dim_anio
             (50.000)
```

## `fact_financiero` — tabla de hechos

Un registro por **empresa y año** (empresa-año).

| Campo | Tipo | Descripción |
|---|---|---|
| `id_registro` | entero | Clave subrogada del registro |
| `id_empresa` | entero | Clave a `dim_empresa` |
| `anio` | entero | Año de corte (2021–2025) |
| `ingresos` | decimal | Ingresos operacionales (billones COP) |
| `ganancia` | decimal | Ganancia (pérdida) neta (billones COP; negativo = pérdida) |
| `activos` | decimal | Total activos (billones COP) |
| `pasivos` | decimal | Total pasivos (billones COP) |
| `patrimonio` | decimal | Total patrimonio (billones COP) |

## `dim_empresa`

Una fila por **NIT** (15.032 empresas distintas). Se conservan los atributos del
año más reciente de cada empresa.

| Campo | Tipo | Descripción |
|---|---|---|
| `id_empresa` | entero | Clave subrogada |
| `nit` | entero | NIT de la sociedad (natural key) |
| `razon_social` | texto | Nombre de la sociedad |
| `supervisor` | texto | Entidad que la supervisa (Supersociedades, Superfinanciera, …) |
| `ciiu` | texto | Código CIIU a 4 dígitos (con ceros a la izquierda) |
| `id_sector` | entero | Clave a `dim_sector` |
| `id_geografia` | entero | Clave a `dim_geografia` |

## `dim_sector`

| Campo | Tipo | Descripción |
|---|---|---|
| `id_sector` | entero | Clave |
| `macrosector` | texto | COMERCIO, SERVICIOS, MANUFACTURA, MINERO, CONSTRUCCIÓN, AGROPECUARIO |

## `dim_geografia`

| Campo | Tipo | Descripción |
|---|---|---|
| `id_geografia` | entero | Clave |
| `region` | texto | Región (p. ej. Bogotá - Cundinamarca, Antioquia, Región Caribe) |
| `departamento` | texto | Departamento de domicilio |
| `ciudad` | texto | Ciudad/municipio de domicilio |

## `dim_anio`

| Campo | Tipo | Descripción |
|---|---|---|
| `anio` | entero | Año de corte (2021–2025) |

## Relaciones

| Desde | Hacia | Cardinalidad |
|---|---|---|
| `fact_financiero[id_empresa]` | `dim_empresa[id_empresa]` | Muchos a uno |
| `fact_financiero[anio]` | `dim_anio[anio]` | Muchos a uno |
| `dim_empresa[id_sector]` | `dim_sector[id_sector]` | Muchos a uno |
| `dim_empresa[id_geografia]` | `dim_geografia[id_geografia]` | Muchos a uno |

## Notas de calidad de datos (resueltas en el ETL)

- **Cifras como texto:** `ingresos` y compañía llegan como `"$ 100.59"`,
  `"-$ 0.82"`; se convierten a numérico (signo incluido).
- **CIIU sin ceros:** `610` se normaliza a `0610` (4 dígitos).
- **Región re-etiquetada:** la etiqueta `Costa Atlántica` (2021–2024) y
  `Región Caribe` (2021–2025) referencian los **mismos departamentos**; se
  unifican en `Región Caribe`. `Otros` se conserva.
- **Municipios/departamentos con variantes** (`BOGOTA`, `MEDELLIN`, uso de ciudad
  como departamento) se normalizan a un nombre canónico.
- **El top-10.000 rota cada año:** 50.000 filas = 10.000 empresas × 5 años, pero
  15.032 NIT distintos.
