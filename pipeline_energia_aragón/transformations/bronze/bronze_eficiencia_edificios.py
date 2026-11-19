from pyspark import pipelines as dp
from pyspark.sql import functions as F

# Zona de aterrizaje con los CSV crudos descargados de Kaggle
# (dataset: isabelocastillo/eficiencia-energetica-edificios-de-aragon)
LANDING_ZONE = "/Volumes/workspace/energia_aragon/landign_zone"


@dp.table(
    name="bronze_eficiencia_edificios",
    comment=(
        "Bronce: certificados de eficiencia energetica de edificios de Aragon, "
        "ingesta cruda vía Auto Loader desde la zona de aterrizaje."
    ),
)
def bronze_eficiencia_edificios():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.inferColumnTypes", "true")
        .option("header", "true")
        .load(LANDING_ZONE)
        .withColumn("_archivo_origen", F.col("_metadata.file_path"))
        .withColumn("_fecha_ingesta", F.current_timestamp())
    )
