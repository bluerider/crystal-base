import os, sys
from pyspark import SparkContext, SparkConf, SQLContext
from sparkdl import readImages, DeepImageFeaturizer
from pyspark.sql.functions import lit
from pyspark.ml import Pipeline
from pyspark.ml.classification import LogisticRegression
from pyspark.ml.evaluation import MulticlassClassificationEvaluator

## main insertion function
def main(sc):
    ## we need to pass in the AWS keys
    sc._jsc.hadoopConfiguration().set("fs.s3a.access.key", os.environ["AWS_ACCESS_KEY_ID"])
    sc._jsc.hadoopConfiguration().set("fs.s3a.secret.key", os.environ["AWS_SECRET_ACCESS_KEY"])
    ## get the training and testing dataframes
    train_df, test_df = genDataFrames("s3a://marcos-data/")
    ## setup the transfer learner
    p = transferLearner(20, 0.05, 0.3)
    ## run the model
    p_model = runModel(train_df, p)
    ## get the predictions data frame
    predictions_df = predictWithModel(test_df, p_model)
    ## get the accuracy of the predictions
    accuracy = validate(predictions_df)
    print("Model was accurate to: "+str(accuracy))
    ## write the results to database
    writeToPostgreSQL(predictions_df)

## let's work on getting this classifier up
## returns a training and test dataframe
def genDataFrames(url):
    ## training set
    ## let's get and combine the negative image data set
    clear_train_imgs = readImages(url+"train-jpg/Clear/*.jpeg").withColumn("label", lit(0))
    precipitate_train_imgs = readImages(url+"train-jpg/Precipitate/*.jpeg").withColumn("label", lit(0))
    other_train_imgs = readImages(url+"train-jpg/Other/*.jpeg").withColumn("label", lit(0))
    negative_train_imgs = clear_train_imgs.unionAll(precipitate_train_imgs).unionAll(other_train_imgs)

    ## let's get crystal data set
    positive_train_imgs = readImages(url+"train-jpg/Crystals/*.jpeg").withColumn("label", lit(1))

    ## testing set
    ## let's get and combine the negative image data set
    clear_test_imgs = readImages(url+"test-jpg/Clear/*.jpeg").withColumn("label", lit(0))
    precipitate_test_imgs = readImages(url+"test-jpg/Precipitate/*.jpeg").withColumn("label", lit(0))
    other_test_imgs = readImages(url+"test-jpg/Other/*.jpeg").withColumn("label", lit(0))
    negative_test_imgs = clear_test_imgs.unionAll(precipitate_test_imgs).unionAll(other_test_imgs)

    ## let's get crystal data set
    positive_test_imgs = readImages(url+"test-jpg/Crystals/*.jpeg").withColumn("label", lit(1))

    ## let's combine them to create the training df
    train_df = positive_train_imgs.unionAll(negative_train_imgs)
    test_df = positive_test_imgs.unionAll(negative_test_imgs)
    
    ## return the dataframes
    return(train_df, test_df)

## let's setup the trainer
## returns a pipeline
def transferLearner(max_iter, reg_param, elastic_net_param):
    ## let's setup some parameters
    featurizer = DeepImageFeaturizer(inputCol="image", outputCol="features", modelName="InceptionV3")
    lr = LogisticRegression(maxIter=max_iter, 
                            regParam=reg_param,
                            elasticNetParam=elastic_net_param, 
                            labelCol="label")
    p = Pipeline(stages=[featurizer, lr])
    
    ## return the pipeline
    return(p)

## run the model
## return a model
def runModel(train_df, pipeline):
    ## run the model
    p_model = pipeline.fit(train_df)
    
    ## return the model
    return(p_model)

## get some predictions
## returns a dataframe
def predictWithModel(test_df, p_model):
    predictions = p_model.transform(test_df)
    df = p_model.transform(test_df)
    
    ## return the dataframe
    return(df)

## validate
## returns the accuracy
def validate(df):
    predictionAndLabels = df.select("prediction", "label")
    evaluator = MulticlassClassificationEvaluator(metricName="accuracy")
    
    ## return the accuracy
    return(evaluator.evaluate(predictionAndLabels))

## write to postgres database
## THIS FUNCTION SHOULD BE SPLIT INTO ITS OWN FILE
## WHEN THE MODEL PARAMETERS CAN BE STORED ON DISK
def writeToPostgreSQL(sql):
    ## let's just write grab the crystal info here
    postgres_df = sql.select("image_id", "label_text").selectExpr("image_id as id", "label_text as crystal")
    postgres_df = postgres_df.withColumn('crystal_bool', when(postgres_df.crystal == "Crystals", True).otherwise(False)).drop(postgres_df.crystal).select(col("crystal_bool").alias("crystal"),col("id"))
    postgres_df = postgres_df.select("id", "crystal")
    postgres_df = postgres_df.withColumn("id", postgres_df.id.cast('integer'))
    ## let's add the dataframe to Postgresql
    postgres_df.write.jdbc(url = "jdbc:postgresql://"+os.environ["POSTGRES_URL"]+":5432/crystal-base", 
                          table = "marcos",
                          mode = "append",
                          properties={"driver": 'org.postgresql.Driver',
                                      "user": os.environ["POSTGRES_USER"],
                                      "password": os.environ["POSTGRES_PASSWORD"]}) 

if __name__ == '__main__':
    sc = SparkContext(conf=SparkConf().setAppName("Crystal-Image-Classifier"))
    os.environ["AWS_ACCESS_KEY_ID"]=sys.argv[1]
    os.environ["AWS_SECRET_ACCESS_KEY"]=sys.argv[2]
    os.environ["AWS_DEFAULT_REGION"]=sys.argv[3]
    os.environ["POSTGRES_URL"]=sys.argv[4]
    os.environ["POSTGRES_USER"]=sys.argv[5]
    os.environ["POSTGRES_PASSWORD"]=sys.argv[6]
    ## run the main insertion function
    main(sc)