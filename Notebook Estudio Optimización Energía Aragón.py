# Databricks notebook source
# DBTITLE 1,Fundamentación y objetivos
# MAGIC %md
# MAGIC # Estudio de Optimización Energética de Edificios de Aragón
# MAGIC
# MAGIC ## Autores
# MAGIC
# MAGIC | Autor | Autor |
# MAGIC | --- | --- |
# MAGIC | Daniel Betancur | Jordan Usuga |
# MAGIC
# MAGIC ## Introducción
# MAGIC
# MAGIC En Aragón el consumo energético de las edificaciones es de interés público e impacta diferentes esferas de la economía y del bienestar ambiental. Dicho consumo está relacionado con características puntuales de los edificios como la antigüedad, la superficie, el tipo de construcción y su ubicación. En este proyecto se usaron datos abiertos suministrados por el Gobierno de Aragón sobre el consumo y las emisiones de CO₂, con el fin de realizar un análisis exploratorio bajo la estructura medallion (bronze → silver → gold) que permita generar un modelo predictivo y de recomendaciones sobre el consumo y la eficiencia energética en la zona.
# MAGIC
# MAGIC ## Planteamiento del problema
# MAGIC
# MAGIC En Aragón los edificios presentan diferentes niveles de consumo energético debido a factores como el año de construcción, la superficie, el estado y la ubicación. Sin embargo, no hay certeza de ¿qué tan eficiente es el sistema?, de si se puede hacer una mejor regulación, o si tal vez la energía se está usando de manera adecuada en los lugares adecuados y con las características óptimas. Además, surge una nueva pregunta: ¿se podrían predecir los niveles de consumo a futuro?
# MAGIC
# MAGIC Los datos disponibles requieren procesos de limpieza, transformación y análisis antes de ser utilizados, para determinar cómo las características de los edificios de Aragón influyen en su consumo energético y, a partir de este análisis, desarrollar los modelos que permitan estimar el consumo, identificar edificios con baja eficiencia y generar recomendaciones para optimizar el uso de la energía.
# MAGIC
# MAGIC ## Objetivos
# MAGIC
# MAGIC **Objetivos generales:**
# MAGIC 1. Analizar la relación entre el consumo energético y las características estructurales, geográficas y ambientales de los edificios.
# MAGIC 2. Construir modelos que permitan estimar el consumo e identificar oportunidades de optimización energética.
# MAGIC
# MAGIC **Usabilidad del dataset:**
# MAGIC 1. **Predicción del consumo energético** de los edificios a partir de superficie, tipo de construcción, ubicación, etc.
# MAGIC 2. **Predicción de las emisiones de CO₂** de un edificio.
# MAGIC 3. **Clasificación de edificios por eficiencia energética** (letra A-G) según sus características.
# MAGIC 4. **Identificación de los factores clave** que más influyen en el consumo y las emisiones (importancia de variables).
# MAGIC 5. **Detección de anomalías**: edificios con consumo o emisiones muy distintos de lo esperado para su perfil.
# MAGIC 6. **Optimización de recursos energéticos**: priorizar dónde invertir para maximizar el ahorro.
# MAGIC 7. **Impacto de renovaciones o mejoras**: cómo se relacionan la época de construcción/estado del edificio con el consumo.
# MAGIC
# MAGIC ## Contexto de la data
# MAGIC
# MAGIC **Dimensión del problema en los datos:** el consumo medio del parque analizado es de **258,4 kWh/m²/año**, mientras que los edificios clase A del mismo tipo consumen de media entre **26 y 95 kWh/m²/año** (el óptimo alcanzable de cada arquetipo), y el **82% de los edificios** (127.375 de 154.538) está certificado en clases E a G. Ni los ciudadanos ni los gestores públicos disponen hoy de una herramienta que responda a preguntas sencillas: ¿cuánto consumiría este edificio si fuera eficiente?, ¿cuánto se ahorraría rehabilitándolo?, ¿qué edificios deben intervenirse primero y con qué medidas? Este estudio responde a esas preguntas con datos.
# MAGIC
# MAGIC ## Contexto y estructura de la información (arquitectura medallion)
# MAGIC
# MAGIC Los datos pasan por tres capas construidas en un pipeline de Lakeflow (SDP), cada una con reglas de calidad verificadas:
# MAGIC
# MAGIC * **Bronze** (179.852 filas): los datos crudos tal cual llegan del CSV (`df_limpio.csv`), con columnas de auditoría de ingesta.
# MAGIC * **Silver** (154.998 filas): limpieza — sin duplicados, solo clasificaciones A-G válidas, años de construcción (1800-2026) y superficies plausibles, coordenadas GPS UTM normalizadas.
# MAGIC * **Gold** (154.538 filas, tabla `gold_edificios_enriquecidos`): una fila por edificio enriquecida con edad, década, flag de proyecto, **óptimo de referencia (benchmark clase A por tipo)**, brecha respecto a ese óptimo y ahorro potencial. Es la capa que alimenta este estudio, los modelos y el dashboard gerencial.
# MAGIC
# MAGIC ## Contenido de este notebook (qué contiene y dónde)
# MAGIC
# MAGIC Cada celda de código abre con un recuadro **QUÉ HACE / CÓMO / RESULTADO OBTENIDO** que explica su propósito en palabras sencillas, sus pasos y el resultado real de la última ejecución. El recorrido completo es:
# MAGIC
# MAGIC | Sección | Celda | Qué responde |
# MAGIC | --- | --- | --- |
# MAGIC | Panorama general de la capa gold | 1 | ¿Cuántos edificios hay y cómo se reparten las letras A-G? |
# MAGIC | Análisis exploratorio (EDA) | 2 | ¿Cómo se distribuye el consumo y cómo se relacionan las variables? |
# MAGIC | Modelo 1: predicción del consumo | 3 | Objetivo 1: ¿cuánto consumirá un edificio? |
# MAGIC | Factores clave del consumo | 4 | Objetivo 4: ¿qué variables más influyen? |
# MAGIC | Modelo 2: predicción de emisiones de CO₂ | 5 | Objetivo 2 |
# MAGIC | Modelo 3: clasificación por letra A-G | 6 | Objetivo 3 |
# MAGIC | Detección de anomalías | 7 | Objetivo 5 |
# MAGIC | Impacto de renovaciones y mejoras | 8 | Objetivo 7 |
# MAGIC | Segmentación de edificios (K-Means) | 9 | Objetivos 6 y 10: ¿en qué "familias" se agrupan los edificios? |
# MAGIC | Modelo óptimo y brechas | 10 | Objetivo 9: ¿cuál es el consumo alcanzable por tipo? |
# MAGIC | Sugerencias de consumo por edificio | 11 | Objetivo 8 |
# MAGIC | Planes de trabajo por segmento | 12 | Objetivo 10 |
# MAGIC | Guardado de tablas gold y resumen ejecutivo | 13 | Materialización de los resultados |
# MAGIC | Conclusiones del estudio | Final | Diagnóstico, métricas, limitaciones y entregables |
# MAGIC
# MAGIC ## Entregables del estudio
# MAGIC
# MAGIC * 4 tablas gold en `workspace.energia_aragon`: `gold_resultados_optimizacion`, `gold_sugerencias_consumo`, `gold_planes_trabajo`, `gold_resumen_gerencial`.
# MAGIC * 5 modelos registrados en MLflow (experimento `Optimizacion_Energia_Aragon`): regresor de consumo, regresor de CO₂, clasificador de letra A-G, detector de anomalías y segmentador K-Means.
# MAGIC * Un **dashboard gerencial interactivo** con filtros (provincia, municipio, tipo, letra, prioridad, segmento) construido sobre las tablas gold.

# COMMAND ----------

# DBTITLE 1,Guía de lectura y variables
# MAGIC %md
# MAGIC ## Cómo leer este notebook (guía para no programadores)
# MAGIC
# MAGIC * Cada celda de código empieza con un recuadro de documentación con tres apartados:
# MAGIC   * **QUÉ HACE**: para qué sirve la celda, contado sin tecnicismos.
# MAGIC   * **CÓMO**: los pasos que sigue, uno a uno.
# MAGIC   * **RESULTADO OBTENIDO**: lo que produjo realmente al ejecutarse (tablas, gráficos, cifras).
# MAGIC * Las celdas de texto (como esta) explican cada sección para directivos y personas sin conocimientos de programación.
# MAGIC * Los modelos se registran en **MLflow** (el registro de experimentos de Databricks): cada entrenamiento queda guardado con sus métricas para poder reproducirlo y desplegarlo.
# MAGIC
# MAGIC ### Variables del modelo y control de "fuga de información"
# MAGIC
# MAGIC Para predecir el consumo **solo se usan atributos que se conocen mirando el edificio** (tipo, estado, provincia, año de construcción, edad, superficie). Las columnas que son **salidas del propio certificado** (consumo, emisiones CO₂ y las letras A-G) se excluyen como variables explicativas porque el certificado las calcula junto con el consumo: usarlas sería como "copiar la respuesta" y el modelo no aprendería nada útil para edificios nuevos.
# MAGIC
# MAGIC | Variable | Papel | Tipo |
# MAGIC | --- | --- | --- |
# MAGIC | `tipo_edificio` | Explicativa | categórica (5 niveles) |
# MAGIC | `estado_edificio` | Explicativa | categórica (4 niveles) |
# MAGIC | `provincia` | Explicativa | categórica (3 niveles) |
# MAGIC | `anio_construccion` | Explicativa | numérica |
# MAGIC | `edad_edificio` | Explicativa | numérica (derivada en gold) |
# MAGIC | `superficie_m2` | Explicativa | numérica |
# MAGIC | `consumo_kwh_m2_anio` | **Objetivo de la regresión 1** | numérica (kWh/m²/año) |
# MAGIC | `emision_co2` | **Objetivo de la regresión 2** | numérica (kg CO₂/m²/año) |
# MAGIC | `clasificacion_consumo` | **Objetivo del clasificador** | categórica A-G |
# MAGIC
# MAGIC Excluidas como explicativas (fuga): `consumo_kwh_m2_anio`, `emision_co2`, `clasificacion_consumo`, `clasificacion_emisiones` (salidas del certificado); `municipio` (713 niveles, se usa en agregaciones y el dashboard, no en los modelos).

