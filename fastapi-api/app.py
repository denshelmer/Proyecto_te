"""
=============================================================================
 API REST - Análisis de Microemprendimientos con Machine Learning
 Endpoints: Ingestión / Procesamiento / Consulta de Datos
 Stack: FastAPI + PostgreSQL + Scikit-Learn (Random Forest)
=============================================================================
"""

import os
import time
import json
import io
import csv
import joblib
import pandas as pd
import psycopg2
import psycopg2.extras

from datetime import datetime
from typing import List, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status, UploadFile, File, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, validator

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURACION
# ─────────────────────────────────────────────────────────────────────────────
DB_URL = os.getenv("DATABASE_URL", "postgres://postgres:root@db:5432/microemprendimientos_db")
MODEL_PATH = os.getenv("MODEL_PATH", "/model/modelo_riesgo_definitivo.pkl")

# ─────────────────────────────────────────────────────────────────────────────
# CONEXION A POSTGRES
# ─────────────────────────────────────────────────────────────────────────────
def get_conn():
    return psycopg2.connect(DB_URL)


def init_tables():
    """Crea las tablas de ingestión y procesamiento si no existen."""
    sql = """
    CREATE TABLE IF NOT EXISTS api_data_ingest (
        id          SERIAL PRIMARY KEY,
        ingresos    DECIMAL(12,2) NOT NULL,
        costos_fijos    DECIMAL(12,2) NOT NULL,
        costos_variables DECIMAL(12,2) NOT NULL,
        fuente      VARCHAR(20) DEFAULT 'json',
        procesado   BOOLEAN DEFAULT FALSE,
        creado_en   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );

    CREATE TABLE IF NOT EXISTS api_data_processed (
        id              SERIAL PRIMARY KEY,
        ingest_id       INT REFERENCES api_data_ingest(id),
        total_costos    DECIMAL(12,2),
        saldo_neto      DECIMAL(12,2),
        margen_utilidad DECIMAL(6,2),
        punto_equilibrio DECIMAL(12,2),
        nivel_riesgo    VARCHAR(10),
        procesado_en    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    with get_conn() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()


# ─────────────────────────────────────────────────────────────────────────────
# LIFESPAN — startup/shutdown moderno (FastAPI 0.100+)
# ─────────────────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicializa tablas al arrancar el servidor."""
    max_retries = 10
    for attempt in range(max_retries):
        try:
            init_tables()
            print(f"[DB] Tablas inicializadas correctamente.")
            break
        except Exception as e:
            print(f"[DB] Intento {attempt+1}/{max_retries} — esperando DB... ({e})")
            time.sleep(3)
    yield
    print("[API] Servidor detenido.")


# ─────────────────────────────────────────────────────────────────────────────
# FASTAPI APP
# ─────────────────────────────────────────────────────────────────────────────
app = FastAPI(
    lifespan=lifespan,
    title="🚀 API Big Data / ML — Microemprendimientos",
    description=(
        "API REST desarrollada con **FastAPI** para la ingestión, "
        "procesamiento (ETL + ML) y consulta de datos financieros de microemprendimientos.\n\n"
        "Permite gestionar el flujo completo de datos desde su recepción hasta la predicción "
        "del **nivel de riesgo de sostenibilidad** usando un modelo de **Random Forest** entrenado "
        "con datos reales de mercado.\n\n"
        "**Stack:** Python · FastAPI · PostgreSQL · Scikit-Learn · Docker"
    ),
    version="1.0.0",
    contact={"name": "Proyecto Tecnologías Emergentes"},
    license_info={"name": "MIT"},
)


# ─────────────────────────────────────────────────────────────────────────────
# MODELOS PYDANTIC
# ─────────────────────────────────────────────────────────────────────────────
class RegistroIngesta(BaseModel):
    """Estructura de un registro financiero a ingestar."""
    ingresos: float = Field(..., gt=0, description="Ingresos mensuales totales del emprendimiento (USD)")
    costos_fijos: float = Field(..., ge=0, description="Gastos que no varían con el volumen de ventas (USD)")
    costos_variables: float = Field(..., ge=0, description="Gastos proporcionales al volumen de producción (USD)")

    class Config:
        json_schema_extra = {
            "example": {
                "ingresos": 15000.00,
                "costos_fijos": 5000.00,
                "costos_variables": 4000.00
            }
        }


class LoteIngesta(BaseModel):
    """Permite ingestar múltiples registros a la vez."""
    registros: List[RegistroIngesta] = Field(..., min_length=1, description="Lista de 1 a N registros financieros.")


