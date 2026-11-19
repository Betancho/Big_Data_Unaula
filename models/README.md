# Modelos de Machine Learning

Modelos entrenados en el notebook `Estudio Optimización Energía Aragón` sobre la capa gold
(`gold_edificios_enriquecidos`, 154.538 edificios con consumo plausible). Tracking en el experimento
MLflow `Optimizacion_Energia_Aragon` (13 runs).

| Modelo | Algoritmo | Métricas |
| --- | --- | --- |
| Clasificación de letra energética (A–G) | Random Forest | accuracy 0.499, F1 ponderado 0.489, F1 macro 0.347 |
| Regresión de consumo (final) | HistGradientBoosting | RMSE 104.92 kWh/m², R² 0.223, MAE 73.50 |
| Regresión de consumo (base) | Ridge | RMSE 113.97, R² 0.083, MAE 80.96 |
| Regresión de emisiones CO₂ | HistGradientBoosting | RMSE 24.88, R² 0.198, MAE 16.63 |
| Segmentación de edificios | KMeans | silueta 0.320, NMI vs letra 0.166 |
| Detección de anomalías de consumo/CO₂ | IQR estadístico | 1.546 edificios anómalos detectados |

Los artefactos de los modelos no se exportaron a este repositorio: el almacenamiento de artefactos del
experimento (DBFS raíz del workspace) no es accesible desde compute serverless. Los modelos se
reproducen íntegramente ejecutando el notebook del estudio, que reentrena y registra todo en MLflow.

Los resultados por edificio (consumo predicho, anomalías y prioridad P1–P3) están en
`data/gold_resultados_optimizacion.csv` y `data/gold_sugerencias_consumo.csv`.
