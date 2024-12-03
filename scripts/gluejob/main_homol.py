import pandas as pd
import re
from pyspark.sql import SparkSession
from pyspark.sql.functions import expr
from pyspark.sql.functions import col
from awsglue.utils import *

# Inicializar SparkSession 
spark = SparkSession.builder.appName("PandasToSparkDataFrame").getOrCreate()

args = getResolvedOptions(sys.argv, ['s3_bucket','s3_input_path','s3_output_path'])

# Definir o caminho do arquivo CSV no S3
s3_bucket_name = args['s3_bucket']
s3_input_path_name = args['s3_input_path']
s3_output_path_name = args['s3_output_path']

dtype = {6: 'str'}
df = pd.read_csv('s3://bucket-glue-incremental/Homologacao/input_homol/a_processar/dados/',dtype=dtype)

def remove_special_characters(text):
    # Remove caracteres que não sejam letras ou números 
    return re.sub(r'[^a-zA-Z0-9\s]', '', text)

df = df.apply(lambda x: x.astype(str).apply(remove_special_characters))

df = df.replace(r' ', '_', regex=True)

colunas_solicitadas =['Name','Description','Violation Type','Inspection Date']
df_edited = df[colunas_solicitadas]

df_edited.rename(columns={'Name':'nome','Description':'descricao','Violation Type':'tipo_violacao','Inspection Date':'data_inspecao'})

df_edited=df.replace('nan','vazio')

spark_df = spark.createDataFrame(df_edited)

spark_df.write.csv(s3_output_path_csv, mode='overwrite', header=True)

spark_df.write.parquet(s3_output_path_name, mode='overwrite')

job.commit()
