## got to pass in the aws keys by arguments
import sys, os, io
## context is labeled sc
from pyspark import SparkContext, SparkConf
## need this to do image classification
from pyspark.ml.image import ImageSchema
from pyspark.sql import *

## let's pass in the sc (if running within pyspark)
def main(sc):
    ## we need to pass in the AWS keys
    sc._jsc.hadoopConfiguration().set("fs.s3a.access.key", os.environ["AWS_ACCESS_KEY_ID"])
    sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key", os.environ["AWS_SECRET_ACCESS_KEY"])
    # use S3 streaming
    addr = "s3a:/"
    ## let's get the rdd for images
    crystal_imgs = getImages(sc, addr)
    ## create a broadcast variable containing AWS keys
    postgres_info = sc.broadcast((os.environ["POSTGRES_USER"], 
                                  os.environ["POSTGRES_PASSWORD"],
                                  os.environ["POSTGRES_URL"]))
    ## let's generate some images and upload them to S3
    crystal_imgs.foreachPartition(lambda partition: classifyImagesPartition(partition, postgres_info))

## get the RDDs from images
## we have to switch to an RDD instead
## return an RDD
def getImages(sc, addr):
    ## get an rdd for the oil drop images
    ## let's set more partitions
    ## use only the 50GB data store
    crystal_imgs= ImageSchema.readImages(addr+"/marcos-data.bak/*/*/*.jpeg", numPartitions = 2000)
    return(crystal_imgs)
    
## classify images according to url
def classifyImages(row):
    ## check if url contains the proper name
    if "Crystal" in row.image.origin:
        crystal_bool = True
    else:
        crystal_bool = False
    return(row.image.origin, crystal_bool)
        
## classify partitions of images to reduce writes
def classifyImagesPartition(partition, postgres_info):
    sc = SparkContext(conf=SparkConf().setAppName("Crystal-Image-Classifier-Simple-worker"))
    ## create the sql context
    spark = SQLContext(sc)
    ## classify images
    values = [classifyImages(row) for row in partition]
    ## create a dataframe
    df = spark.createDataFrame(values)
    ## relabel the columns
    df = crystal_df.select("_1", "_2").selectExpr("image_id as id", "label_text as crystal")
    ## get postgres configuration
    user, password, postgres_url = postgres_info.value
    ## let's add the dataframe to Postgresql
    df.write.jdbc(url = "jdbc:postgresql://"+postgres_url+":5432/crystal-base",
                  table = "marcos",
                  mode = "append",
                  properties={"driver": 'org.postgresql.Driver',
                              "user": user,
                              "password": password})

if __name__ == '__main__':
    ## pass the AWS access keys
    os.environ["AWS_ACCESS_KEY_ID"]=sys.argv[1]
    os.environ["AWS_SECRET_ACCESS_KEY"]=sys.argv[2]
    os.environ["AWS_DEFAULT_REGION"]=sys.argv[3]
    os.environ["POSTGRES_URL"]=sys.argv[4]
    os.environ["POSTGRES_USER"]=sys.argv[5]
    os.environ["POSTGRES_PASSWORD"]=sys.argv[6]
    sc = SparkContext(conf=SparkConf().setAppName("Crystal-Image-Classifier-Simple"))
    ## run the main insertion function
    main(sc)