class ResultadoProcesado(BaseModel):
    """Estructura del resultado tras el procesamiento ML + ETL."""
    id: int
    ingest_id: int
    ingresos: float
    costos_fijos: float
    costos_variables: float
    total_costos: float
    saldo_neto: float
    margen_utilidad: float
    punto_equilibrio: float
    nivel_riesgo: str
    procesado_en: datetime


# ─────────────────────────────────────────────────────────────────────────────
# UTILIDADES
# ─────────────────────────────────────────────────────────────────────────────
def cargar_modelo():
    """Carga el modelo ML desde el archivo .pkl."""
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(f"Modelo no encontrado en: {MODEL_PATH}")
    return joblib.load(MODEL_PATH)


def predecir_riesgo(modelo, ingresos: float, total_costos: float) -> str:
    """Aplica el modelo Random Forest para clasificar el nivel de riesgo."""
    df_entrada = pd.DataFrame([[ingresos, total_costos]], columns=['Sales', 'COGS'])
    pred = modelo.predict(df_entrada)[0]
    return {2: "ALTO", 1: "MEDIO", 0: "BAJO"}.get(int(pred), "DESCONOCIDO")


# ─────────────────────────────────────────────────────────────────────────────
# ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

@app.get(
    "/",
    summary="Estado del servidor",
    tags=["Health"]
)
def root():
    """Verifica que la API esté activa y retorna información básica del sistema."""
    return {
        "api": "Análisis de Microemprendimientos — Big Data / ML",
        "version": "1.0.0",
        "status": "✅ Activo",
        "docs": "/docs",
        "endpoints": {
            "ingestión": "POST /api/data/ingest",
            "procesamiento": "POST /api/data/process",
            "resultados": "GET /api/data/results"
        }
    }


