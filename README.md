# Crystal-Base
# Table of Contents
1. [Protein Crystallization Challenges](README.md#Protein-Crystallization-Challenges)
2. [Dataset](README.md#Dataset)
3. [Architecture](README.md#Architecture)
4. [Web App](README.md#Web-App)

## Protein Crystallization Challenges

Crystal-Base is an image classification pipeline that reports whether or not an image contains a protein crystal. Crystal-Base caters towards both academic and industrial researchers who are running large scale HTS protein crystallization projects who do not want to spend time on the mundane task of identifying possible protein crystals from their crystallization screens.

![Image of Protein Crystal Screen](images/Crystal-Screen.png)

## Dataset

All protein crystal data was obtained from the [Marco Database](https://marco.ccr.buffalo.edu/)

## Architecture
![Image of Pipeline](images/Pipeline.png)

### Ingestion

Data is ingested with Spark from S3 buckets and batch processed.

### Training

With Crystal-base I decided to use a transfer learning and the [inceptionv3](https://www.tensorflow.org/tutorials/images/image_recognition) training model to identify protein drop crystals from the [Marco Database](https://marco.ccr.buffalo.edu/).

### Distributed Image Classification

Data is ingested with Spark from S3 buckets and batch processedon a distributed tensorflow cluster using executors running their own tensorflow instances.

## Web App

### Try it out!

Upload protein crystal jpeg images at [Crystal-Base](http://www.crystal-base.com)
