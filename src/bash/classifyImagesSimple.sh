## let's try creating a spark context for the S3 files
function classifyImagesSimple {
    ## get the needed config
    source config/bash/env.sh
    ## get the needed hostnames
    spark_hosts=($(cat ${PEGASUS_HOME}/tmp/crystal-project-spark-cluster/public_dns))
    ## get the database hostname
    postgresql_dns=($(cat ${PEGASUS_HOME}/tmp/crystal-project-database-cluster/public_dns))
    ## copy the pyspark python script
    echo "Copy python script to spark master..."
    scp src/python/classifyImagesSimple.py ubuntu@${spark_hosts[0]}:
    ## launch the command
    echo "Running spark image generator job..."
    ssh ubuntu@${spark_hosts[0]} "
        export PYSPARK_PYTHON=python3
        export LD_LIBRARY_PATH+=:/usr/local/hadoop/lib/native
        export SPARK_HOME=/usr/local/spark
        export HADOOP_HOME=/usr/local/hadoop
        spark-submit --packages org.apache.hadoop:hadoop-aws:2.7.1,org.postgresql:postgresql:42.1.4 --master spark://${spark_hosts[0]}:7077 --executor-memory 20G --driver-memory 20G --py-files classifyImagesSimple.py classifyImagesSimple.py $AWS_ACCESS_KEY_ID $AWS_SECRET_ACCESS_KEY $AWS_DEFAULT_REGION ${postgresql_dns[0]} $POSTGRES_USER $POSTGRES_PASSWORD
        "
}