# ─────────────────────────────────────────────────────────────────────────────
# 1. INGESTIÓN
# ─────────────────────────────────────────────────────────────────────────────
@app.post(
    "/api/data/ingest",
    status_code=status.HTTP_201_CREATED,
    summary="1. Ingestión de datos financieros (JSON)",
    tags=["1. Ingestión"],
    response_description="Confirmación de registro almacenado."
)
def ingest_json(payload: RegistroIngesta):
    """
    **Ingestión de un solo registro** financiero vía JSON.

    - Recibe ingresos, costos fijos y costos variables.
    - Valida que los valores sean positivos (Pydantic).
    - Persiste el registro en la tabla `api_data_ingest` de PostgreSQL.
    - Marca el registro como **pendiente** de procesamiento.
    """
    t0 = time.time()
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """INSERT INTO api_data_ingest (ingresos, costos_fijos, costos_variables, fuente)
                       VALUES (%s, %s, %s, 'json') RETURNING id, creado_en""",
                    (payload.ingresos, payload.costos_fijos, payload.costos_variables)
                )
                row = cur.fetchone()
            conn.commit()

        latencia = round((time.time() - t0) * 1000, 2)
        return {
            "mensaje": "✅ Registro ingestado exitosamente",
            "id": row[0],
            "creado_en": row[1].isoformat(),
            "estado": "pendiente",
            "latencia_ms": latencia
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al ingestar datos: {str(e)}")


@app.post(
    "/api/data/ingest/batch",
    status_code=status.HTTP_201_CREATED,
    summary="1b. Ingestión de lote de registros (JSON)",
    tags=["1. Ingestión"],
    response_description="Confirmación de múltiples registros almacenados."
)
def ingest_batch(payload: LoteIngesta):
    """
    **Ingestión de múltiples registros** en una sola petición (batch).

    - Acepta entre 1 y N registros en formato JSON.
    - Inserta todos los registros en un solo comando SQL para eficiencia.
    """
    t0 = time.time()
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                valores = [
                    (r.ingresos, r.costos_fijos, r.costos_variables, 'batch')
                    for r in payload.registros
                ]
                psycopg2.extras.execute_values(
                    cur,
                    "INSERT INTO api_data_ingest (ingresos, costos_fijos, costos_variables, fuente) VALUES %s RETURNING id",
                    valores
                )
                ids = [row[0] for row in cur.fetchall()]
            conn.commit()

        latencia = round((time.time() - t0) * 1000, 2)
        return {
            "mensaje": f"✅ {len(ids)} registros ingestados exitosamente",
            "ids": ids,
            "estado": "pendiente",
            "latencia_ms": latencia
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error en ingestión batch: {str(e)}")


@app.post(
    "/api/data/ingest/csv",
    status_code=status.HTTP_201_CREATED,
    summary="1c. Ingestión de archivo CSV",
    tags=["1. Ingestión"],
    response_description="Confirmación de registros extraídos del CSV e ingresados."
)
async def ingest_csv(file: UploadFile = File(..., description="Archivo CSV con columnas: ingresos, costos_fijos, costos_variables")):
    """
    **Ingestión desde un archivo CSV**.

    - Acepta archivos `.csv` con encabezados `ingresos`, `costos_fijos`, `costos_variables`.
    - Valida que las columnas requeridas existan.
    - Ingesta todos los registros válidos del archivo.
    """
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Solo se aceptan archivos .csv")

    t0 = time.time()
    try:
        content = await file.read()
        df = pd.read_csv(io.BytesIO(content))

        required = {"ingresos", "costos_fijos", "costos_variables"}
        missing = required - set(df.columns.str.lower())
        if missing:
            raise HTTPException(status_code=422, detail=f"Columnas faltantes en CSV: {missing}")

        df.columns = df.columns.str.lower()
        df = df[list(required)].dropna()

        with get_conn() as conn:
            with conn.cursor() as cur:
                valores = [
                    (float(row["ingresos"]), float(row["costos_fijos"]), float(row["costos_variables"]), "csv")
                    for _, row in df.iterrows()
                ]
                psycopg2.extras.execute_values(
                    cur,
                    "INSERT INTO api_data_ingest (ingresos, costos_fijos, costos_variables, fuente) VALUES %s RETURNING id",
                    valores
                )
                ids = [r[0] for r in cur.fetchall()]
            conn.commit()

        latencia = round((time.time() - t0) * 1000, 2)
        return {
            "mensaje": f"✅ {len(ids)} registros del CSV ingestados correctamente",
            "ids": ids,
            "estado": "pendiente",
            "latencia_ms": latencia
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar CSV: {str(e)}")


# ─────────────────────────────────────────────────────────────────────────────
# 2. PROCESAMIENTO (ETL + ML)
# ─────────────────────────────────────────────────────────────────────────────
@app.post(
    "/api/data/process",
    summary="2. Procesamiento ETL + ML (predice riesgo)",
    tags=["2. Procesamiento"],
    response_description="Registros procesados con métricas financieras y nivel de riesgo predicho."
)
def process_data(limite: int = Query(default=100, ge=1, le=1000, description="Número máximo de registros pendientes a procesar.")):
    """
    **Procesamiento de datos pendientes de ingestión.**

    Ejecuta el pipeline completo:
    1. **Extracción:** Recupera registros con `procesado = FALSE` de `api_data_ingest`.
    2. **Transformación (ETL):** Calcula métricas financieras derivadas:
       - Total de costos, saldo neto, margen de utilidad, punto de equilibrio.
    3. **Predicción ML:** Aplica el modelo **Random Forest** para clasificar el riesgo (BAJO, MEDIO, ALTO).
    4. **Carga:** Persiste los resultados en `api_data_processed` y marca el registro como procesado.
    """
    t0 = time.time()
    try:
        modelo = cargar_modelo()
    except FileNotFoundError as e:
        raise HTTPException(status_code=503, detail=str(e))

    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                # Extracción
                cur.execute(
                    "SELECT * FROM api_data_ingest WHERE procesado = FALSE ORDER BY creado_en ASC LIMIT %s",
                    (limite,)
                )
                pendientes = cur.fetchall()

            if not pendientes:
                return {"mensaje": "⚠️ No hay registros pendientes de procesamiento.", "procesados": 0}

            resultados = []
            with conn.cursor() as cur:
                for rec in pendientes:
                    ingresos = float(rec["ingresos"])
                    cf = float(rec["costos_fijos"])
                    cv = float(rec["costos_variables"])

                    # Transformación (ETL)
                    total_costos = cf + cv
                    saldo_neto = ingresos - total_costos
                    margen = round((saldo_neto / ingresos * 100) if ingresos > 0 else 0.0, 2)
                    punto_eq = total_costos

                    # Predicción ML
                    nivel_riesgo = predecir_riesgo(modelo, ingresos, total_costos)

                    # Carga
                    cur.execute(
                        """INSERT INTO api_data_processed
                           (ingest_id, total_costos, saldo_neto, margen_utilidad, punto_equilibrio, nivel_riesgo)
                           VALUES (%s, %s, %s, %s, %s, %s) RETURNING id""",
                        (rec["id"], total_costos, saldo_neto, margen, punto_eq, nivel_riesgo)
                    )
                    processed_id = cur.fetchone()[0]

                    cur.execute("UPDATE api_data_ingest SET procesado = TRUE WHERE id = %s", (rec["id"],))

                    resultados.append({
                        "processed_id": processed_id,
                        "ingest_id": rec["id"],
                        "ingresos": ingresos,
                        "total_costos": total_costos,
                        "saldo_neto": saldo_neto,
                        "margen_utilidad_pct": margen,
                        "punto_equilibrio": punto_eq,
                        "nivel_riesgo": nivel_riesgo
                    })

            conn.commit()

        latencia = round((time.time() - t0) * 1000, 2)
        return {
            "mensaje": f"✅ {len(resultados)} registros procesados con éxito",
            "procesados": len(resultados),
            "latencia_ms": latencia,
            "resultados": resultados
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el procesamiento: {str(e)}")


# ─────────────────────────────────────────────────────────────────────────────
# 3. DESPLIEGUE / CONSULTA
# ─────────────────────────────────────────────────────────────────────────────
@app.get(
    "/api/data/results",
    summary="3. Consulta de datos procesados",
    tags=["3. Despliegue"],
    response_description="Lista de registros procesados con predicción de riesgo."
)
def get_results(
    limite: int = Query(default=50, ge=1, le=500, description="Número de resultados a retornar."),
    riesgo: Optional[str] = Query(default=None, description="Filtrar por nivel de riesgo: BAJO, MEDIO, ALTO")
):
    """
    **Consulta de resultados procesados.**

    - Retorna registros de `api_data_processed` junto con los datos originales de ingestión.
    - Permite filtrar por nivel de riesgo (`BAJO`, `MEDIO`, `ALTO`).
    - Incluye métricas financieras calculadas durante el procesamiento ETL.
    """
    t0 = time.time()
    try:
        filtro_riesgo = ""
        params = []
        if riesgo:
            filtro_riesgo = "WHERE p.nivel_riesgo = %s"
            params.append(riesgo.upper())
        params.append(limite)

        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(f"""
                    SELECT
                        p.id,
                        p.ingest_id,
                        i.ingresos,
                        i.costos_fijos,
                        i.costos_variables,
                        i.fuente,
                        p.total_costos,
                        p.saldo_neto,
                        p.margen_utilidad,
                        p.punto_equilibrio,
                        p.nivel_riesgo,
                        p.procesado_en
                    FROM api_data_processed p
                    JOIN api_data_ingest i ON i.id = p.ingest_id
                    {filtro_riesgo}
                    ORDER BY p.procesado_en DESC
                    LIMIT %s
                """, params)
                rows = cur.fetchall()

        latencia = round((time.time() - t0) * 1000, 2)
        return {
            "total": len(rows),
            "latencia_ms": latencia,
            "filtro_riesgo": riesgo,
            "datos": [dict(r) for r in rows]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al consultar resultados: {str(e)}")


@app.get(
    "/api/data/metrics",
    summary="3b. Métricas agregadas del sistema",
    tags=["3. Despliegue"],
    response_description="Estadísticas y métricas del pipeline completo."
)
def get_metrics():
    """
    **Métricas de calidad y rendimiento del sistema.**

    Retorna estadísticas agregadas de todo el pipeline:
    - Totales de registros ingestados vs. procesados.
    - Distribución por nivel de riesgo.
    - Estadísticas descriptivas (promedios, máximos, mínimos) de los registros procesados.
    """
    t0 = time.time()
    try:
        with get_conn() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute("SELECT COUNT(*) AS total, COUNT(*) FILTER (WHERE procesado) AS procesados FROM api_data_ingest")
                totales = cur.fetchone()

                cur.execute("""
                    SELECT nivel_riesgo, COUNT(*) AS cantidad
                    FROM api_data_processed
                    GROUP BY nivel_riesgo
                    ORDER BY cantidad DESC
                """)
                dist_riesgo = cur.fetchall()

                cur.execute("""
                    SELECT
                        ROUND(AVG(ingresos)::numeric, 2)        AS prom_ingresos,
                        ROUND(AVG(total_costos)::numeric, 2)    AS prom_costos,
                        ROUND(AVG(saldo_neto)::numeric, 2)      AS prom_saldo_neto,
                        ROUND(AVG(margen_utilidad)::numeric, 2) AS prom_margen_pct,
                        ROUND(MAX(ingresos)::numeric, 2)        AS max_ingresos,
                        ROUND(MIN(ingresos)::numeric, 2)        AS min_ingresos
                    FROM api_data_processed p
                    JOIN api_data_ingest i ON i.id = p.ingest_id
                """)
                estadisticas = cur.fetchone()

        latencia = round((time.time() - t0) * 1000, 2)
        return {
            "latencia_ms": latencia,
            "totales": dict(totales),
            "distribucion_riesgo": [dict(r) for r in dist_riesgo],
            "estadisticas_financieras": dict(estadisticas) if estadisticas else {}
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al obtener métricas: {str(e)}")