# COMMAND ----------

# DBTITLE 1,Carga gold y panorama
# ============================================================================
# CELDA 1 — CARGA DE DATOS (CAPA GOLD) Y PANORAMA GENERAL
# ----------------------------------------------------------------------------
# QUÉ HACE: Lee la tabla gold (los certificados ya limpios y enriquecidos) y
# muestra un panorama general: cuántos edificios hay, cómo se reparten las
# letras energéticas A-G y cuánto consume cada grupo de media.
#
# CÓMO:
# 1. spark.table(...) conecta con la tabla gold del pipeline.
# 2. .count() cuenta los edificios.
# 3. groupBy("clasificacion_consumo") agrupa por letra y calcula cuántos
#    edificios hay por letra, su consumo medio y su mediana (el valor
#    "típico": la mitad de los edificios consume menos que la mediana).
#
# RESULTADO OBTENIDO: 154.538 edificios. Reparto por letra: A 1.415 (0,9%),
# B 1.970, C 6.169, D 17.609, E 86.419 (el 55,9%), F 17.393, G 23.563.
# El consumo medio crece de A (38,4) a G (430,9) y las emisiones de 9,0
# a 92,1 kg CO₂/m²/año: la letra resume fielmente el desempeño del edificio.
# ============================================================================

from pyspark.sql import functions as F

GOLD = "workspace.energia_aragon.gold_edificios_enriquecidos"
df_gold = spark.table(GOLD)

n_gold = df_gold.count()
print(f"Edificios en la capa gold: {n_gold:,}")

display(
    df_gold.groupBy("clasificacion_consumo")
    .agg(
        F.count("*").alias("n_edificios"),
        F.round(F.mean("consumo_kwh_m2_anio"), 1).alias("consumo_medio"),
        F.round(F.percentile_approx("consumo_kwh_m2_anio", 0.5), 1).alias("mediana_consumo"),
        F.round(F.mean("emision_co2"), 1).alias("emision_media"),
    )
    .orderBy("clasificacion_consumo")
)

# COMMAND ----------

# DBTITLE 1,EDA visualizaciones
# ============================================================================
# CELDA 2 — ANÁLISIS EXPLORATORIO: GRÁFICOS Y RELACIONES ENTRE VARIABLES
# ----------------------------------------------------------------------------
# QUÉ HACE: Dibuja los datos para entenderlos "a simple vista": cómo se
# distribuye el consumo, cuánto consume cada clase energética, y cómo se
# relaciona el consumo con el año de construcción y la superficie.
#
# CÓMO:
# 1. Pasa los datos a pandas (una copia pequeña en memoria) y dibuja 4
#    gráficos con matplotlib: histograma del consumo, cajas por letra A-G,
#    dispersión año-consumo (con la media por década) y superficie-consumo.
# 2. Calcula las correlaciones: un número entre -1 y +1 que indica si dos
#    variables se mueven juntas (edad +, año -, superficie casi 0) y
#    comprueba que emisiones y consumo van de la mano (misma física).
#
# RESULTADO OBTENIDO: distribución asimétrica del consumo (mediana ~223,
# media 258); cajas por letra claramente escalonadas de A a G; el consumo
# medio por década cae de ~300-330 (pre-1960) a 145 (2010) y 74 (2020).
# Correlaciones: corr(año, consumo) = -0,294 | corr(edad) = +0,288 |
# corr(superficie) = +0,012 | corr(emisiones CO₂, consumo) = +0,910 (misma física).
# ============================================================================

import matplotlib.pyplot as plt

pdf_viz = df_gold.select(
    "clasificacion_consumo", "consumo_kwh_m2_anio", "emision_co2",
    "anio_construccion", "superficie_m2",
).toPandas()

fig, axes = plt.subplots(2, 2, figsize=(14, 9))
CLASES = list("ABCDEFG")

axes[0, 0].hist(pdf_viz["consumo_kwh_m2_anio"], bins=60, color="#4C72B0", edgecolor="white")
axes[0, 0].set_title("Distribución del consumo (kWh/m²/año)")
axes[0, 0].set_xlabel("kWh/m²/año")

axes[0, 1].boxplot(
    [pdf_viz.loc[pdf_viz.clasificacion_consumo == c, "consumo_kwh_m2_anio"] for c in CLASES],
    tick_labels=CLASES, showfliers=False,
)
axes[0, 1].set_title("Consumo por clase energética")
axes[0, 1].set_ylabel("kWh/m²/año")

smp = pdf_viz.sample(5000, random_state=42)
axes[1, 0].scatter(smp["anio_construccion"], smp["consumo_kwh_m2_anio"], s=4, alpha=0.25, color="#55A868")
por_decada = smp.assign(decada=(smp["anio_construccion"] // 10) * 10).groupby("decada")["consumo_kwh_m2_anio"].mean()
axes[1, 0].plot(por_decada.index, por_decada.values, color="crimson", lw=2, label="media por década")
axes[1, 0].set_title("Consumo vs año de construcción")
axes[1, 0].set_xlabel("Año de construcción")
axes[1, 0].set_ylabel("kWh/m²/año")
axes[1, 0].legend()

axes[1, 1].scatter(smp["superficie_m2"].clip(upper=2000), smp["consumo_kwh_m2_anio"], s=4, alpha=0.25, color="#C44E52")
axes[1, 1].set_title("Consumo vs superficie (recortada a 2000 m²)")
axes[1, 1].set_xlabel("Superficie (m²)")
axes[1, 1].set_ylabel("kWh/m²/año")

plt.tight_layout()
plt.show()

print("Correlaciones con el consumo (kWh/m²/año):")
for c in ["anio_construccion", "edad_edificio", "superficie_m2", "emision_co2"]:
    corr = df_gold.stat.corr(c, "consumo_kwh_m2_anio")
    print(f"  corr({c}, consumo) = {corr:+.3f}")

# COMMAND ----------

# DBTITLE 1,Sección modelos
# MAGIC %md
# MAGIC ## Modelos: predicción, clasificación, factores clave y anomalías (objetivos 1-5)
# MAGIC
# MAGIC En esta sección se entrenan los modelos de aprendizaje automático. Todos siguen la misma receta transparente:
# MAGIC
# MAGIC 1. Se separa un **20% de los edificios como "examen"** (test): el modelo nunca los ve durante el aprendizaje y se usan al final para comprobar cuánto acierta con edificios nuevos.
# MAGIC 2. Se comparan **dos modelos** en la predicción del consumo: una regresión lineal sencilla (línea base, para tener una referencia) y un **Gradient Boosting** (el "motor potente" que detecta patrones complejos). El que cometa menos error se queda.
# MAGIC 3. Cada entrenamiento queda registrado en **MLflow** con sus métricas, y el modelo final (reentrenado con el 100% de los datos) se guarda como artefacto desplegable.
# MAGIC
# MAGIC **Cómo leer las métricas:** RMSE y MAE se miden en kWh/m²/año (cuanto más bajos, mejor; el MAE es "el error típico"). R² es la fracción de la variabilidad del consumo que el modelo explica (0 a 1, con solo atributos físicos se logra ~0.21 porque el consumo real depende de muchos factores no registrados, como la calefacción o los hábitos de uso).

# COMMAND ----------

# DBTITLE 1,Modelo 1: regresión del consumo
# ============================================================================
# CELDA 3 — MODELO 1: PREDICCIÓN DEL CONSUMO ENERGÉTICO (objetivo 1)
# ----------------------------------------------------------------------------
# QUÉ HACE: Entrena dos modelos que predicen el consumo (kWh/m²/año) de un
# edificio a partir de sus atributos físicos (tipo, estado, provincia, año,
# edad, superficie), y elige el que menos se equivoca.
#
# CÓMO:
# 1. Copia a memoria (pandas) solo las columnas necesarias.
# 2. Divide: 80% de los edificios para APRENDER y 20% para EXAMEN (test).
# 3. Entrena Ridge (regresión lineal con regularización) y
#    HistGradientBoosting (árboles secuenciales que corrigen sus errores).
#    Ambos transforman internamente el consumo con log1p (la variable es
#    asimétrica) y devuelven la predicción en unidades reales.
# 4. Evalúa en el examen: RMSE, MAE y R². El mejor se reentrena con el 100%
#    de los datos y se registra en MLflow como "regresor_consumo_gold".
#
# RESULTADO OBTENIDO: gana hist_gb: RMSE=104,92 | MAE=73,50 | R²=0,223
# (ridge: 113,97 / 80,96 / 0,083). Residuo medio +19,71 y mediana +5,36
# (sesgo de subpredicción por la transformación log, documentado). Modelo
# final reentrenado con los 154.538 edificios y registrado en MLflow como
# "regresor_consumo_gold".
# ============================================================================

import gc
import warnings

warnings.filterwarnings("ignore")

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd
from mlflow.models import infer_signature
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Solo las columnas necesarias (reduce memoria y evita bloqueos del kernel)
COLS_MODELO = [
    "clasificacion_consumo", "clasificacion_emisiones", "consumo_kwh_m2_anio", "emision_co2",
    "tipo_edificio", "estado_edificio", "provincia", "anio_construccion", "superficie_m2",
    "municipio", "edad_edificio", "es_proyecto", "decada_construccion",
    "consumo_optimo_kwh_m2", "brecha_kwh_m2", "ahorro_potencial_kwh", "ahorro_potencial_pct",
]
pdf = df_gold.select(COLS_MODELO).toPandas()

FEATURES = ["tipo_edificio", "estado_edificio", "provincia", "anio_construccion", "edad_edificio", "superficie_m2"]
TARGET = "consumo_kwh_m2_anio"
CAT = ["tipo_edificio", "estado_edificio", "provincia"]
NUM = ["anio_construccion", "edad_edificio", "superficie_m2"]

X = pdf[FEATURES]
y = pdf[TARGET]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42)

# Preprocesamiento dentro del pipeline (se guarda junto al modelo): imputa
# huecos, escala números y convierte categorías en columnas 0/1
prepro = ColumnTransformer([
    ("num", Pipeline([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler())]), NUM),
    ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")), ("oh", OneHotEncoder(handle_unknown="ignore"))]), CAT),
])

