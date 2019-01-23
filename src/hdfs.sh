#!/bin/bash

## launch database instances
function launchHadoop {
    source config/bash/env.sh
    ## requires the use of peg
    for a in config/spark-cluster/*yml; do
        peg up "$a"
    done
    ## get the cluster information
    peg fetch crystal-project-spark-cluster
    
    ## install some suff on hdfs-cluster
    for a in ssh aws environment hadoop; do
        peg install crystal-project-spark-cluster "$a"
    done
    
    ## launch the hadoop cluster
    peg service crystal-project-spark-cluster hadoop start
    
    ## fetch the cluster information
    peg fetch crystal-project-spark-cluster
    
    ## error checking
    if [ $? == 0 ]; then
        echo "Launched hadoop hdfs cluster!"
    else
        echo "Error in launching hadoop cluster"
    fi
}

## download database-instances
## need to download all files in MARCO database
function getMarcosFiles {
    ## let's temporarily use ssh command instead of pegasus
    hadoop_master=$(cat ${PEGASUS_HOME}/tmp/crystal-project-spark-cluster/public_dns | head -1)
    ## we should do this remotely
    ssh ubuntu@$hadoop_master "
        ## got to install awscli since it is not included
        dpkg -l awscli || sudo apt-install awscli -y
        ## set the needed keys
        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
        export AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION
        
        ## need to get terf tool to extract images
        terf_name=terf-0.0.3-0-gde97e3c-linux-amd64
        wget https://github.com/ubccr/terf/releases/download/v0.0.3/\${terf_name}.zip
        unzip \${terf_name}.zip
        ## there are issues with not enough storage space
        ## we need to switch to a streaming method
        for a in train test; do
            ## download file and stream to tar extractor and stream to aws S3
            wget -O - "https://marco.ccr.buffalo.edu/data/archive/\$a-jpg-tfrecords.tar" | \
                tar xf -
        done
        ## extract the data set
        mkdir marco-data
        for a in train-jpg test-jpg; do
            \${terf_name}/terf extract --input "$a" -o "marcos-data/\${a}"
        done
        ## send the marco data to amazon S3
        aws s3 sync {,s3://}marcos-data
        "
}

## rudimentary 
## add the files to the hadoop file system
function addMarcosToHDFS {
    ## let's temporarily use ssh command instead of pegasus
    hadoop_master=$(cat ${PEGASUS_HOME}/tmp/crystal-project-spark-cluster/public_dns | head -1)
    ## source the aws credentials
    source config/bash/env.sh
    ## make the hdfs directory
    ssh ubuntu@$hadoop_master "
        ## source the needed keys
        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
        export AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION
        export HADOOP_HOME=/usr/local/hadoop
                
        ## check if aws-cli is installed
        dpkg -l awscli || sudo apt-get install awscli -y
        ## check if marcos-data is available
        if [ ! -d marcos-data ]; then
            mkdir marcos-data
        fi
        ## synchronize marcos-data folder
        aws s3 sync s3://marcos-data marcos-data/
        ## group all images together
        for crystal_dir in {test,train}-jpeg; do
            mkdir marcos-data/\$crystal_dir/oil_drops
            for type in Crystals Other Precipitate Clear; do
                ## loop to avoid trying to pass too many files at once
                for file in \$crystal_dir/\$type/*; do
                    mv \$file \$crystal_dir/oil_drops/
            done
        ## generate hdfs
        \$HADOOP_HOME/hdfs dfs -mkdir /marcos-data
        \$HADOOP_HOME/bin/hdfs dfs -moveFromLocal ~/marcos-data/* /marcos-data/
    "
}