## got to pass in the aws keys by arguments
import sys, os
from socket import gethostname as hostname
## context is labeled sc
from pyspark import SparkContext, SparkConf, SQLContext
## need this to write a dataframe to PostgreSQL
from pyspark.sql import DataFrameWriter
## need this to do image classification
from pyspark.ml.image import ImageSchema

## let's pass in the sc (if running within pyspark)
def main(sc):
    ## let's just use the HDFS method first
    ## let's set the addr
    local_ip = '.'.join(hostname().split("-")[1:])
    addr = "hdfs://"+local_ip+":9000"
    ## let's get a dataframe
    crystal_df = getDataFrame(sc, addr)
    
def getDataFrame(sc, addr):
    sqlContext = SQLContext(sc)
    ## get the file stream
    crystal_log = sc.textFile(addr+"/marcos-data/*/info.csv")
    ## get the header (contains the fields)
    ## need to create a RDD for the header for later
    ## subtract operation to remove the header from crystal_log
    header = sc.parallelize(crystal_log.first())
    fields = crystal_log.first().split(",")
    ## remove the header from crystal_log
    crystal_values = crystal_log.subtract(header)
    ## split the log by comma separated values
    crystal_values = crystal_values.map(lambda line: line.split(","))
    ## create the data frame
    crystal_df = crystal_values.toDF(fields)
    return(crystal_df)

def getImages(sc, addr):
    ## get an rdd for the oil drop images
    crystal_imgs= ImageSchema.readImages(addr+"/marcos-data/*/oil_drops/*.jpeg")
    return(crystal_imgs)
    

if __name__ == '__main__':
    ## pass the AWS access keys
    os.environ["AWS_ACCESS_KEY_ID"]=sys.argv[1]
    os.environ["AWS_SECRET_ACCESS_KEY"]=sys.argv[2]
    os.environ["AWS_DEFAULT_REGION"]=sys.argv[3]
    sc = SparkContext(conf=SparkConf().setAppName("Crystal-Filter"))
    ## run the main insertion function
    main(sc)