def make_regressor(estimador):
    # log1p del consumo DENTRO del modelo: predict() devuelve kWh/m²/año reales
    return Pipeline([
        ("pre", prepro),
        ("m", TransformedTargetRegressor(regressor=estimador, func=np.log1p, inverse_func=np.expm1)),
    ])

mlflow.set_experiment("/Users/daniel.betancur2667@unaula.edu.co/Optimizacion_Energia_Aragon")

resultados_reg = {}
with mlflow.start_run(run_name="gold_regresion_consumo"):
    mlflow.log_param("features", FEATURES)
    mlflow.log_param("n_train", len(X_train))
    mlflow.log_param("n_test", len(X_test))
    for nombre, modelo in [
        ("ridge", make_regressor(Ridge(alpha=1.0))),
        ("hist_gb", make_regressor(HistGradientBoostingRegressor(max_iter=300, learning_rate=0.08, random_state=42))),
    ]:
        modelo.fit(X_train, y_train)
        pred = modelo.predict(X_test)
        rmse = float(np.sqrt(mean_squared_error(y_test, pred)))
        mae = float(mean_absolute_error(y_test, pred))
        r2 = float(r2_score(y_test, pred))
        resultados_reg[nombre] = {"rmse": rmse, "mae": mae, "r2": r2, "modelo": modelo}
        mlflow.log_metrics({f"{nombre}_rmse": rmse, f"{nombre}_mae": mae, f"{nombre}_r2": r2})
        print(f"{nombre:8s} RMSE={rmse:7.2f}  MAE={mae:7.2f}  R²={r2:.3f}")

mejor_reg = min(resultados_reg, key=lambda k: resultados_reg[k]["rmse"])
pred_test = resultados_reg[mejor_reg]["modelo"].predict(X_test)
residuos = y_test - pred_test
print(f"\nMejor modelo: {mejor_reg} | RMSE={resultados_reg[mejor_reg]['rmse']:.2f} | MAE={resultados_reg[mejor_reg]['mae']:.2f} | R²={resultados_reg[mejor_reg]['r2']:.3f}")
print(f"Media de residuos: {residuos.mean():+.2f} | Mediana: {residuos.median():+.2f} (sesgo de subpredicción por la transformación log)")

fig, axes = plt.subplots(1, 2, figsize=(13, 4))
axes[0].hist(residuos, bins=60, color="#8172B3", edgecolor="white")
axes[0].axvline(0, color="crimson", ls="--")
axes[0].set_title("Residuos del consumo (real − predicho)")
axes[1].scatter(pred_test, residuos, s=4, alpha=0.2, color="#8172B3")
axes[1].axhline(0, color="crimson", ls="--")
axes[1].set_title("Residuos vs predicción")
axes[1].set_xlabel("Consumo predicho (kWh/m²/año)")
plt.tight_layout()
plt.show()

# Reajuste final con TODOS los edificios y registro del artefacto desplegable
params_finales = {
    "hist_gb": HistGradientBoostingRegressor(max_iter=300, learning_rate=0.08, random_state=42),
    "ridge": Ridge(alpha=1.0),
}
modelo_final_consumo = make_regressor(params_finales[mejor_reg])
modelo_final_consumo.fit(X, y)
firma = infer_signature(X.head(100), modelo_final_consumo.predict(X.head(100)))
with mlflow.start_run(run_name="gold_regresion_consumo_final"):
    mlflow.log_param("modelo", mejor_reg)
    mlflow.log_param("n_final_fit", len(X))
    mlflow.log_metrics({k: resultados_reg[mejor_reg][k] for k in ("rmse", "mae", "r2")})
    modelo_info_consumo = mlflow.sklearn.log_model(
        modelo_final_consumo, name="regresor_consumo_gold", signature=firma, input_example=X.head(3)
    )
print("Modelo final de consumo registrado en:", modelo_info_consumo.model_uri)

# COMMAND ----------

# DBTITLE 1,Factores clave del consumo
# ============================================================================
# CELDA 4 — FACTORES CLAVE DEL CONSUMO (objetivo 4, parte 1)
# ----------------------------------------------------------------------------
# QUÉ HACE: Averigua qué características del edificio más influyen en el
# consumo, midiendo cuánto empeora la predicción si se "esconde" cada
# variable al modelo (importancia por permutación).
#
# CÓMO:
# 1. Toma 5.000 edificios del examen y, variable a variable, la baraja
#    aleatoriamente: si al barajarla el modelo se equivoca mucho más, esa
#    variable es importante.
# 2. Ordena las variables de mayor a menor influencia.
#
# RESULTADO OBTENIDO: año de construcción (0,295) > tipo de edificio (0,156)
# > superficie (0,123) > edad (0,102) > provincia (0,029) > estado (0,014).
# La ANTIGÜEDAD y el TIPO son los grandes factores: la política de
# rehabilitación debe priorizar el parque construido antes de 1980.
# ============================================================================

from sklearn.inspection import permutation_importance

idx_perm = X_test.sample(5000, random_state=42).index
perm = permutation_importance(
    resultados_reg[mejor_reg]["modelo"], X_test.loc[idx_perm], y_test.loc[idx_perm],
    n_repeats=5, random_state=42, scoring="r2",
)

factores_consumo = (
    pd.DataFrame({"variable": FEATURES, "importancia": perm.importances_mean})
    .sort_values("importancia", ascending=False)
    .round(4)
)
display(factores_consumo)
print("Interpretación: las variables de arriba son las que más explican el consumo; barajarlas hace fallar más al modelo.")

# COMMAND ----------

# DBTITLE 1,Modelo 2: regresión de CO₂
# ============================================================================
# CELDA 5 — MODELO 2: PREDICCIÓN DE EMISIONES DE CO₂ (objetivo 2)
# ----------------------------------------------------------------------------
# QUÉ HACE: Entrena un modelo equivalente al de consumo pero para predecir
# las emisiones de CO₂ (kg CO₂/m²/año) del edificio con sus atributos físicos,
# clave para iniciativas de sostenibilidad y huella de carbono.
#
# CÓMO:
# 1. Filtra emisiones plausibles (0, 2000] kg CO₂/m²/año: los valores fuera
#    son errores de registro (los errores de consumo arrastran a las
#    emisiones, que se calculan del consumo).
# 2. Divide 80/20 y entrena HistGradientBoosting con log1p del target.
# 3. Evalúa en el examen (RMSE, MAE, R²), reentrena con el 100% y registra
#    "regresor_co2_gold" en MLflow; calcula también sus factores clave.
#
# RESULTADO OBTENIDO: 154.534 edificios (4 excluidos por emisiones fuera de
# rango). RMSE=24,88 | MAE=16,63 | R²=0,198, similar al modelo de consumo
# (las emisiones derivan del consumo). Factores dominantes: año de
# construcción y edad. Modelo registrado como "regresor_co2_gold".
# ============================================================================

pdf_co2 = pdf[(pdf["emision_co2"] > 0) & (pdf["emision_co2"] <= 2000)].copy()
print(f"Edificios para el modelo de CO₂: {len(pdf_co2):,} (excluidos {len(pdf) - len(pdf_co2):,} por emisiones fuera de rango plausible)")

y_co2 = pdf_co2["emision_co2"]
X_co2 = pdf_co2[FEATURES]
X_train_co2, X_test_co2, y_train_co2, y_test_co2 = train_test_split(X_co2, y_co2, test_size=0.20, random_state=42)

