from pyspark import pipelines as dp
from pyspark.sql import functions as F

# Clasificaciones validas del certificado de eficiencia energetica (A-G)
CLASIFICACIONES_VALIDAS = ["A", "B", "C", "D", "E", "F", "G"]

# Coordenadas UTM en formato "674903,68 , 4612931,37" -> doubles con punto decimal
# try_cast tolera valores corruptos (p. ej. ",") dejandolos como NULL
COORDENADA_X_UTM = F.expr(
    "try_cast(regexp_replace(get(split(Coordenadas_gps, ' , '), 0), ',', '.') AS double)"
)
COORDENADA_Y_UTM = F.expr(
    "try_cast(regexp_replace(get(split(Coordenadas_gps, ' , '), 1), ',', '.') AS double)"
)


@dp.table(
    name="silver_eficiencia_edificios",
    comment=(
        "Plata: certificados limpios y normalizados: sin duplicados exactos, "
        "clasificaciones A-G validas, anio de construccion plausible, superficie > 0 "
        "y coordenadas UTM numericas."
    ),
    cluster_by=["provincia", "municipio"],
)
@dp.expect(
    "coordenadas_utm_validas",
    "coordenada_x_utm IS NOT NULL AND coordenada_y_utm IS NOT NULL",
)
@dp.expect("emision_co2_no_negativa", "emision_co2 >= 0")
@dp.expect("consumo_no_negativo", "consumo_kwh_m2_anio >= 0")
def silver_eficiencia_edificios():
    return (
        spark.readStream.table("bronze_eficiencia_edificios")
        .select(
            F.col("Fecha_emision").cast("timestamp").alias("fecha_emision"),
            F.col("Fecha_expiracion").cast("date").alias("fecha_expiracion"),
            F.col("Emision_CO2").cast("double").alias("emision_co2"),
            F.upper(F.trim(F.col("Clasificacion_Emisiones"))).alias("clasificacion_emisiones"),
            F.col("ConsumoKWh/m2/Anio").cast("double").alias("consumo_kwh_m2_anio"),
            F.upper(F.trim(F.col("Clasificacion_consumo"))).alias("clasificacion_consumo"),
            F.trim(F.col("Tipo_edificio")).alias("tipo_edificio"),
            F.trim(F.col("Estado_edificio")).alias("estado_edificio"),
            F.col("Anio_construccion").cast("int").alias("anio_construccion"),
            F.col("Superficie_m2").cast("double").alias("superficie_m2"),
            F.initcap(F.trim(F.col("Municipio"))).alias("municipio"),
            F.upper(F.trim(F.col("Provincia"))).alias("provincia"),
            COORDENADA_X_UTM.alias("coordenada_x_utm"),
            COORDENADA_Y_UTM.alias("coordenada_y_utm"),
            F.col("Anio_emision").cast("int").alias("anio_emision"),
            F.col("Dias_hasta_expiracion").cast("int").alias("dias_hasta_expiracion"),
        )
        .filter(
            F.col("clasificacion_emisiones").isin(CLASIFICACIONES_VALIDAS)
            & F.col("clasificacion_consumo").isin(CLASIFICACIONES_VALIDAS)
            & F.col("anio_construccion").between(1800, 2026)
            & (F.col("superficie_m2") > 0)
        )
        .dropDuplicates()
    )
