import argparse

from pyspark.sql import SparkSession
from pyspark.sql.functions import col

def transform_data(data_source: str, output_uri: str) -> None:
    with SparkSession.builder.appName("Primeiro job EMR").getOrCreate() as spark:
        df = spark.read.option("header","true").csv(data_source)

        df = df.select(
            col("Name").alias("nome"),
            col("Description").alias("descricao"),
            col("Violation Type").alias("tipo_violacao")            
        )


        df.createOrReplaceTempView("restaurantes_violacoes")

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

        df_result_blue = spark.sql(QUERY_GROUP_BY_BLUE)
        df_result_red = spark.sql(QUERY_GROUP_BY_RED)


        # Gravando os resultados em tabelas Parquet

        df_result_blue.write.mode("overwrite").parquet(output_uri)
        df_result_red.write.mode("overwrite").parquet(output_uri)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--data_sourcer')
    parser.add_argument('--output_uri')
    args = parser.parse_args()

    transform_data(args.data_source, args.output_uri)