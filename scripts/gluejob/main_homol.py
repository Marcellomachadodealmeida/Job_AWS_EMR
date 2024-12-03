
from pyspark.sql import SparkSession
from pyspark.sql.functions import expr
from pyspark.sql.functions import col,regexp_replace
from awsglue.utils import *


# Inicializar SparkSession 
spark = SparkSession.builder.appName("PandasToSparkDataFrame").getOrCreate()

# Recuperando variáveis
args = getResolvedOptions(sys.argv, ['s3_bucket','s3_input_path','s3_output_path'])

# Definir o caminho do arquivo CSV no S3
s3_bucket_name = args['s3_bucket']
s3_input_path_name = args['s3_input_path']
s3_output_path_name = args['s3_output_path']

df = spark.read.csv(s3_input_path_name, header=True, inferSchema=True)

for coluna in df.columns: 
    df = df.withColumn(coluna, regexp_replace(col(coluna).cast("string"), "[^a-zA-Z0-9]", ""))

for coluna in df.columns: 
    df = df.withColumn(coluna, regexp_replace(col(coluna).cast("string"), " ", "_"))

df_editado = df.select(
    col("Name").alias("nome"),
    col("Description").alias("descricao"),
    col("Violation Type").alias("tipo_violacao")
)
df_editado.createOrReplaceTempView("Tb_blue_tipo_violacao")

query_table = """
    SELECT nome, tipo_violacao,count(*) as contagem
    from Tb_blue_tipo_violacao
    where tipo_violacao = "BLUE"
    group by nome, tipo_violacao
"""

tb_final = spark.sql(query_table)

tb_final.write.csv(s3_output_path_csv, mode='overwrite', header=True)

tb_final.write.parquet(s3_output_path_name, mode='overwrite')

job.commit()
