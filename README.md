# Optimización Energética de Edificios — Aragón

Proyecto de Big Data sobre los **certificados de eficiencia energética de edificios de Aragón** (España)
(dataset de Kaggle: `isabelocastillo/eficiencia-energetica-edificios-de-aragon`, ~180.000 certificados).

Objetivo: identificar edificios con consumo excesivo, cuantificar el ahorro potencial de llevar cada
edificio al "óptimo" de su tipo (mediana de consumo de los edificios clase A) y priorizar planes de
trabajo por segmento.

## Estructura del repositorio

| Ruta | Contenido |
| --- | --- |
| `data/df_limpio.csv` | Datos crudos (zona de aterrizaje, 179.852 filas) |
| `data/gold_*.csv` | Tablas analíticas finales exportadas (resultados, sugerencias, planes, resumen) |
| `energia_aragon/transformations/` | Código del pipeline medallón (bronze / silver / gold) |
| `Optimización Energía Edificios Aragón.ipynb` | Notebook histórico del proyecto |
| `Estudio Optimización Energía Aragón.ipynb` | Notebook del estudio: análisis, modelos ML y tablas gold |
| `Optimización Energética Edificios Aragón.lvdash.json` | Dashboard gerencial (5 páginas, 21 widgets) |
| `models/README.md` | Documentación de los modelos de ML con sus métricas |
| `credit_risk_dataset.csv` | Dataset de otro proyecto (incluido en la carpeta) |

## Arquitectura medallón

* **Bronce** (`bronze_eficiencia_edificios.py`): ingesta cruda del CSV vía Auto Loader desde la zona de
  aterrizaje (`/Volumes/workspace/energia_aragon/landign_zone`), con archivo de origen y fecha de ingesta.
* **Plata** (`silver_eficiencia_edificios.py`): limpieza y normalización — sin duplicados, clasificaciones
  A–G válidas, año de construcción plausible (1800–2026), superficie > 0, coordenadas UTM numéricas.
* **Oro** (`gold_eficiencia_edificios.py`): enriquecimiento por edificio — edad y década de construcción,
  flag de proyecto, consumo óptimo por tipo (mediana clase A), brecha sobre el óptimo y ahorro potencial
  anual. Se excluyen consumos fuera de (0, 1000] kWh/m²·año por ser errores de registro.

Pipeline Spark Declarativo (SDP) `energia_aragon`, serverless, en el catálogo `workspace`, esquema
`energia_aragon`. Las tablas resultantes viven en Unity Catalog y no en Git; se regeneran ejecutando
el pipeline.

## Cómo reproducir

1. Subir `data/df_limpio.csv` a un volumen de Unity Catalog (zona de aterrizaje del pipeline).
2. Crear/ejecutar el pipeline SDP con las transformaciones de `energia_aragon/transformations/`
   (catálogo `workspace`, esquema `energia_aragon`).
3. Ejecutar el notebook `Estudio Optimización Energía Aragón` para generar las tablas gold analíticas
   y entrenar los modelos (ver `models/README.md`).
4. Abrir el dashboard `Optimización Energética Edificios Aragón` para el resumen gerencial.

## Datos de referencia

* Certificados brutos: 179.852 → limpios (plata): ~155.000.
* Ahorro potencial total estimado y planes de trabajo por segmento: ver dashboard y
  `data/gold_planes_trabajo.csv`.
