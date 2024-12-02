
import boto3
import pandas as pd
import re
import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.context import SparkContext

# Função para ler o arquivo CSV do S3
def read_csv_from_s3(bucket, key):
    s3 = boto3.client('s3')
    response = s3.get_object(Bucket=bucket, Key=key)
    status = response.get("ResponseMetadata", {}).get("HTTPStatusCode")

    if status == 200:
        print(f"Successfully fetched object {key} from bucket {bucket}")
        df = pd.read_csv(response.get("Body"))
        return df
    else:
        print(f"Failed to fetch object {key} from bucket {bucket}. Status - {status}")
        return None

# Função para salvar o DataFrame em Parquet no S3
def save_parquet_to_s3(df, bucket, key):
    buffer = io.BytesIO()
    df.to_parquet(buffer, index=False)
    s3 = boto3.client('s3')
    s3.put_object(Bucket=bucket, Key=key, Body=buffer.getvalue())

# Configurar o contexto do Glue
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

args = getResolvedOptions(sys.argv, ['JOB_NAME'])
job.init(args['JOB_NAME'], args)

# Parâmetros do bucket e do caminho
input_bucket = 'bucket-glue-incremental'
input_key = 's3://bucket-glue-incremental/Homologacao/input_homol/a_processar/dados/'
output_bucket = 'bucket-glue-incremental'
output_key = 's3://bucket-glue-incremental/Homologacao/output_homol/'

# Ler o CSV do S3
df = read_csv_from_s3(input_bucket, input_key)

if df is not None:
    # Fazer o tratamento dos dados com pandas
    # Exemplo: Remover caracteres especiais das colunas
    df = df.applymap(lambda x: re.sub(r'[^a-zA-Z0-9\s]', '', str(x)))
    df = df.replace(r' ', '_', regex=True)
    df=df.replace('nan','vazio')
    # Salvar o DataFrame tratado em formato Parquet no S3
    save_parquet_to_s3(df, output_bucket, output_key)

# Commit do job
job.commit()