modelo_co2 = make_regressor(HistGradientBoostingRegressor(max_iter=300, learning_rate=0.08, random_state=42))
modelo_co2.fit(X_train_co2, y_train_co2)
pred_co2 = modelo_co2.predict(X_test_co2)

rmse_co2 = float(np.sqrt(mean_squared_error(y_test_co2, pred_co2)))
mae_co2 = float(mean_absolute_error(y_test_co2, pred_co2))
r2_co2 = float(r2_score(y_test_co2, pred_co2))
print(f"CO₂ -> RMSE={rmse_co2:.2f} | MAE={mae_co2:.2f} | R²={r2_co2:.3f}")

idx_perm_co2 = X_test_co2.sample(5000, random_state=42).index
perm_co2 = permutation_importance(
    modelo_co2, X_test_co2.loc[idx_perm_co2], y_test_co2.loc[idx_perm_co2],
    n_repeats=5, random_state=42, scoring="r2",
)
display(
    pd.DataFrame({"variable": FEATURES, "importancia": perm_co2.importances_mean})
    .sort_values("importancia", ascending=False)
    .round(4)
)

# Reajuste final con todos los edificios plausibles y registro en MLflow
modelo_final_co2 = make_regressor(HistGradientBoostingRegressor(max_iter=300, learning_rate=0.08, random_state=42))
modelo_final_co2.fit(X_co2, y_co2)
firma_co2 = infer_signature(X_co2.head(100), modelo_final_co2.predict(X_co2.head(100)))
with mlflow.start_run(run_name="gold_regresion_co2"):
    mlflow.log_param("target", "emision_co2")
    mlflow.log_param("n_final_fit", len(X_co2))
    mlflow.log_metrics({"rmse": rmse_co2, "mae": mae_co2, "r2": r2_co2})
    modelo_info_co2 = mlflow.sklearn.log_model(
        modelo_final_co2, name="regresor_co2_gold", signature=firma_co2, input_example=X_co2.head(3)
    )
print("Modelo final de CO₂ registrado en:", modelo_info_co2.model_uri)

# COMMAND ----------

# DBTITLE 1,Modelo 3: clasificación A-G
# ============================================================================
# CELDA 6 — MODELO 3: CLASIFICACIÓN DE EDIFICIOS POR LETRA ENERGÉTICA (obj. 3)
# ----------------------------------------------------------------------------
# QUÉ HACE: Entrena un modelo que, con los atributos físicos de un edificio,
# predice su letra energética (A-G). Sirve para etiquetar edificios sin
# certificado vigente.
#
# CÓMO:
# 1. Divide 80/20 manteniendo la proporción de cada letra (split estratificado).
# 2. Entrena un Random Forest (votación de 150 "árboles que hacen preguntas")
#    con class_weight="balanced": las clases raras A (~1%), B (~1,3%) y C (~4%)
#    pesan más para que el modelo no las ignore.
# 3. Evalúa: acierto global, F1 por clase (equilibrio precisión-cobertura) y
#    matriz de confusión (dónde se confunde una letra con otra).
# 4. Reentrena con el 100% y registra "clasificador_letra_gold" en MLflow;
#    extrae además la importancia de cada variable (factores clave, obj. 4).
#
# RESULTADO OBTENIDO: accuracy 49,9% | F1 macro 0,347 | F1 ponderado 0,489.
# Mejor F1 en E (0,66) y A (0,47); confusión sobre todo entre letras vecinas
# (D↔E, E↔F/G). Las variables más determinantes de la letra: superficie
# (0,50), año de construcción (0,20) y edad (0,20). Registrado como
# "clasificador_letra_gold".
# ============================================================================

from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score, classification_report, confusion_matrix

y_cls = pdf["clasificacion_consumo"]
X_train_c, X_test_c, y_train_c, y_test_c = train_test_split(X, y_cls, test_size=0.20, random_state=42, stratify=y_cls)

clf_holdout = Pipeline([
    ("pre", prepro),
    ("m", RandomForestClassifier(n_estimators=150, class_weight="balanced", random_state=42, n_jobs=-1)),
])
clf_holdout.fit(X_train_c, y_train_c)
pred_c = clf_holdout.predict(X_test_c)

acc = float(accuracy_score(y_test_c, pred_c))
f1_macro = float(f1_score(y_test_c, pred_c, average="macro"))
f1_weighted = float(f1_score(y_test_c, pred_c, average="weighted"))
print(f"Accuracy={acc:.3f} | F1 macro={f1_macro:.3f} | F1 ponderado={f1_weighted:.3f}\n")
print(classification_report(y_test_c, pred_c, labels=CLASES, zero_division=0))

display(pd.DataFrame(
    confusion_matrix(y_test_c, pred_c, labels=CLASES),
    index=[f"real_{c}" for c in CLASES], columns=CLASES,
))

# Factores clave de la letra energética (objetivo 4, parte 2): importancia
# de cada variable (y de cada categoría) dentro del Random Forest
nombres_vars = clf_holdout.named_steps["pre"].get_feature_names_out()
importancias_clf = pd.DataFrame({
    "variable": nombres_vars,
    "importancia": clf_holdout.named_steps["m"].feature_importances_,
}).sort_values("importancia", ascending=False).head(12)
display(importancias_clf.round(4))

del clf_holdout
gc.collect()

# Reajuste final con todos los edificios (n_jobs=1: un solo hilo para no
# duplicar la memoria en el kernel) y registro en MLflow
modelo_final_letra = Pipeline([
    ("pre", prepro),
    ("m", RandomForestClassifier(n_estimators=150, class_weight="balanced", random_state=42, n_jobs=1)),
])
modelo_final_letra.fit(X, y_cls)
firma_clf = infer_signature(X.head(100), modelo_final_letra.predict(X.head(100)))
with mlflow.start_run(run_name="gold_clasificacion_letra"):
    mlflow.log_param("modelo", "RandomForestClassifier(150, balanced)")
    mlflow.log_param("n_final_fit", len(X))
    mlflow.log_metrics({"accuracy": acc, "f1_macro": f1_macro, "f1_weighted": f1_weighted})
    modelo_info_letra = mlflow.sklearn.log_model(
        modelo_final_letra, name="clasificador_letra_gold", signature=firma_clf, input_example=X.head(3)
    )
print("Clasificador final registrado en:", modelo_info_letra.model_uri)

# COMMAND ----------

# DBTITLE 1,Detección de anomalías
# ============================================================================
# CELDA 7 — DETECCIÓN DE ANOMALÍAS (objetivo 5)
# ----------------------------------------------------------------------------
# QUÉ HACE: Identifica edificios cuyo consumo (o emisiones) es muy distinto
# de lo ESPERADO para un edificio con su mismo perfil (tipo, zona, antigüedad,
# superficie). Un consumo muy superior al esperado delata ineficiencia;
# uno muy inferior puede señalar datos mal registrados o edificios ejemplares.
#
# CÓMO (puntuación por residuos robusta):
# 1. Predice el consumo de cada edificio con el modelo final y calcula el
#    residuo (real − esperado).
# 2. Convierte el residuo en una puntuación "z robusta": cuántas medianas
#    absolutas (MAD) se aleja el edificio del residuo típico. No usa la media
#    para que unos pocos extremos no contaminen la escala.
# 3. Marca como anómalo lo que supera el cuantil del 99% (~1% de edificios,
#    tasa esperada asumida al no haber confirmaciones reales), guardando la
#    puntuación continua para ordenar por gravedad.
# 4. Repite lo mismo con las emisiones de CO₂ y registra el detector en
#    MLflow como "detector_anomalias_consumo".
#
# RESULTADO OBTENIDO: umbral z robusta = 4,53 (consumo) y 5,17 (CO₂) ->
# 1.546 edificios anómalos (1,0%) en cada objetivo. Los casos extremos son
# consumos de ~986 kWh/m²/año cuando su perfil esperaba ~161 (score >10,
# "Sobrecosto inesperado"): candidatas prioritarias a auditoría.
# Detector registrado en MLflow como "detector_anomalias_consumo".
# ============================================================================

# Predicción "esperada" de consumo y emisiones para todos los edificios
pdf["consumo_predicho_kwh_m2"] = np.maximum(modelo_final_consumo.predict(pdf[FEATURES]), 0.1)
pdf["emision_predicha_kg_m2"] = np.maximum(
    modelo_final_co2.predict(pdf[FEATURES]).astype(float), 0.0
)

TASA_ESPERADA_ANOMALIAS = 0.01  # 1%: tasa asumida al no existir casos confirmados

for objetivo, col_real, col_pred, col_score, col_flag, col_tipo, col_umbral in [
    ("consumo", "consumo_kwh_m2_anio", "consumo_predicho_kwh_m2", "score_anomalia_consumo", "es_anomalia_consumo", "tipo_anomalia_consumo", "umbral_consumo"),
    ("co2", "emision_co2", "emision_predicha_kg_m2", "score_anomalia_co2", "es_anomalia_co2", "tipo_anomalia_co2", "umbral_co2"),
]:
    residuo = pdf[col_real] - pdf[col_pred]
    mediana_resid = residuo.median()
    mad = (residuo - mediana_resid).abs().median()
    score = (residuo - mediana_resid).abs() / (1.4826 * mad if mad > 0 else 1.0)
    umbral = float(score.quantile(1 - TASA_ESPERADA_ANOMALIAS))
    pdf[col_score] = score.round(2)
    pdf[col_flag] = score >= umbral
    pdf[col_tipo] = np.where(residuo > 0, "Sobrecosto inesperado", "Más eficiente de lo esperado")
    globals()[col_umbral] = umbral
    n_flag = int(pdf[col_flag].sum())
    print(f"{objetivo}: umbral z robusta={umbral:.2f} -> {n_flag:,} edificios anómalos ({100 * n_flag / len(pdf):.1f}%)")

