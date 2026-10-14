from pyspark.sql import SparkSession

spark = (
    SparkSession.builder
    .appName("Olist_Pipeline")
    .master("local[2]")
    .config("spark.driver.memory", "1g")
    .config("spark.executor.memory", "1g")
    .config("spark.sql.shuffle.partitions", "2")
    .config("spark.default.parallelism", "2")
    .config("spark.jars.packages", "org.postgresql:postgresql:42.7.2")
    .getOrCreate()
)