import os
import tensorflow as tf
from zipfile import ZipFile
    
## bring the model out of the function to speed up loading
## for dash instances
model = ZipFile('savedmodel.zip', 'r')\
            .extractall("")
predictor = tf.contrib.predictor.from_saved_model('savedmodel')

## define the one off function, uses a preloaded predictor
def classifyImagesMarcoPartitionOneOff(partition):
    """
    Classify images using a preloaded model.
    Returns (url, boolean).
    """
    ## return the values with the global predictor
    values = classifyImagesMarcoPartition(partition, predictor)
    return(values)

## classify partitions of images to reduce writes
## pass in the predictor to reuse a predictor
def classifyImagesMarcoPartition(partition, predictor):
    """
    Classify images using a preloaded model.
    Returns (url, boolean).
    """
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
    ## we want to return the values as key value tuples
    ## <s3_url, crystal boolean>
    values = [(url, bool(crystal_bool)) for url, crystal_bool in zip(urls, bools)]
    
    ## return the values
    return(values)