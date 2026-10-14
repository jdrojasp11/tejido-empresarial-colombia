-- =====================================================================
-- Consultas analiticas del caso:
--   Tejido empresarial colombiano - 10.000 empresas mas grandes (2021-2025)
-- Se ejecutan desde src/analytics.py. El separador "-- name:" identifica
-- cada consulta.
-- NOTA: todas las cifras monetarias estan en BILLONES de pesos (COP).
-- =====================================================================

-- name: resumen_anual
SELECT a.anio,
       COUNT(*) AS empresas,
       ROUND(SUM(f.ingresos), 2)   AS ingresos,
       ROUND(SUM(f.ganancia), 2)   AS ganancia,
       ROUND(SUM(f.activos), 2)    AS activos,
       ROUND(SUM(f.pasivos), 2)    AS pasivos,
       ROUND(SUM(f.patrimonio), 2) AS patrimonio,
       ROUND(100.0 * SUM(f.ganancia) / NULLIF(SUM(f.ingresos), 0), 2) AS margen_pct,
       ROUND(100.0 * SUM(f.pasivos) / NULLIF(SUM(f.activos), 0), 2)   AS endeudamiento_pct
FROM fact_financiero f
JOIN dim_anio a ON a.anio = f.anio
GROUP BY a.anio
ORDER BY a.anio;

-- name: top_empresas
SELECT e.razon_social,
       s.macrosector,
       g.ciudad,
       e.nit,
       ROUND(f.ingresos, 2) AS ingresos,
       ROUND(f.ganancia, 2) AS ganancia,
       ROUND(100.0 * f.ganancia / NULLIF(f.ingresos, 0), 2) AS margen_pct,
       ROUND(100.0 * f.pasivos / NULLIF(f.activos, 0), 2)   AS endeudamiento_pct
FROM fact_financiero f
JOIN dim_empresa e  ON e.id_empresa = f.id_empresa
JOIN dim_sector s   ON s.id_sector = e.id_sector
JOIN dim_geografia g ON g.id_geografia = e.id_geografia
WHERE f.anio = (SELECT MAX(anio) FROM dim_anio)
ORDER BY f.ingresos DESC
LIMIT 25;

-- name: por_sector
SELECT s.macrosector,
       COUNT(*) AS empresas,
       ROUND(SUM(f.ingresos), 2) AS ingresos,
       ROUND(SUM(f.ganancia), 2) AS ganancia,
       ROUND(100.0 * SUM(f.ganancia)  / NULLIF(SUM(f.ingresos), 0), 2) AS margen_pct,
       ROUND(100.0 * SUM(f.ganancia)  / NULLIF(SUM(f.activos), 0), 2)  AS roa_pct,
       ROUND(100.0 * SUM(f.ganancia)  / NULLIF(SUM(f.patrimonio), 0), 2) AS roe_pct,
       ROUND(100.0 * SUM(f.pasivos)   / NULLIF(SUM(f.activos), 0), 2)  AS endeudamiento_pct
FROM fact_financiero f
JOIN dim_empresa e ON e.id_empresa = f.id_empresa
JOIN dim_sector s  ON s.id_sector = e.id_sector
WHERE f.anio = (SELECT MAX(anio) FROM dim_anio)
GROUP BY s.macrosector
ORDER BY ingresos DESC;

-- name: por_region
SELECT g.region,
       COUNT(*) AS empresas,
       ROUND(SUM(f.ingresos), 2) AS ingresos,
       ROUND(SUM(f.ganancia), 2) AS ganancia,
       ROUND(100.0 * SUM(f.ganancia) / NULLIF(SUM(f.ingresos), 0), 2) AS margen_pct
FROM fact_financiero f
JOIN dim_empresa e   ON e.id_empresa = f.id_empresa
JOIN dim_geografia g ON g.id_geografia = e.id_geografia
WHERE f.anio = (SELECT MAX(anio) FROM dim_anio)
GROUP BY g.region
ORDER BY ingresos DESC;

-- name: por_ciudad
SELECT g.ciudad,
       g.departamento,
       COUNT(*) AS empresas,
       ROUND(SUM(f.ingresos), 2) AS ingresos,
       ROUND(SUM(f.ganancia), 2) AS ganancia
FROM fact_financiero f
JOIN dim_empresa e   ON e.id_empresa = f.id_empresa
JOIN dim_geografia g ON g.id_geografia = e.id_geografia
WHERE f.anio = (SELECT MAX(anio) FROM dim_anio)
GROUP BY g.ciudad, g.departamento
ORDER BY ingresos DESC
LIMIT 20;

-- name: top_rentabilidad
SELECT e.razon_social,
       s.macrosector,
       ROUND(f.ingresos, 2) AS ingresos,
       ROUND(f.ganancia, 2) AS ganancia,
       ROUND(100.0 * f.ganancia / NULLIF(f.ingresos, 0), 2) AS margen_pct