# Histograma de puntuaciones con el umbral marcado
fig, axes = plt.subplots(1, 2, figsize=(13, 4))
axes[0].hist(pdf["score_anomalia_consumo"].clip(upper=20), bins=60, color="#8172B3", edgecolor="white")
axes[0].axvline(umbral_consumo, color="crimson", ls="--", label=f"umbral {umbral_consumo:.1f}")
axes[0].set_title("Puntuación de anomalía en consumo")
axes[0].legend()
axes[1].hist(pdf["score_anomalia_co2"].clip(upper=20), bins=60, color="#CCB974", edgecolor="white")
axes[1].axvline(umbral_co2, color="crimson", ls="--", label=f"umbral {umbral_co2:.1f}")
axes[1].set_title("Puntuación de anomalía en CO₂")
axes[1].legend()
plt.tight_layout()
plt.show()

# Los 10 casos más extremos de consumo, con su contexto
display(
    pdf[pdf["es_anomalia_consumo"]]
    .sort_values("score_anomalia_consumo", ascending=False)
    .head(10)[[
        "municipio", "provincia", "tipo_edificio", "anio_construccion", "superficie_m2",
        "clasificacion_consumo", "consumo_kwh_m2_anio", "consumo_predicho_kwh_m2",
        "score_anomalia_consumo", "tipo_anomalia_consumo",
    ]]
)

# Detector registrado en MLflow: dado un edificio, devuelve puntuación y flag
class DetectorAnomaliasConsumo(mlflow.pyfunc.PythonModel):
    """Envuelve el regresor final: predict() devuelve puntuación de anomalía y flag por edificio."""

    def __init__(self, pipeline, mediana_resid, mad, umbral):
        self.pipeline = pipeline
        self.mediana_resid = mediana_resid
        self.mad = mad
        self.umbral = umbral

    def predict(self, context, model_input, params=None):
        esperado = self.pipeline.predict(model_input)
        real = model_input["consumo_kwh_m2_anio"].to_numpy() if "consumo_kwh_m2_anio" in model_input else esperado
        residuo = real - esperado
        score = np.abs(residuo - self.mediana_resid) / (1.4826 * self.mad if self.mad > 0 else 1.0)
        return pd.DataFrame({
            "anomaly_score": score,
            "is_anomaly": (score >= self.umbral).astype(int),
        })

resid_consumo = (pdf["consumo_kwh_m2_anio"] - pdf["consumo_predicho_kwh_m2"])
mediana_resid_consumo = float(resid_consumo.median())
mad_consumo = float((resid_consumo - mediana_resid_consumo).abs().median())
detector = DetectorAnomaliasConsumo(modelo_final_consumo, mediana_resid_consumo, mad_consumo, umbral_consumo)
with mlflow.start_run(run_name="gold_detector_anomalias"):
    mlflow.log_param("tasa_esperada", TASA_ESPERADA_ANOMALIAS)
    mlflow.log_param("umbral_z_robusta", umbral_consumo)
    mlflow.log_metric("n_anomalias", int(pdf["es_anomalia_consumo"].sum()))
    mlflow.pyfunc.log_model(
        "detector_anomalias_consumo", python_model=detector,
        signature=infer_signature(
            pdf[FEATURES + ["consumo_kwh_m2_anio"]].head(100),
            detector.predict(None, pdf[FEATURES + ["consumo_kwh_m2_anio"]].head(100)),
        ),
        input_example=pdf[FEATURES + ["consumo_kwh_m2_anio"]].head(3),
    )
print("Detector de anomalías registrado en MLflow")

# COMMAND ----------

# DBTITLE 1,Impacto de renovaciones
# ============================================================================
# CELDA 8 — IMPACTO DE RENOVACIONES Y MEJORAS (objetivo 7)
# ----------------------------------------------------------------------------
# QUÉ HACE: Compara el consumo de los edificios por época de construcción y
# por estado del certificado, para ver cuánto mejora la eficiencia con las
# normas constructivas modernas y las reformas.
#
# CÓMO:
# 1. Agrupa por década de construcción y calcula el consumo medio.
# 2. Agrupa por estado (existente, obra terminada, proyecto) y consumo medio.
# 3. Dibuja el consumo medio por década: cada bajada marca un salto normativo
#    (aislamiento obligatorio desde 1979, Código Técnico 2006, etc.).
#
# LIMITACIÓN HONESTA: el dataset solo tiene 138 certificados de "Proyecto
# Reforma" y no registra el año de las reformas, así que el impacto se
# aproxima por época/estado; no es causal. Los edificios nuevos (post-2006)
# muestran el consumo alcanzable con construcción/reforma moderna.
#
# RESULTADO OBTENIDO: el consumo medio por década cae de ~300-333 (décadas
# 1800-1950) a 145,4 (2010) y 73,5 (2020): cada salto normativo se ve en los
# datos. Por estado: Existente 260,2 (153.019) | Obra terminada 68,3 |
# Proyecto reforma 148,2 (solo 136). Pre-1980: 287,8 vs post-2007: 175,1
# kWh/m²/año -> una reforma profunda moderna ahorra ~112,8 kWh/m²/año.
# ============================================================================

por_decada = (
    pdf.groupby("decada_construccion")
    .agg(n_edificios=("decada_construccion", "size"), consumo_medio=("consumo_kwh_m2_anio", "mean"))
    .round(1)
    .reset_index()
)
display(por_decada)

fig, ax = plt.subplots(figsize=(12, 4))
ax.bar(por_decada["decada_construccion"].astype(str), por_decada["consumo_medio"], color="#4C72B0")
ax.axhline(pdf["consumo_kwh_m2_anio"].mean(), color="crimson", ls="--", label="media global")
ax.set_title("Consumo medio por década de construcción (salto normativo CTE 2006)")
ax.set_xlabel("Década")
ax.set_ylabel("kWh/m²/año")
ax.legend()
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

por_estado = (
    pdf.groupby("estado_edificio")
    .agg(n_edificios=("estado_edificio", "size"), consumo_medio=("consumo_kwh_m2_anio", "mean"))
    .round(1)
)
display(por_estado)

consumo_pre_1980 = pdf.loc[pdf["anio_construccion"] < 1980, "consumo_kwh_m2_anio"].mean()
consumo_post_2007 = pdf.loc[pdf["anio_construccion"] >= 2007, "consumo_kwh_m2_anio"].mean()
print(f"Consumo medio pre-1980: {consumo_pre_1980:.1f} kWh/m²/año vs post-2007: {consumo_post_2007:.1f} kWh/m²/año")
print(f"Diferencia: {consumo_pre_1980 - consumo_post_2007:.1f} kWh/m²/año -> una reforma profunda moderna aproxima el edificio a los estándares de construcción actuales.")

# COMMAND ----------

# DBTITLE 1,Sección optimización
# MAGIC %md
# MAGIC ## Optimización: segmentación, modelo óptimo, sugerencias y planes (objetivos 6, 8, 9 y 10)
# MAGIC
# MAGIC Con los edificios caracterizados, esta sección responde a la pregunta de gestión: **¿dónde actuar primero y con qué medidas?**
# MAGIC
# MAGIC * **Segmentación (K-Means):** agrupa los edificios en "familias" con edad, tamaño, consumo y brecha parecidos, sin usar las letras energéticas, para diseñar una intervención distinta por familia. Se elige el número de grupos (k) con la **silueta**: una métrica que mide si los edificios de un grupo se parecen mucho entre sí y poco a los demás. La concordancia con la letra A-G (ARI/NMI) comprueba si la segmentación recupera la clasificación oficial sin haberla usado.
# MAGIC * **Modelo óptimo (benchmark):** ya está calculado en la capa gold: el consumo de referencia alcanzable de cada tipo de edificio (mediana de los clase A del mismo tipo). Aquí se resume la brecha y el ahorro que supone cerrarla.
# MAGIC * **Modelo de sugerencias:** un motor de reglas por edificio que, según su edad, tipo, brecha, anomalías y prioridad, asigna una **medida principal**, **medidas complementarias**, el **ahorro estimado** y la **letra objetivo alcanzable**.
# MAGIC * **Planes de trabajo:** por segmento, con número de edificios, medidas dominantes, ahorro total y horizonte temporal (P1 corto, P2 medio, P3 largo).
# MAGIC
# MAGIC La prioridad **P1/P2/P3** se asigna por terciles del ahorro potencial: los edificios que concentran el 25% de mayor ahorro son P1 (intervención inmediata).

# COMMAND ----------

