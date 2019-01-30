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