from pyspark.sql import SparkSession


spark = (
    SparkSession.builder\
    .master("local[*]")\
    .appName("Pipeline - Dados Olist")\
    .config("spark.jars.packages", "org.postgresql:postgresql:42.7.2")\
    .config("spark.driver.memory", "2g")\
    .config("spark.sql.shuffle.partitions", "8")\
    .getOrCreate()
)