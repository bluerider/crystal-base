#!/bin/bash

## launch database instances
function launchHadoop {
    source config/bash/env.sh
    echo "Launching ec2 instances..."
    ## requires the use of peg
    for a in config/spark-cluster/*yml; do
        peg up "$a"
    done
    echo "Getting cluster information..."
    ## get the cluster information
    peg fetch crystal-project-spark-cluster
    
    ## install some stuff on hdfs-cluster
    echo "Installing hadoop..."
    for a in ssh aws environment hadoop; do
        peg install crystal-project-spark-cluster "$a"
    done
    
    echo "Launching hadoop...."
    ## launch the hadoop cluster
    peg service crystal-project-spark-cluster hadoop start
    
    ## error checking
    if [ $? == 0 ]; then
        echo "Launched hadoop hdfs cluster!"
    else
        echo "Error in launching hadoop cluster"
    fi
}