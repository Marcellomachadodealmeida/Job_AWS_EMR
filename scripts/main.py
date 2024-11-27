import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from awsglue import DynamicFrame

def transform_data(glueContext, query, mapping, transformation_ctx) -> DynamicFrame:
    for alias, frame in mapping.items():
        frame.toDF().createOrReplaceTempView(alias)
    result = spark.sql(query)
    return DynamicFrame.fromDF(result, glueContext, transformation_ctx)
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# Script generated for node AWS Glue Data Catalog
table_name = args['TABLE_NAME']
AWSGLUE_DF = glueContext.create_dynamic_frame.from_catalog(database="table_etl_teste", table_name=table_name, transformation_ctx="AWSGLUE_DF")

# Script generated for node SQL Query
QUERY_GROUP_BY_RED = """
            SELECT nome, descricao, count(*) AS total_violacoes_red
            FROM restaurantes_violacoes
            WHERE tipo_violacao = "RED"
            GROUP BY nome
        """
 QUERY_GROUP_BY_BLUE = """
            SELECT nome, descricao, count(*) AS total_violacoes_red
            FROM restaurantes_violacoes
            WHERE tipo_violacao = "BLUE"
            GROUP BY nome
        """

EXEC_RED_QUERY = transform_data(glueContext, query = QUERY_GROUP_BY_RED, mapping = {"myDataSource":AWSGLUE_DF}, transformation_ctx = "EXEC_RED_QUERY")

EXEC_BLUE_QUERY = transform_data(glueContext, query = QUERY_GROUP_BY_BLUE, mapping = {"myDataSource":AWSGLUE_DF}, transformation_ctx = "EXEC_BLUE_QUERY")

# Script generated for node Amazon S3
Store_Table_RED = glueContext.write_dynamic_frame.from_options(frame=EXEC_RED_QUERY, connection_type="s3", format="glueparquet", connection_options={"path": "s3://bucket-glue-incremental/output/", "partitionKeys": []}, format_options={"compression": "snappy"}, transformation_ctx="Store_Table_RED")

Store_Table_BLUE = glueContext.write_dynamic_frame.from_options(frame=EXEC_BLUE_QUERY, connection_type="s3", format="glueparquet", connection_options={"path": "s3://bucket-glue-incremental/output/", "partitionKeys": []}, format_options={"compression": "snappy"}, transformation_ctx="Store_Table_BLUE")

job.commit()
     
