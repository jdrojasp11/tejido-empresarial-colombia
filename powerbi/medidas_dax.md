# Medidas DAX del modelo (Power BI)

Crear las medidas sobre la tabla `fact_financiero`. El modelo sigue un esquema en
estrella (`fact_financiero` + `dim_empresa`, `dim_sector`, `dim_geografia`,
`dim_anio`). Las cifras están en **billones de COP**.

## Medidas base

```DAX
Ingresos = SUM ( fact_financiero[ingresos] )

Utilidad = SUM ( fact_financiero[ganancia] )

Num Empresas = DISTINCTCOUNT ( fact_financiero[id_empresa] )
```

## Indicadores de rentabilidad y riesgo

```DAX
Margen % = DIVIDE ( [Utilidad], [Ingresos] )

ROA % = DIVIDE ( [Utilidad], SUM ( fact_financiero[activos] ) )

ROE % = DIVIDE ( [Utilidad], SUM ( fact_financiero[patrimonio] ) )

Endeudamiento % = DIVIDE ( SUM ( fact_financiero[pasivos] ), SUM ( fact_financiero[activos] ) )
```

## Tamaño

```DAX
Activos = SUM ( fact_financiero[activos] )

Ingreso Promedio por Empresa = DIVIDE ( [Ingresos], [Num Empresas] )
```

## Concentración y ranking

```DAX
Ranking Empresa por Ingresos =
RANKX ( ALL ( dim_empresa[razon_social] ), [Ingresos], , DESC )

% del Ingreso Total =
DIVIDE ( [Ingresos], CALCULATE ( [Ingresos], ALL ( dim_empresa ) ) )
```

Con `% del Ingreso Total` y un ranking se obtiene la **curva de Pareto** (cuota
acumulada de las mayores empresas).

## Variación anual

Marca `dim_anio` como dimensión temporal (relación con `fact_financiero[anio]`).

```DAX
Ingresos Anio Anterior =
CALCULATE ( [Ingresos], SAMEPERIODLASTYEAR ( dim_anio[anio] ) )

Variacion Anual % =
DIVIDE ( [Ingresos] - [Ingresos Anio Anterior], [Ingresos Anio Anterior] )
```

> Nota: para usar funciones de inteligencia de tiempo, conviene tener una tabla
> de fechas continua; alternativamente, compara directamente por `anio`.

## Etiqueta dinámica de riesgo (opcional)

```DAX
Nivel de Riesgo =
SWITCH (
    TRUE (),
    [Endeudamiento %] >= 0.65, "Alto",
    [Endeudamiento %] >= 0.50, "Medio",
    "Bajo"
)
```