# DBTITLE 1,Segmentación K-Means
# ============================================================================
# CELDA 9 — SEGMENTACIÓN DE EDIFICIOS CON K-MEANS (objetivos 6 y 10)
# ----------------------------------------------------------------------------
# QUÉ HACE: Agrupa automáticamente los 154.538 edificios en "familias"
# (segmentos) según su antigüedad, tamaño, consumo y distancia al óptimo,
# para diseñar un plan de intervención distinto por familia.
#
# CÓMO:
# 1. Construye 4 variables descriptivas (edad recortada a 0, y logaritmo de
#    superficie, consumo y brecha para domar los valores extremos) y las
#    escala para que ninguna domine por su magnitud.
# 2. Prueba k = 3 a 8 grupos en una muestra de 20.000 edificios y elige el k
#    con mejor silueta (>= 0 significa grupos bien separados).
# 3. Ajusta el modelo final con todos los edificios, asigna a cada uno su
#    segmento y comprueba (ARI/NMI, escala 0-1) cuánto coincide la
#    segmentación con la letra oficial A-G sin haberla usado para agrupar.
# 4. Perfila cada segmento y registra el segmentador en MLflow.
#
# RESULTADO OBTENIDO: k=3 con silueta 0,320 (mejor opción; k=4 dio 0,316).
# ARI=0,068 y NMI=0,166 frente a la letra oficial: la segmentación aporta
# una vista OPERATIVA distinta. S1: 90.135 edificios, 318,2 kWh/m²/año, 2.066
# GWh; S2: 8.186 edificios de gran tamaño, 285,8, 3.095 GWh (¡el mayor ahorro!);
# S3: 56.217 edificios eficientes, 158,4, 657 GWh. Segmentador registrado
# como "segmentador_kmeans_gold".
# ============================================================================

from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score, normalized_mutual_info_score
from sklearn.preprocessing import StandardScaler

X_cluster = pd.DataFrame({
    "edad": pdf["edad_edificio"].clip(lower=0),
    "log_superficie": np.log1p(pdf["superficie_m2"]),
    "log_consumo": np.log1p(pdf["consumo_kwh_m2_anio"]),
    "log_brecha": np.log1p(pdf["brecha_kwh_m2"]),
})

# Elección de k por silueta en una muestra (rápida y fiable)
muestra_cluster = X_cluster.sample(20000, random_state=42)
scaler_cluster = StandardScaler().fit(muestra_cluster)
muestra_escalada = scaler_cluster.transform(muestra_cluster)

siluetas = {}
for k in range(3, 9):
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(muestra_escalada)
    siluetas[k] = float(silhouette_score(muestra_escalada, km.labels_))
    print(f"k={k}  silueta={siluetas[k]:.3f}")
k_optimo = max(siluetas, key=siluetas.get)
print(f"\nk elegido: {k_optimo} (mejor silueta {siluetas[k_optimo]:.3f})")

# Ajuste final con todos los edificios
pipeline_segmentador = Pipeline([
    ("sc", StandardScaler()),
    ("km", KMeans(n_clusters=k_optimo, n_init=10, random_state=42)),
])
pdf["cluster"] = pipeline_segmentador.fit_predict(X_cluster)

ari_km = float(adjusted_rand_score(pdf["clasificacion_consumo"], pdf["cluster"]))
nmi_km = float(normalized_mutual_info_score(pdf["clasificacion_consumo"], pdf["cluster"]))
print(f"Concordancia con la letra oficial A-G: ARI={ari_km:.3f} | NMI={nmi_km:.3f} (sin usarla para agrupar)")

# Perfil de cada segmento: tamaño, edad media, consumo medio, brecha, ahorro
perfiles_segmentos = (
    pdf.groupby("cluster")
    .agg(
        n_edificios=("cluster", "size"),
        edad_media=("edad_edificio", "mean"),
        consumo_medio=("consumo_kwh_m2_anio", "mean"),
        brecha_media=("brecha_kwh_m2", "mean"),
        ahorro_total_gwh=("ahorro_potencial_kwh", lambda s: s.sum() / 1e6),
        letra_tipica=("clasificacion_consumo", lambda s: s.mode().iloc[0]),
    )
    .round(1)
)
display(perfiles_segmentos)

# Visualización: los segmentos proyectados en 2D (PCA), y la misma proyección
# coloreada por letra oficial para comparar
from sklearn.decomposition import PCA

muestra_pca = X_cluster.sample(5000, random_state=42)
proyeccion = PCA(n_components=2, random_state=42).fit_transform(StandardScaler().fit_transform(muestra_pca))
muestra_vis = pdf.loc[muestra_pca.index]
fig, axes = plt.subplots(1, 2, figsize=(14, 5))
axes[0].scatter(proyeccion[:, 0], proyeccion[:, 1], c=muestra_vis["cluster"], s=5, alpha=0.5, cmap="viridis")
axes[0].set_title(f"Segmentos K-Means (k={k_optimo})")
orden_letras = {c: i for i, c in enumerate(CLASES)}
axes[1].scatter(proyeccion[:, 0], proyeccion[:, 1], c=muestra_vis["clasificacion_consumo"].map(orden_letras), s=5, alpha=0.5, cmap="RdYlGn_r")
axes[1].set_title("Misma proyección coloreada por letra oficial")
plt.tight_layout()
plt.show()

with mlflow.start_run(run_name="gold_segmentacion_kmeans"):
    mlflow.log_param("k", k_optimo)
    mlflow.log_param("variables_cluster", list(X_cluster.columns))
    mlflow.log_metrics({"silueta": siluetas[k_optimo], "ari_letra": ari_km, "nmi_letra": nmi_km})
    mlflow.sklearn.log_model(pipeline_segmentador, name="segmentador_kmeans_gold")
print("Segmentador registrado en MLflow")

# COMMAND ----------

# DBTITLE 1,Modelo óptimo y brechas
# ============================================================================
# CELDA 10 — MODELO ÓPTIMO DE EFICIENCIA Y BRECHAS (objetivo 9)
# ----------------------------------------------------------------------------
# QUÉ HACE: Resume el "modelo óptimo": el consumo de referencia alcanzable
# por tipo de edificio (mediana de los clase A del mismo tipo, calculada en
# la capa gold) y cuánto se ahorraría llevando cada parque a ese nivel.
#
# CÓMO:
# 1. Agrupa por tipo de edificio: nº de edificios, consumo óptimo de
#    referencia, brecha media y ahorro total anual si se cerrara la brecha.
# 2. Ordena los municipios con mayor ahorro potencial (dónde invertir antes).
#
# RESULTADO OBTENIDO: 153.506 edificios (99,3%) están por encima de su
# óptimo de referencia. Óptimos: 25,7 (vivienda individual), 28,2 (unifamiliar),
# 31,0 (bloque), 65,9 (edificio completo), 94,7 (local). Ahorro potencial
# total: 5,818 TWh/año; el municipio más grande concentra 3.831,7 GWh
# (90.927 edificios).
# ============================================================================

resumen_optimo = (
    pdf.groupby("tipo_edificio")
    .agg(
        n_edificios=("tipo_edificio", "size"),
        consumo_optimo=("consumo_optimo_kwh_m2", "min"),
        consumo_medio=("consumo_kwh_m2_anio", "mean"),
        brecha_media=("brecha_kwh_m2", "mean"),
        pct_con_brecha=("brecha_kwh_m2", lambda s: 100 * (s > 0).mean()),
        ahorro_total_gwh=("ahorro_potencial_kwh", lambda s: s.sum() / 1e6),
    )
    .round(1)
)
display(resumen_optimo)

top_municipios = (
    pdf.groupby("municipio")
    .agg(
        n_edificios=("municipio", "size"),
        ahorro_total_gwh=("ahorro_potencial_kwh", lambda s: s.sum() / 1e6),
    )
    .sort_values("ahorro_total_gwh", ascending=False)
    .head(10)
    .round(1)
)
display(top_municipios)

n_con_brecha = int((pdf["brecha_kwh_m2"] > 0).sum())
print(f"Edificios por encima de su óptimo de referencia: {n_con_brecha:,} ({100 * n_con_brecha / len(pdf):.1f}%)")
print(f"Ahorro potencial total: {pdf['ahorro_potencial_kwh'].sum() / 1e9:.3f} TWh/año")

# COMMAND ----------

# DBTITLE 1,Modelo de sugerencias por edificio
# ============================================================================
# CELDA 11 — MODELO DE SUGERENCIAS DE CONSUMO POR EDIFICIO (objetivo 8)
# ----------------------------------------------------------------------------
# QUÉ HACE: Para cada edificio genera una recomendación personalizada: medida
# principal y complementarias según su edad, tipo y brecha; ahorro estimado;
# letra objetivo alcanzable; y prioridad de intervención (P1/P2/P3).
#
# CÓMO:
# 1. Prioridad por terciles de ahorro: el 25% de mayor ahorro = P1
#    (intervención inmediata), el siguiente 25% = P2, el resto = P3.
# 2. Medida principal según antigüedad (>=50 años: rehabilitación integral;
#    30-49: ventanas y aislamiento; <30: ajuste de instalaciones), con regla
#    específica para locales comerciales (climatización e iluminación).
# 3. Medidas complementarias por reglas (caldera de alta eficiencia, solar
#    térmica, auditoría urgente si es anómalo, revisión de proyecto).
# 4. Letra objetivo: la clase cuya mediana de consumo más se acerca al
#    consumo óptimo de referencia de su tipo de edificio.
#
# RESULTADO OBTENIDO: 154.538 edificios con sugerencia (100%). Medida
# principal: instalaciones 52.121 | rehabilitación integral 48.212 |
# ventanas+aislamiento 42.987 | locales 11.218. Prioridades: P1 38.635 |
# P2 38.634 | P3 77.269. Letra objetivo mayoritariamente A (B en locales).
# ============================================================================

