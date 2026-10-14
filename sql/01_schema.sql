PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS fact_financiero;
DROP TABLE IF EXISTS dim_empresa;
DROP TABLE IF EXISTS dim_sector;
DROP TABLE IF EXISTS dim_geografia;
DROP TABLE IF EXISTS dim_anio;

CREATE TABLE dim_sector (
    id_sector    INTEGER PRIMARY KEY,
    macrosector  TEXT NOT NULL
);

CREATE TABLE dim_geografia (
    id_geografia INTEGER PRIMARY KEY,
    region       TEXT NOT NULL,
    departamento TEXT NOT NULL,
    ciudad       TEXT NOT NULL
);

CREATE TABLE dim_anio (
    anio INTEGER PRIMARY KEY
);

CREATE TABLE dim_empresa (
    id_empresa   INTEGER PRIMARY KEY,
    nit          INTEGER NOT NULL UNIQUE,
    razon_social TEXT NOT NULL,
    supervisor   TEXT NOT NULL,
    ciiu         TEXT,
    id_sector    INTEGER NOT NULL,
    id_geografia INTEGER NOT NULL,
    FOREIGN KEY (id_sector)    REFERENCES dim_sector (id_sector),
    FOREIGN KEY (id_geografia) REFERENCES dim_geografia (id_geografia)
);

CREATE TABLE fact_financiero (
    id_registro  INTEGER PRIMARY KEY,
    id_empresa   INTEGER NOT NULL,
    anio         INTEGER NOT NULL,
    ingresos     REAL,
    ganancia     REAL,
    activos      REAL,
    pasivos      REAL,
    patrimonio   REAL,
    FOREIGN KEY (id_empresa) REFERENCES dim_empresa (id_empresa),
    FOREIGN KEY (anio)       REFERENCES dim_anio (anio)
);

CREATE INDEX idx_fact_empresa ON fact_financiero (id_empresa);
CREATE INDEX idx_fact_anio    ON fact_financiero (anio);
CREATE INDEX idx_empresa_sector ON dim_empresa (id_sector);
CREATE INDEX idx_empresa_geo    ON dim_empresa (id_geografia);
