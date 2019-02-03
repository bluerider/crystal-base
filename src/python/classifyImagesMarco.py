## got to pass in the aws keys by arguments
import sys, os
from pyspark import SparkContext, SparkConf, SparkFiles
from pyspark.ml.image import ImageSchema
from pyspark.sql.types import StringType, StructField, StructType, BooleanType
from pyspark.sql import *
import tensorflow as tf
from numpy import argmax
from zipfile import ZipFile

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
    crystal_mapped = crystal_imgs.mapPartitions(classifyImagesPartition)
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
    crystal_imgs = sc.binaryFiles(addr+"/marcos-data.bak/test-jpg/*/*.jpeg")
    return(crystal_imgs)
        
## classify partitions of images to reduce writes
def classifyImagesPartition(partition):
    model = ZipFile('savedmodel.zip', 'r')\
        .extractall("")
    predictor = tf.contrib.predictor.from_saved_model('savedmodel')
    ## grab the byte arrays for the imgs
    ## use zip since we are passed a list of
    ## tuples : <url, bytestring>
    urls, imgs = zip(*partition)
    ## create a dictionary entry for the imgs for
    ## tensorflow model
    dictionary = {"image_bytes" : imgs}
    ## classify images as a batch
    prediction = predictor(dictionary)
    ## get the predicted state of each image
    ## the first reported class is the right one 
    test_string = bytes("Crystals", 'ascii')
    bools = [test_string == array[0] for array in prediction["classes"]]
    #bools = [1 == argmax(array) for array in prediction["scores"]]
    ## we want to return the values as key value tuples
    ## <s3_url, crystal boolean>
    values = [(url, bool(crystal_bool)) for url, crystal_bool in zip(urls, bools)]
    
    ## return the values
    return(values)

if __name__ == '__main__':
    sc = SparkContext(conf=SparkConf().setAppName("Crystal-Image-Classifier"))
    os.environ["AWS_ACCESS_KEY_ID"]=sys.argv[1]
    os.environ["AWS_SECRET_ACCESS_KEY"]=sys.argv[2]
    os.environ["AWS_DEFAULT_REGION"]=sys.argv[3]
    os.environ["POSTGRES_URL"]=sys.argv[4]
    os.environ["POSTGRES_USER"]=sys.argv[5]
    os.environ["POSTGRES_PASSWORD"]=sys.argv[6]
    ## create spark session
    spark_session = SparkSession.builder.appName("Crystal-Image-Classifier-Marco").getOrCreate()
    sc = spark_session.sparkContext
    ## run the main insertion function
    main(sc)