FROM fact_financiero f
JOIN dim_empresa e ON e.id_empresa = f.id_empresa
JOIN dim_sector s  ON s.id_sector = e.id_sector
WHERE f.anio = (SELECT MAX(anio) FROM dim_anio)
  AND f.ingresos >= 1
  AND f.ganancia > 0
ORDER BY margen_pct DESC
LIMIT 15;

-- name: utilidades_perdidas
SELECT a.anio,
       SUM(CASE WHEN f.ganancia > 0 THEN 1 ELSE 0 END) AS con_utilidad,
       SUM(CASE WHEN f.ganancia < 0 THEN 1 ELSE 0 END) AS con_perdida,
       ROUND(100.0 * SUM(CASE WHEN f.ganancia < 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS pct_en_perdida,
       ROUND(SUM(CASE WHEN f.ganancia > 0 THEN f.ganancia ELSE 0 END), 2) AS utilidades,
       ROUND(SUM(CASE WHEN f.ganancia < 0 THEN f.ganancia ELSE 0 END), 2) AS perdidas
FROM fact_financiero f
JOIN dim_anio a ON a.anio = f.anio
GROUP BY a.anio
ORDER BY a.anio;

-- name: segmentos
SELECT CASE
         WHEN f.ingresos >= 10 THEN '1. Gigante (>= $10 billones)'
         WHEN f.ingresos >= 1  THEN '2. Grande ($1 - $10 billones)'
         WHEN f.ingresos >= 0.5 THEN '3. Mediana-alta ($0,5 - $1)'
         WHEN f.ingresos >= 0.1 THEN '4. Mediana ($0,1 - $0,5)'
         ELSE '5. Pequena (< $0,1)'
       END AS segmento,
       COUNT(*) AS empresas,
       ROUND(SUM(f.ingresos), 2) AS ingresos,
       ROUND(100.0 * SUM(f.ingresos) /
             (SELECT SUM(ingresos) FROM fact_financiero WHERE anio = (SELECT MAX(anio) FROM dim_anio)), 1) AS pct_ingresos
FROM fact_financiero f
WHERE f.anio = (SELECT MAX(anio) FROM dim_anio)
GROUP BY segmento
ORDER BY segmento;

-- name: por_supervisor
SELECT e.supervisor,
       COUNT(*) AS empresas,
       ROUND(SUM(f.ingresos), 2) AS ingresos,
       ROUND(SUM(f.ganancia), 2) AS ganancia
FROM fact_financiero f
JOIN dim_empresa e ON e.id_empresa = f.id_empresa
WHERE f.anio = (SELECT MAX(anio) FROM dim_anio)
GROUP BY e.supervisor
ORDER BY ingresos DESC;

-- name: concentracion
WITH base AS (
    SELECT e.razon_social, f.ingresos,
           ROW_NUMBER() OVER (ORDER BY f.ingresos DESC) AS posicion
    FROM fact_financiero f
    JOIN dim_empresa e ON e.id_empresa = f.id_empresa
    WHERE f.anio = (SELECT MAX(anio) FROM dim_anio)
)
SELECT posicion,
       razon_social,
       ROUND(ingresos, 2) AS ingresos,
       ROUND(SUM(ingresos) OVER (ORDER BY posicion), 2) AS ingresos_acumulados,
       (SELECT SUM(ingresos) FROM fact_financiero WHERE anio = (SELECT MAX(anio) FROM dim_anio)) AS ingresos_total,
       (SELECT COUNT(*) FROM fact_financiero WHERE anio = (SELECT MAX(anio) FROM dim_anio)) AS empresas_total
FROM base
WHERE posicion <= 500
ORDER BY posicion;

-- name: crecimiento_empresas
WITH primera AS (
    SELECT id_empresa, ingresos AS ingresos_inicial
    FROM fact_financiero WHERE anio = (SELECT MIN(anio) FROM dim_anio)
),
ultima AS (
    SELECT id_empresa, ingresos AS ingresos_final, ganancia AS ganancia_final
    FROM fact_financiero WHERE anio = (SELECT MAX(anio) FROM dim_anio)
)
SELECT e.razon_social,
       s.macrosector,
       ROUND(p.ingresos_inicial, 2) AS ingresos_inicial,
       ROUND(u.ingresos_final, 2)   AS ingresos_final,
       ROUND(u.ingresos_final - p.ingresos_inicial, 2) AS variacion,
       ROUND(100.0 * (u.ingresos_final - p.ingresos_inicial) / NULLIF(p.ingresos_inicial, 0), 1) AS variacion_pct
FROM primera p
JOIN ultima u    ON u.id_empresa = p.id_empresa
JOIN dim_empresa e ON e.id_empresa = p.id_empresa
JOIN dim_sector s  ON s.id_sector = e.id_sector
WHERE p.ingresos_inicial >= 1
ORDER BY variacion DESC
LIMIT 15;
