from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
REPORTS_DIR = BASE_DIR / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
SQL_DIR = BASE_DIR / "sql"
DB_PATH = DATA_DIR / "warehouse.db"

SOURCES = {
    "empresas": {
        "url": "https://www.datos.gov.co/resource/6cat-2gcs.csv",
        "params": {"$limit": 200000},
        "file": "empresas_mas_grandes.csv",
        "dataset": "10.000 Empresas mas Grandes del Pais",
        "entity": "Superintendencia de Sociedades",
        "page": "https://www.datos.gov.co/Comercio-Industria-y-Turismo/10-000-Empresas-mas-Grandes-del-Pa-s/6cat-2gcs",
        "license": "CC-BY-SA-4.0",
    },
}

# Columnas originales (nombres de campo Socrata) -> nombres internos
COLUMNAS = {
    "nit": "nit",
    "raz_n_social": "razon_social",
    "supervisor": "supervisor",
    "regi_n": "region",
    "departamento_domicilio": "departamento",
    "ciudad_domicilio": "ciudad",
    "ciiu": "ciiu",
    "macrosector": "macrosector",
    "ingresos_operacionales": "ingresos",
    "ganancia_p_rdida": "ganancia",
    "total_activos": "activos",
    "total_pasivos": "pasivos",
    "total_patrimonio": "patrimonio",
    "a_o_de_corte": "anio",
}

SECTORES = ["MINERO", "MANUFACTURA", "COMERCIO", "CONSTRUCCIÓN", "AGROPECUARIO", "SERVICIOS"]

# Alias para unificar variantes de nombre de municipio (clave sin acentos y en mayusculas)
ALIAS_CIUDAD = {
    "BOGOTA": "Bogotá D.C.",
    "BOGOTA DC": "Bogotá D.C.",
    "BOGOTA D.C.": "Bogotá D.C.",
    "MEDELLIN": "Medellín",
    "CALI": "Cali",
    "BARRANQUILLA": "Barranquilla",
    "CARTAGENA": "Cartagena",
    "BUCARAMANGA": "Bucaramanga",
    "CUCUTA": "Cúcuta",
    "PEREIRA": "Pereira",
    "MANIZALES": "Manizales",
    "SANTA MARTA": "Santa Marta",
    "VILLAVICENCIO": "Villavicencio",
    "PASTO": "Pasto",
    "MONTERIA": "Montería",
    "IBAGUE": "Ibagué",
    "NEIVA": "Neiva",
    "ARMENIA": "Armenia",
    "POPAYAN": "Popayán",
    "SINCELEJO": "Sincelejo",
    "VALLEDUPAR": "Valledupar",
    "RIOHACHA": "Riohacha",
    "YUMBO": "Yumbo",
    "ITAGUI": "Itagüí",
    "ENVIGADO": "Envigado",
    "SABANETA": "Sabaneta",
    "RIONEGRO": "Rionegro",
    "COTA": "Cota",
    "FUNZA": "Funza",
    "SIN INFORMACION": "Sin información",
}

# Alias de departamento (clave sin acentos y en mayusculas)
ALIAS_DEPARTAMENTO = {
    "BOGOTA": "Bogotá D.C.",
    "BOGOTA D.C.": "Bogotá D.C.",
    "BOGOTA DC": "Bogotá D.C.",
    "VALLE": "Valle del Cauca",
    "VALLE DEL CAUCA": "Valle del Cauca",
    "ATLANTICO": "Atlántico",
    "BOLIVAR": "Bolívar",
    "CORDOBA": "Córdoba",
    "NARINO": "Nariño",
    "NORTE DE SANTANDER": "Norte de Santander",
    "BOYACA": "Boyacá",
    "CAQUETA": "Caquetá",
    "CHOCO": "Chocó",
    "GUAJIRA": "La Guajira",
    "LA GUAJIRA": "La Guajira",
    "QUINDIO": "Quindío",
    "RISARALDA": "Risaralda",
    "SAN ANDRES": "San Andrés y Providencia",
    "SAN ANDRES Y PROVIDENCIA": "San Andrés y Providencia",
    "ARCHIPIELAGO DE SAN ANDRES": "San Andrés y Providencia",
    "VAUPES": "Vaupés",
    "VICHADA": "Vichada",
    "GUAINIA": "Guainía",
    "AMAZONAS": "Amazonas",
    "ANTIOQUIA": "Antioquia",
    "CUNDINAMARCA": "Cundinamarca",
    "SANTANDER": "Santander",
    "CALDAS": "Caldas",
    "MAGDALENA": "Magdalena",
    "META": "Meta",
    "TOLIMA": "Tolima",
    "HUILA": "Huila",
    "CAUCA": "Cauca",
    "CESAR": "Cesar",
    "CASANARE": "Casanare",
    "ARAUCA": "Arauca",
    "PUTUMAYO": "Putumayo",
    "SUCRE": "Sucre",
    "ARMENIA": "Quindío",
    "MONTERIA": "Córdoba",
    "VALLEDUPAR": "Cesar",
    "SIN INFORMACION": "Sin información",
}

# Alias de region (la etiqueta cambio entre anios: unificar el Caribe)
ALIAS_REGION = {
    "COSTA ATLANTICA": "Región Caribe",
    "REGION CARIBE": "Región Caribe",
    "OTROS": "Otros",
}

