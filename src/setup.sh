#!/bin/bash

## get needed tools
git clone https://github.com/InsightDataScience/pegasus.git tools/pegasus

## NEED TO HAVE config/bash/env.sh
if [ ! -e config/bash/env.sh ]; then
    cat <<EOF
    Need to add a config/bash/env.sh with:
    ## needed variables for pegasus
    export AWS_ACCESS_KEY_ID=
    export AWS_SECRET_ACCESS_KEY=
    export AWS_DEFAULT_REGION=
    export REM_USER=ubuntu
    export PEGASUS_HOME=
    export PATH=$PEGASUS_HOME:$PATH
    EOF
    ## return
    exit 1
fi
        
## some rudimentary attachment of pipeline
## setup HDFS
## create hadoop cluster
source src/hdfs.sh
launch_hadoop()
## download marcos files and trasnfer them to S3
getMarcosFiles()
## add S3 files to HDFS
addMarcosToHDFS()
    
## setup spark
source src/spark.sh
## install spark
launchSpark()
## install pyspark
installPySpark()