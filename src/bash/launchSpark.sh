#!/bin/bash

## launch spark-instances
function launchSpark {
    ## get the need keys
    source config/bash/env.sh
    
    ## get the cluster information
    echo "Getting cluster information..."
    peg fetch crystal-project-spark-cluster
    
    ## install some stuff on spark-cluster
    echo "Installing spark..."
    peg install crystal-project-spark-cluster spark
    
    ## get the needed hostnames
    spark_hosts=($(cat ${PEGASUS_HOME}/tmp/crystal-project-spark-cluster/public_dns))
    ## install needed python packages
    echo "Installing python packages..."
    for host in ${spark_hosts[@]}; do
        ssh ubuntu@$host '
            sudo apt-get install python3-pip -y
            sudo pip3 install pyspark numpy nose pillow keras h5py py4j boto3 tensorflow s3fs sparkdl pandas
            done
        '
    done
    
    ## launch spark
    echo "Launching spark..."
    peg service crystal-project-spark-cluster spark start
    
    ## error handling
    if [ $? == 0 ]; then
        echo "Launched spark!"
    else
        echo "Error in launching spark cluster"
    fi
}
