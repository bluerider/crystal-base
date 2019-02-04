## got to pass in the aws keys by arguments
import sys, os
from pyspark import SparkContext, SparkConf, SparkFiles
from pyspark.ml.image import ImageSchema
from pyspark.sql.types import StringType, StructField, StructType, BooleanType
from pyspark.sql import *
import tensorflow as tf
from numpy import argmax
from zipfile import ZipFile
from classifyImagesMarcoPartition import classifyImagesMaroPartition
from classifyImagesSimplePartition import classifyImagesSimplePartition

## main insertion function
def main(sc):
    ## we need to pass in the AWS keys
    sc._jsc.hadoopConfiguration().set("fs.s3a.access.key", os.environ["AWS_ACCESS_KEY_ID"])
    sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key", os.environ["AWS_SECRET_ACCESS_KEY"])
    # use S3 streaming
    addr = "s3a:/"
    ## get the crystal images
    crystal_imgs = getImages(sc, addr)
    ##  set the schema
    schema = StructType([StructField('id', StringType(), False),
                         StructField('crystal', BooleanType(), False)])
    ## set the DAG
    if os.environ["CLASSIFIER_TYPE"] == "marco":
        crystal_mapped = crystal_imgs.mapPartitions(classifyImagesMaroPartition)
    ## use the simple url classifier if we're not using the Marco classifier
    else:
        crystal_mapped = crystal_imgs.mapPartitions(classifyImagesSimplePartition)
    ##  return results as a dataframe
    df = spark_session.createDataFrame(crystal_mapped, schema)
    ## we have too many partitions this
    #df.rdd.coalesce(100)
    df.write.jdbc(url = "jdbc:postgresql://"+os.environ["POSTGRES_URL"]+":5432/crystal-base",
                  table = "marcos",
                  mode = "append",
                  properties={"driver": 'org.postgresql.Driver',
                              "user": os.environ["POSTGRES_USER"],
                               "password": os.environ["POSTGRES_PASSWORD"],
                               "usessl" : "true",
                               "reWriteBatchedInserts" : "true",
                               "batchsize" : "10000"})

## get the RDDs for images as <url, bytestring>
def getImages(sc, addr):
    ## get an rdd for the binaryfiles from the crystal_imgs
    ## use to reduce the number of transfers of uncompressed
    ## imgs
    crystal_imgs = sc.binaryFiles(addr+"/marcos-data.bak/test-jpg/Clear/*.jpeg")
    return(crystal_imgs)

if __name__ == '__main__':
    sc = SparkContext(conf=SparkConf().setAppName("Crystal-Image-Classifier"))
    os.environ["AWS_ACCESS_KEY_ID"] = sys.argv[1]
    os.environ["AWS_SECRET_ACCESS_KEY"] = sys.argv[2]
    os.environ["AWS_DEFAULT_REGION"] = sys.argv[3]
    os.environ["POSTGRES_URL"] = sys.argv[4]
    os.environ["POSTGRES_USER"] = sys.argv[5]
    os.environ["POSTGRES_PASSWORD"] = sys.argv[6]
    os.environ["CLASSIFIER_TYPE"] = sys.argv[7]
    ## create spark session
    spark_session = SparkSession.builder.appName("Crystal-Image-Classifier").getOrCreate()
    sc = spark_session.sparkContext
    ## run the main insertion function
    main(sc)