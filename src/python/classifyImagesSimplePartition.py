## classify partitions of images to reduce writes
def classifyImagesSimplePartition(partition):
    """
    Simple image classifier using url parsing.
    Returns (urls, boolean).
    """
    ## get the urls and imgs byte data
    urls, imgs = zip(*partition)
    ## determine crystal boolean by url
    bools = [lambda url: "Crystal" in url for url in urls]
    ## we want to return 
    ## classify images as a batch
    values = [(url, bool(crystal_bool)) for url, crystal_bool in zip(urls, bools)]
              
    ## return the values
    ## we want to return the values as key value tuples
    ## <s3_url, crystal boolean>
    return(values)