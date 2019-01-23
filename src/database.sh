#!/bin/bash

## launch database instances
function launchDatabase {
    ## requires the use of peg
    for a in config/database-cluster/*yml; do
        peg up "$a"
    done
    ## get the cluster information
    peg fetch crystal-project-database-cluster
    
    ## install some suff on hdfs-cluster
    for a in ssh environment postgres; do
        peg install "$a"
    done
    
    ## error handling
    if [ $? == 0 ]; then
        echo "Launched databases!"
    else
        echo "Error in launching database cluster"
    fi
}