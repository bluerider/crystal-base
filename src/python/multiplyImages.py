## got to pass in the aws keys by arguments
import sys, os, io
## context is labeled sc
from pyspark import SparkContext, SparkConf
## need this to do image classification
from pyspark.ml.image import ImageSchema
## use pillow
from PIL import Image
## use boto for AWS S3 file access
import boto3, s3fs

## let's pass in the sc (if running within pyspark)
def main(sc):
    """
    Main insertion function.
    Multiply images from S3 using rotation and mirror operations.
    Upload the images to S3.
    """
    ## we need to pass in the AWS keys
    sc._jsc.hadoopConfiguration().set("fs.s3a.access.key", os.environ["AWS_ACCESS_KEY_ID"])
    sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key", os.environ["AWS_SECRET_ACCESS_KEY"])
    # use S3 streaming
    addr = "s3a:/"
    ## let's get the rdd for images
    crystal_imgs = getImages(sc, addr)
    ## create a broadcast variable containing AWS keys
    aws_info = sc.broadcast((os.environ["AWS_ACCESS_KEY_ID"], 
                             os.environ["AWS_SECRET_ACCESS_KEY"]))
    ## let's generate some images and upload them to S3
    crystal_imgs.foreach(lambda row: genImagesToS3(row, aws_info))

## get the RDDs from images
## we have to switch to an RDD instead
## return an RDD
def getImages(sc, addr):
    """
    Return RDDs for crystal images from S3.
    """
    crystal_imgs= ImageSchema.readImages(addr+"/marcos-data/*/*/*.jpeg", numPartitions = 2000)
    return(crystal_imgs)

## generate variations of an image
def genImagesToS3(row, aws_info):
    """
    Generate variations of an image from a dataframe row.
    Upload images to S3.
    """
    urls, imgs = transformImages(row)
    aws_access_key, aws_secret_key = aws_info.value
    s3 = s3fs.S3FileSystem(key = aws_access_key,
                           secret = aws_secret_key,
                           use_ssl = True,
                           anon = False)
    addToS3(urls, imgs, s3)
    
## generate images
## we will need to do several transform operations
## mirror -> rotate (90 degrees)
def transformImages(row):
    """
    Transform images from a dataframe by rotating and mirroring.
    Returns (url, jpeg).
    """
    ## name is stored in url
    url_name = row.image.origin.split('.')[:-1][0]
    ## get the byte array
    byte_array = row.image.data
    ## mirror the image
    img = Image.frombytes("RGB", 
                          (row.image.width, row.image.height),
                          bytes(byte_array))
    mirrored_img = img.transpose(Image.FLIP_LEFT_RIGHT)
    ## create an array of rotated images
    imgs = [a.rotate(deg) for deg in range(0, 360, 90) for a in [img, mirrored_img]]
    ## let's give the images a new id
    urls = [url_name+"-"+str(num)+".jpeg" for num in range(len(imgs))]
    return(urls, imgs)

## add images to S3
def addToS3(urls, imgs, s3):
    """
    Upload images to S3 using url scheme.
    """
    ## strip urls to become buckets
    buckets = [url.split("s3a://")[1] for url in urls]
    ## loop for buckets and imgs
    for pair in zip(buckets,imgs):
        bucket = pair[0]
        img = pair[1]
        ## get a streaming byte array
        byte_array = io.BytesIO()
        ## save the image with compression
        ## to byte array
        img.save(byte_array, format = "JPEG")
        with s3.open(bucket, 'wb') as f:
            ## write the img
            f.write(byte_array.getvalue())
            ## close the file
            f.close()
    


if __name__ == '__main__':
    """
    Setup spark and AWS keys.
    """
    ## pass the AWS access keys
    os.environ["AWS_ACCESS_KEY_ID"]=sys.argv[1]
    os.environ["AWS_SECRET_ACCESS_KEY"]=sys.argv[2]
    os.environ["AWS_DEFAULT_REGION"]=sys.argv[3]
    sc = SparkContext(conf=SparkConf().setAppName("Crystal-Image-Generator"))
    ## run the main insertion function
    main(sc)