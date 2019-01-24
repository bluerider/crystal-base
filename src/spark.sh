#!/bin/bash

## launch spark-instances
## we are using spark on top of hadoop
## so the spark cluster should have been launched
## by hdfs.sh
function launchSpark {
    ## get the need keys
    source config/bash/env.sh
    
    ## get the cluster information
    peg fetch crystal-project-spark-cluster
    
    ## install some suff on spark-cluster
    peg install crystal-project-spark-cluster spark
    
    ## launch spark
    peg service crystal-project-spark-cluster spark start
    
    ## error handling
    if [ $? == 0 ]; then
        echo "Launched spark!"
    else
        echo "Error in launching spark cluster"
    fi
}

## let's test reading images into spark
## let's install pyspark for ease of use
function installPySpark {
    ## get the needed config
    source config/bash/env.sh
    ## get the needed hostnames
    aws_hosts=($(cat ${PEGASUS_HOME}/tmp/crystal-project-spark-cluster/public_dns))
    ## install pyspark for all aws hosts in crystal-spark-cluster
    for host in ${aws_hosts[@]}; do
        ssh ubuntu@$host '
            sudo apt-get install python3-pip -y
            for package in pyspark numpy; do
                sudo pip3 install $package
            done
        '
    done
}

## let's try creating a spark context for the S3 files
function filterImages {
    ## get the needed config
    source config/bash/env.sh
    ## get the needed hostnames
    aws_hosts=($(cat ${PEGASUS_HOME}/tmp/crystal-project-spark-cluster/public_dns))
    ## get the postgresql hostname
    postgresql_dns=($(cat ${PEGASUS_HOME}/tmp/crystal-project-database-cluster/public_dns))
    ## copy the pyspark python script
    scp src/image_filter.py ubuntu@${aws_hosts[0]}:
    ## launch the command
    ssh ubuntu@${aws_hosts[0]} "
        export PYSPARK_PYTHON=python3
        export LD_LIBRARY_PATH+=:/usr/local/hadoop/lib/native
        export SPARK_HOME=/usr/local/spark
        export HADOOP_HOME=/usr/local/hadoop
        hostname=\$(hostname)
        hostname=\${hostname##ip-}
        hostname=\${hostname//-/.}
        spark-submit --packages org.apache.hadoop:hadoop-aws:2.7.1,org.postgresql:postgresql:42.1.4 --master spark://\$hostname:7077 image_filter.py $AWS_ACCESS_KEY_ID $AWS_SECRET_ACCESS_KEY $AWS_DEFAULT_REGION ${postgresql_dns[0]}
        "
}