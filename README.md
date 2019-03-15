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

### Setting up AWS

Crystal-base uses **pegasus** to setup AWS clusters with configurations in **yaml** files.

Run `./main.sh --setup-pegasus` to install pegasus.

Run `./main.sh --setup-config` to setup the bash environment

Run `./main.sh --setup-database` to setup a Postgres database.

Run `./main.sh --setup-hadoop` to setup a hadoop cluster.

Run `./main.sh --setup-spark` to setup a spark cluster

Run `./main.sh --setup-web-server` to setup a web server.

### Ingestion

Crystal base ingests files from the [Marco Database](https://marco.ccr.buffalo.edu/) using **bash** and an EC2 instance to an S3 bucket.

Run `source src/bash/ingestMarcoFiles.sh && ingestMarcosFiles` to ingest files

### Training

Crystal-base uses transfer learning [inceptionv3](https://www.tensorflow.org/tutorials/images/image_recognition) training model to identify protein drop crystals from the [Marco Database](https://marco.ccr.buffalo.edu/).

Run `python3 src/python/classifyImagesTrainer.py` to train the image classifier and write to a Postgres Database.

### Distributed Image Classification

Data is ingested with Spark from S3 buckets and batch processedon a distributed tensorflow cluster using executors running their own tensorflow instances.

Run `./main.sh --classify-images simple` to use the simple test classifier. Results are expected to output to a Postgres database.

## Web App

Crystal-base has a web interface that runs its own instance of the trained tensorflow model.

Run `./main.sh --run-webs-server` to run this web-server instance.

### Try it out!

Upload protein crystal jpeg images at [Crystal-Base](http://www.crystal-base.com)
