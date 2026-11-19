from pyspark import pipelines as dp
from pyspark.sql import functions as F

# ============================================================================
# CAPA GOLD: certificados enriquecidos, listos para analítica y modelos.
#
# QUÉ HACE ESTE ARCHIVO (sin tecnicismos):
# Toma los datos limpios de la capa silver (una fila por certificado de
# edificio) y añade, para cada edificio, informacion calculada que despues
# usan los modelos y el dashboard:
#   - edad_edificio: antiguedad del edificio al emitirse el certificado.
#   - decada_construccion: decada (1900, 1930, ...) para agrupaciones.
#   - es_proyecto: TRUE si el certificado es de un proyecto (obra no
#     terminada), util para excluirlos de ciertos analisis.
#   - consumo_optimo_kwh_m2: el "modelo optimo" de eficiencia = mediana de
#     consumo de los edificios clase A del MISMO tipo de edificio. Si un
#     tipo no tiene clase A, se usa la mediana global de clase A.
#   - brecha_kwh_m2: cuanto consumo por encima del optimo (0 si ya es
#     eficiente).
#   - ahorro_potencial_kwh: energia anual que se ahorraria llevando el
#     edificio al optimo (brecha x superficie).
#
# Regla de negocio: se excluyen los consumos fuera del rango plausible
# (0, 1000] kWh/m2/año porque son errores de registro del certificado
# (310 registros con hasta 347.347 kWh/m2/año, fisicamente imposibles).
# ============================================================================


@dp.materialized_view(
    name="gold_edificios_enriquecidos",
    comment=(
        "Oro: certificados de edificios de Aragon enriquecidos por edificio: "
        "edad y decada de construccion, flag de proyecto, modelo optimo de "
        "eficiencia (mediana clase A por tipo de edificio), brecha sobre el "
        "optimo y ahorro potencial anual. Consumos fuera de (0, 1000] "
        "kWh/m2/año excluidos como errores de registro."
    ),
    cluster_by=["provincia", "tipo_edificio"],
)
@dp.expect("optimo_positivo", "consumo_optimo_kwh_m2 > 0")
@dp.expect("brecha_no_negativa", "brecha_kwh_m2 >= 0")
@dp.expect("ahorro_no_negativo", "ahorro_potencial_kwh >= 0")
def gold_edificios_enriquecidos():
    silver = spark.read.table("silver_eficiencia_edificios")

    # --- Paso 1: modelo optimo = mediana de consumo de los edificios clase A ---
    # Se calcula por tipo de edificio (arquetipo) y, como respaldo, a nivel
    # global para los tipos sin edificios clase A. Solo se usan consumos en
    # rango plausible (0, 1000] para que los errores de registro no distorsionen
    # el optimo.
    clase_a = silver.filter(
        (F.col("clasificacion_consumo") == "A")
        & (F.col("consumo_kwh_m2_anio") > 0)
        & (F.col("consumo_kwh_m2_anio") <= 1000)
    )
    optimo_por_tipo = clase_a.groupBy("tipo_edificio").agg(
        F.percentile_approx("consumo_kwh_m2_anio", 0.5, 1000).alias("optimo_tipo")
    )
    optimo_global = clase_a.agg(
        F.percentile_approx("consumo_kwh_m2_anio", 0.5, 1000).alias("optimo_global")
    )

    # --- Paso 2: atributos derivados + filtro de calidad del consumo ---
    df = (
        silver
        .filter((F.col("consumo_kwh_m2_anio") > 0) & (F.col("consumo_kwh_m2_anio") <= 1000))
        .withColumn("edad_edificio", F.col("anio_emision") - F.col("anio_construccion"))
        .withColumn(
            "decada_construccion",
            (F.floor(F.col("anio_construccion") / 10) * 10).cast("int"),
        )
        .withColumn("es_proyecto", F.col("estado_edificio").startswith("Proyecto"))
    )

    # --- Paso 3: cruza con el optimo y calcula brecha y ahorro potencial ---
    return (
        df
        .join(optimo_por_tipo, on="tipo_edificio", how="left")
        .join(optimo_global, how="cross")  # una sola fila: mediana global clase A
        .withColumn(
            "consumo_optimo_kwh_m2",
            F.coalesce("optimo_tipo", "optimo_global"),
        )
        .withColumn(
            "brecha_kwh_m2",
            F.greatest(F.col("consumo_kwh_m2_anio") - F.col("consumo_optimo_kwh_m2"), F.lit(0.0)),
        )
        .withColumn(
            "ahorro_potencial_kwh",
            F.col("brecha_kwh_m2") * F.col("superficie_m2"),
        )
        .withColumn(
            "ahorro_potencial_pct",
            F.round(100 * F.col("brecha_kwh_m2") / F.col("consumo_kwh_m2_anio"), 1),
        )
        .drop("optimo_tipo", "optimo_global")
    )