# Laboratorio PySpark Random Forest

Descarga juntos `pyspark_random_forest.ipynb` y `train_rf_bigquery.py`. El notebook usa el script compartido y parte de datos sintéticos locales. El diagrama representa una arquitectura propuesta; los servicios cloud no se despliegan al abrirlo.

Entorno comprobado: Python 3.10, Java 17 y PySpark 3.5.7. Instala las dependencias en un entorno virtual:

```sh
python -m pip install 'pyspark[ml,sql]==3.5.7' 'numpy<2'
python train_rf_bigquery.py --demo
```

`--demo` no descarga el conector BigQuery ni permite destinos remotos. Para leer una tabla real, indica `--project_id`, `--dataset` e `--input_table`, con credenciales ADC y permisos configurados en el entorno. La ejecución cloud puede tener coste y no está validada por la prueba local.

La escritura está desactivada por defecto. `--output_table` solicita una tabla nueva con modo `errorifexists`; `--model_output` guarda el PipelineModel completo en una ruta nueva. Los errores se propagan y ninguna operación usa `overwrite`.

La separación train/test precede al cálculo de pesos y al ajuste de características. CrossValidator ajusta todo el pipeline en cada fold. Las métricas se calculan durante la ejecución y no acreditan resultados sobre fraude real.

## Verificación reproducible del ejemplo

Desde la raíz del repositorio, con Java 17 y un entorno Python 3.10:

```sh
python -m pip install -r tests/requirements-pyspark.txt
SPARK_LOCAL_IP=127.0.0.1 PYSPARK_PYTHON=python python -m unittest discover -s tests -p test_pyspark_example.py -v
```

Las pruebas cubren argumentos seguros, propagación de errores, validación del esquema, ausencia de categorías del test en el modelo aprendido y persistencia/restauración del pipeline completo. Solo utilizan Spark local y carpetas temporales. La CI separa esta comprobación del lint TypeScript y el build web.
