#!/bin/bash

## launch database instances
function launchPostgreSQL {
    source config/bash/env.sh
    ## requires the use of peg
    for a in config/database-cluster/*yml; do
        peg up "$a"
    done
    ## get the cluster information
    peg fetch crystal-project-database-cluster
    
    ## install some suff on hdfs-cluster
    for a in ssh aws environment timescaledb; do
        peg install crystal-project-database-cluster "$a"
    done
    
    ## launch the hadoop cluster
    peg service crystal-project-database-cluster timescaledb start
    
    ## fetch the cluster information
    peg fetch crystal-project-database-cluster
    
    ## error checking
    if [ $? == 0 ]; then
        echo "Launched hadoop hdfs cluster!"
    else
        echo "Error in launching hadoop cluster"
    fi
}