q75_ahorro = pdf["ahorro_potencial_kwh"].quantile(0.75)
q50_ahorro = pdf["ahorro_potencial_kwh"].quantile(0.50)

# Lettra objetivo: mediana de consumo de cada clase -> letra mas cercana al optimo
mediana_clase = pdf.groupby("clasificacion_consumo")["consumo_kwh_m2_anio"].median()
def letra_objetivo(consumo_optimo):
    return min(mediana_clase.index, key=lambda c: abs(mediana_clase[c] - consumo_optimo))

objetivo_por_tipo = {tipo: letra_objetivo(opt) for tipo, opt in pdf.groupby("tipo_edificio")["consumo_optimo_kwh_m2"].first().items()}

# Nombres de segmento: ordenados por consumo medio descendente (S1 = peor)
orden_clusters = pdf.groupby("cluster")["consumo_kwh_m2_anio"].mean().sort_values(ascending=False).index.tolist()
mapa_segmento = {clu: f"S{rank + 1}" for rank, clu in enumerate(orden_clusters)}
pdf["segmento"] = pdf["cluster"].map(mapa_segmento)

# Medida principal: por edad del edificio, con regla especial para locales
medida_edad = np.select(
    [pdf["edad_edificio"] >= 50, pdf["edad_edificio"] >= 30],
    [
        "Rehabilitación integral de envolvente (fachada, cubierta y ventanas)",
        "Sustitución de ventanas y mejora del aislamiento",
    ],
    default="Ajuste y mejora de instalaciones (calefacción, ACS y control)",
)
pdf["medida_principal"] = np.where(
    pdf["tipo_edificio"] == "Local",
    "Optimización de climatización, iluminación y horarios de uso",
    medida_edad,
)

# Medidas complementarias (reglas simples, legibles para el gestor)
secundarias = [
    np.where(pdf["edad_edificio"] >= 30, "Sustitución del generador por alta eficiencia", ""),
    np.where(pdf["brecha_kwh_m2"] > 200, "Instalación de energía solar térmica", ""),
    np.where(pdf["es_anomalia_consumo"], "Auditoría energética prioritaria (anomalía detectada)", ""),
    np.where(pdf["es_proyecto"], "Revisión del proyecto para asegurar clase A antes de ejecutar", ""),
    np.where(pdf["clasificacion_consumo"].isin(["F", "G"]), "Certificación y asesoramiento para rehabilitación", ""),
]
pdf["medidas_secundarias"] = [
    "; ".join([m for m in lista if m]) for lista in zip(*secundarias)
]

pdf["prioridad"] = np.select(
    [pdf["ahorro_potencial_kwh"] >= q75_ahorro, pdf["ahorro_potencial_kwh"] >= q50_ahorro],
    ["P1", "P2"],
    default="P3",
)
pdf["ahorro_estimado_kwh"] = pdf["ahorro_potencial_kwh"].round(0)
pdf["clase_objetivo"] = pdf["tipo_edificio"].map(objetivo_por_tipo)

# Verificación del motor de sugerencias
columnas_sugerencia = [
    "municipio", "provincia", "tipo_edificio", "edad_edificio", "clasificacion_consumo",
    "consumo_kwh_m2_anio", "consumo_optimo_kwh_m2", "brecha_kwh_m2", "clase_objetivo",
    "medida_principal", "medidas_secundarias", "ahorro_estimado_kwh", "prioridad", "segmento",
]
print("Edificios con sugerencia:", len(pdf), "(100% del parque analizado)")
display(pdf[columnas_sugerencia].sample(10, random_state=42))
display(pdf["medida_principal"].value_counts().rename("n_edificios").to_frame().reset_index(names="medida_principal"))
display(pdf["prioridad"].value_counts().to_frame())

# COMMAND ----------

# DBTITLE 1,Planes de trabajo por segmento
# ============================================================================
# CELDA 12 — PLANES DE TRABAJO POR SEGMENTO (objetivo 10)
# ----------------------------------------------------------------------------
# QUÉ HACE: Condensa las sugerencias en un plan de trabajo por segmento:
# cuántos edificios, qué medida domina, ahorro total y horizonte temporal
# (P1 corto 0-2 años, P2 medio 2-5 años, P3 largo 5+ años).
#
# CÓMO:
# 1. Agrupa por segmento y calcula tamaño, consumo medio, ahorro total,
#    nº de P1, letra típica y letra objetivo dominante.
# 2. El horizonte del plan depende de la proporción de P1 del segmento.
#
# RESULTADO OBTENIDO: S1 (90.135 edificios, 2.066 GWh, 27.181 P1):
# rehabilitación integral, horizonte largo. S2 (8.186 edificios, 3.095 GWh,
# 8.059 P1): rehabilitación integral, horizonte CORTO (0-2 años): son los
# grandes edificios donde cada actuación rinde más. S3 (56.217, 657 GWh):
# ajuste de instalaciones. Suma: 5.817,6 GWh/año, cuadra con el total por
# edificio (5,818 TWh).
# ============================================================================

planes_trabajo = (
    pdf.assign(horizonte_por_edificio=np.select(
        [pdf["prioridad"] == "P1", pdf["prioridad"] == "P2"],
        ["Corto (0-2 años)", "Medio (2-5 años)"],
        default="Largo (5+ años)",
    ))
    .groupby("segmento")
    .agg(
        n_edificios=("segmento", "size"),
        consumo_medio=("consumo_kwh_m2_anio", "mean"),
        n_p1=("prioridad", lambda s: (s == "P1").sum()),
        ahorro_total_gwh=("ahorro_estimado_kwh", lambda s: s.sum() / 1e6),
        letra_tipica=("clasificacion_consumo", lambda s: s.mode().iloc[0]),
        letra_objetivo=("clase_objetivo", lambda s: s.mode().iloc[0]),
        medida_dominante=("medida_principal", lambda s: s.mode().iloc[0]),
        horizonte=("horizonte_por_edificio", lambda s: s.mode().iloc[0]),
    )
    .round(1)
    .reset_index()
)
display(planes_trabajo)

print(f"Suma de ahorro de los planes: {planes_trabajo['ahorro_total_gwh'].sum():.1f} GWh/año (debe coincidir con el total por edificio)")

# COMMAND ----------

# DBTITLE 1,Guardado tablas gold y resumen
# ============================================================================
# CELDA 13 — GUARDADO DE LAS TABLAS GOLD ANALÍTICAS Y RESUMEN EJECUTIVO
# ----------------------------------------------------------------------------
# QUÉ HACE: Materializa los resultados como tablas gold para que el
# dashboard gerencial (y cualquier consulta SQL) pueda usarlas sin
# recalcular nada: resultados por edificio, sugerencias por edificio,
# planes por segmento y resumen agregado por territorio.
#
# CÓMO:
# 1. Selecciona las columnas finales de cada tabla (nombres claros).
# 2. Escribe cada tabla en el esquema workspace.energia_aragon con
#    mode="overwrite" (si ya existiera, se reemplaza con la versión nueva).
# 3. Verifica los conteos y cuadres (las prioridades suman el total; el
#    ahorro de los planes = ahorro por edificio) y emite el resumen
#    ejecutivo del estudio.
#
# RESULTADO OBTENIDO: 4 tablas creadas en workspace.energia_aragon:
# gold_resultados_optimizacion (154.538 filas), gold_sugerencias_consumo
# (154.538), gold_planes_trabajo (3 segmentos) y gold_resumen_gerencial
# (5.974 combinaciones territoriales). Verificaciones y asserts OK.
# ============================================================================

SCHEMA = "workspace.energia_aragon"

# --- Tabla 1: resultados de optimización por edificio ---
cols_resultados = [
    "municipio", "provincia", "tipo_edificio", "estado_edificio", "anio_construccion",
    "superficie_m2", "clasificacion_consumo", "clasificacion_emisiones",
    "consumo_kwh_m2_anio", "consumo_predicho_kwh_m2", "emision_co2", "emision_predicha_kg_m2",
    "consumo_optimo_kwh_m2", "brecha_kwh_m2", "ahorro_potencial_kwh", "ahorro_potencial_pct",
    "es_anomalia_consumo", "score_anomalia_consumo", "es_anomalia_co2", "score_anomalia_co2",
    "cluster", "segmento", "prioridad",
]
df_resultados = pdf[cols_resultados].copy()
spark.createDataFrame(df_resultados).write.mode("overwrite").saveAsTable(f"{SCHEMA}.gold_resultados_optimizacion")

# --- Tabla 2: sugerencias por edificio ---
df_sugerencias = pdf[columnas_sugerencia + ["es_anomalia_consumo", "estado_edificio", "superficie_m2"]].copy()
spark.createDataFrame(df_sugerencias).write.mode("overwrite").saveAsTable(f"{SCHEMA}.gold_sugerencias_consumo")

# --- Tabla 3: planes de trabajo por segmento ---
spark.createDataFrame(planes_trabajo).write.mode("overwrite").saveAsTable(f"{SCHEMA}.gold_planes_trabajo")

