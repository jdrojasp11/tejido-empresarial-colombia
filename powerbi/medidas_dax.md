# Medidas DAX del modelo (Power BI)

Crear las medidas sobre la tabla `fact_financiero`. El modelo sigue un esquema en
estrella (`fact_financiero` + `dim_empresa`, `dim_sector`, `dim_geografia`,
`dim_anio`). Las cifras están en **billones de COP**.

> **Nota de nomenclatura:** Analysis Services **no distingue mayúsculas**; una
> medida llamada `Ingresos` chocaría con la columna `ingresos`. Por eso la medida
> se llama `Ingresos Totales`.

## Medidas del modelo (6)

```DAX
Ingresos Totales = SUM ( fact_financiero[ingresos] )

Utilidad = SUM ( fact_financiero[ganancia] )

Margen = DIVIDE ( [Utilidad], [Ingresos Totales] )

ROA = DIVIDE ( [Utilidad], SUM ( fact_financiero[activos] ) )

Endeudamiento = DIVIDE ( SUM ( fact_financiero[pasivos] ), SUM ( fact_financiero[activos] ) )

NumEmpresas = DISTINCTCOUNT ( fact_financiero[id_empresa] )
```

## Medidas adicionales sugeridas

```DAX
ROE = DIVIDE ( [Utilidad], SUM ( fact_financiero[patrimonio] ) )

Activos = SUM ( fact_financiero[activos] )

Ingreso Promedio por Empresa = DIVIDE ( [Ingresos Totales], [NumEmpresas] )
```

## Concentración y ranking (curva de Pareto)

```DAX
Ranking Empresa por Ingresos =
RANKX ( ALL ( dim_empresa[razon_social] ), [Ingresos Totales], , DESC )

% del Ingreso Total =
DIVIDE ( [Ingresos Totales], CALCULATE ( [Ingresos Totales], ALL ( dim_empresa ) ) )
```

## Variación anual

Marca `dim_anio` como dimensión temporal (relación con `fact_financiero[anio]`).

```DAX
Ingresos Anio Anterior =
CALCULATE ( [Ingresos Totales], SAMEPERIODLASTYEAR ( dim_anio[anio] ) )

Variacion Anual % =
DIVIDE ( [Ingresos Totales] - [Ingresos Anio Anterior], [Ingresos Anio Anterior] )
```

> Nota: para usar funciones de inteligencia de tiempo, conviene tener una tabla
> de fechas continua; alternativamente, compara directamente por `anio`.

## Etiqueta dinámica de riesgo (opcional)

```DAX
Nivel de Riesgo =
SWITCH (
    TRUE (),
    [Endeudamiento] >= 0.65, "Alto",
    [Endeudamiento] >= 0.50, "Medio",
    "Bajo"
)
```