# --- Tabla 4: resumen gerencial territorial (para el dashboard) ---
resumen_gerencial = (
    pdf.groupby(["provincia", "municipio", "tipo_edificio", "segmento", "prioridad"])
    .agg(
        n_edificios=("municipio", "size"),
        consumo_medio=("consumo_kwh_m2_anio", "mean"),
        emision_media=("emision_co2", "mean"),
        ahorro_gwh=("ahorro_estimado_kwh", lambda s: s.sum() / 1e6),
        n_anomalias=("es_anomalia_consumo", "sum"),
    )
    .round(2)
    .reset_index()
)
spark.createDataFrame(resumen_gerencial).write.mode("overwrite").saveAsTable(f"{SCHEMA}.gold_resumen_gerencial")

# --- Verificación de cuadres ---
verif = spark.table(f"{SCHEMA}.gold_resultados_optimizacion").count()
print(f"gold_resultados_optimizacion: {verif:,} filas")
print(f"gold_sugerencias_consumo: {spark.table(f'{SCHEMA}.gold_sugerencias_consumo').count():,} filas")
print(f"gold_planes_trabajo: {spark.table(f'{SCHEMA}.gold_planes_trabajo').count()} segmentos")
print(f"gold_resumen_gerencial: {spark.table(f'{SCHEMA}.gold_resumen_gerencial').count():,} combinaciones territoriales")

assert verif == len(pdf), "El conteo de la tabla de resultados no cuadra con el parque"
assert planes_trabajo["ahorro_total_gwh"].sum() > 0, "El ahorro agregado no puede ser 0"

# --- Resumen ejecutivo del estudio ---
print("\n" + "=" * 70)
print("RESUMEN EJECUTIVO — OPTIMIZACIÓN ENERGÉTICA DE EDIFICIOS DE ARAGÓN")
print("=" * 70)
print(f"Parque analizado: {len(pdf):,} edificios certificados")
print(f"Consumo medio: {pdf['consumo_kwh_m2_anio'].mean():.0f} kWh/m²/año | Emisiones medias: {pdf['emision_co2'].mean():.1f} kg CO₂/m²/año")
print(f"Edificios por encima del óptimo de referencia: {n_con_brecha:,} ({100 * n_con_brecha / len(pdf):.1f}%)")
print(f"Ahorro potencial total: {pdf['ahorro_potencial_kwh'].sum() / 1e9:.2f} TWh/año")
print(f"Prioridad P1 (mayor ahorro, 25% del parque): {int((pdf['prioridad'] == 'P1').sum()):,} edificios")
print(f"Anomalías detectadas (consumo muy distinto del esperado): {int(pdf['es_anomalia_consumo'].sum()):,}")
print(f"Segmentos de intervención: {k_optimo} (S1 = mayor consumo)")
print("=" * 70)

# COMMAND ----------

# DBTITLE 1,Conclusiones
# MAGIC %md
# MAGIC ## Conclusiones del estudio
# MAGIC
# MAGIC **Diagnóstico del parque.** Se analizaron 154.538 certificados de edificios de Aragón (datos abiertos del Gobierno de Aragón, https://opendata.aragon.es/). El consumo medio es de 258 kWh/m²/año y las emisiones medias de 55,2 kg CO₂/m²/año. El 99,3% de los edificios (153.506) consume por encima del óptimo de referencia de su tipo, con un **ahorro potencial total de 5,82 TWh/año** si todo el parque alcanzara el nivel de los edificios clase A de su mismo tipo.
# MAGIC
# MAGIC **Modelos entrenados (todos registrados en MLflow y reutilizables).**
# MAGIC
# MAGIC * Predicción del consumo: HistGradientBoosting, MAE 73,5 kWh/m²/año, R² 0,223 (con solo atributos físicos del edificio).
# MAGIC * Predicción de emisiones de CO₂: MAE 16,6 kg CO₂/m²/año, R² 0,198.
# MAGIC * Clasificación por letra A-G: 49,9% de acierto global (F1 ponderado 0,489), útil para cribar edificios sin certificado vigente.
# MAGIC * Detección de anomalías: 1.546 edificios (1%) con consumo muy distinto del esperado para su perfil; los extremos consumen ~986 kWh/m²/año cuando su perfil esperaba ~161.
# MAGIC * Segmentación: 3 segmentos operativos (k=3, silueta 0,320), que no copian la letra oficial (ARI 0,068) sino que añaden la vista de gestión.
# MAGIC
# MAGIC **Factores clave (objetivo 4).** La antigüedad (año de construcción / edad) y el tipo de edificio son los mayores determinantes del consumo y de la letra; la provincia aporta poco. La política de rehabilitación debe priorizar el parque construido antes de 1980.
# MAGIC
# MAGIC **Impacto de renovaciones (objetivo 7, aproximación).** Los edificios pre-1980 consumen de media 287,8 frente a 175,1 kWh/m²/año de los construidos desde 2007: una reforma profunda moderna ahorra del orden de 112,8 kWh/m²/año por edificio. Limitación: el dataset no registra reformas realizadas (solo 136 "Proyecto Reforma"), por lo que esta cifra es una comparación por época, no causal.
# MAGIC
# MAGIC **Dónde actuar (objetivos 6, 8, 9, 10).** Cada edificio tiene sugerencia personalizada (100% del parque): la rehabilitación integral de envolvente aplica a 48.212 edificios, la mejora de ventanas y aislamiento a 42.987 y el ajuste de instalaciones a 52.121. La prioridad P1 (38.635 edificios, 25% de mayor ahorro) incluye los grandes edificios del segmento S2: solo 8.186 edificios concentran 3.095 GWh/año de ahorro potencial, el mejor retorno por actuación y con horizonte corto (0-2 años).
# MAGIC
# MAGIC **Entregables.** Cuatro tablas gold en `workspace.energia_aragon` (`gold_resultados_optimizacion`, `gold_sugerencias_consumo`, `gold_planes_trabajo`, `gold_resumen_gerencial`), cinco modelos en el experimento MLflow `Optimizacion_Energia_Aragon` (regresor de consumo, regresor de CO₂, clasificador de letra, detector de anomalías y segmentador K-Means) y un dashboard gerencial interactivo con filtros por provincia, municipio, tipo, letra, prioridad y segmento.
# MAGIC
# MAGIC **Limitaciones honestas.** Con solo atributos físicos el R² es modesto (~0,2): el consumo real depende de factores no registrados (calefacción, hábitos de uso, ocupación). El óptimo de referencia es un proxy (mediana de los clase A del mismo tipo). La tasa de anomalías (1%) es una suposición al no existir casos confirmados. El sesgo medio de +19,7 kWh/m²/año en las predicciones del consumo (transformación logarítmica) está documentado y debe corregirse al usar el modelo en producción.

# COMMAND ----------

# DBTITLE 1,Atajos a los entregables del proyecto
# MAGIC %md
# MAGIC ## Atajos a los entregables del proyecto
# MAGIC
# MAGIC Este notebook contiene **el código completo de los modelos** (celdas 3–12: regresión de consumo, factores clave, emisiones de CO₂, clasificación de letra A–G, detección de anomalías, segmentación, modelo óptimo, sugerencias y planes de trabajo) y **la creación de las 4 tablas gold** que alimentan el resto de entregables (celda 13). El dashboard y el asistente Genie son assets independientes que consumen esas tablas: aquí están sus atajos directos.
# MAGIC
# MAGIC * **📊 Dashboard gerencial** — «Estudio Completo Eficiencia Energética Aragón»: 6 páginas en español para directivos (resumen ejecutivo, parque edilicio, consumo y óptimo, modelos ML, priorización territorial, sugerencias y planes) con filtros globales. [Abrir el dashboard](/sql/dashboardsv3/01f1e3befa1f1fcb80c90c93592b4391) · Archivo del repo: `Estudio Completo Eficiencia Energética Aragón.lvdash.json`
# MAGIC * **🤖 Asistente Genie** — «Energia Aragon Gold Energy Optimization Insights»: responde preguntas en lenguaje natural sobre las tablas gold del estudio. [Abrir el Genie](/genie/rooms/01f1e3bf2aba1c3b8c076c60828e48c2)
# MAGIC * **🧪 Modelos registrados (MLflow)** — experimento «Optimizacion_Energia_Aragon» con los 5 modelos entrenados en este notebook (regresor de consumo, regresor de CO₂, clasificador de letra, detector de anomalías y segmentador K-Means). [Abrir el experimento](/ml/experiments/987497754115382)
# MAGIC * **🏗️ Código del pipeline medallón** (bronze → silver → gold) — carpeta [`pipeline_energia_aragón`](/Workspace/Users/daniel.betancur2667@unaula.edu.co/Big_Data_Unaula/pipeline_energia_aragón)
# MAGIC * **📁 Datos y métricas documentadas** — carpetas [`data`](/Workspace/Users/daniel.betancur2667@unaula.edu.co/Big_Data_Unaula/data) y [`models`](/Workspace/Users/daniel.betancur2667@unaula.edu.co/Big_Data_Unaula/models), y el [`README.md`](/Workspace/Users/daniel.betancur2667@unaula.edu.co/Big_Data_Unaula/README.md) general del proyecto.
# MAGIC
# MAGIC > Nota: el dashboard y el Genie se generaron como assets de Databricks (no desde este notebook), por eso se enlazan aquí; para reproducir sus datos basta reejecutar este notebook, que regenera las tablas gold de las que dependen.