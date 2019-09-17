## let's try creating a spark context for the S3 files
function classifyImages {
    ## get the needed config
    source config/bash/env.sh
    ## get the needed hostnames
    spark_hosts=($(cat ${PEGASUS_HOME}/tmp/crystal-project-spark-cluster/public_dns))
    postgresql_hosts=($(cat ${PEGASUS_HOME}/tmp/crystal-project-database-cluster/public_dns))
    ## copy the pyspark python script
    echo "Copying python scripts to spark master..."
    for a in src/python/classifyImages{,{Marco,Simple}Partition}.py; do
        scp "$a" ubuntu@${spark_hosts[0]}:
    done
    ## launch the command
    echo "Running spark classification job..."
    ssh ubuntu@${spark_hosts[0]} "
        export PYSPARK_PYTHON=python3
        export LD_LIBRARY_PATH+=:/usr/local/hadoop/lib/native
        export SPARK_HOME=/usr/local/spark
        export HADOOP_HOME=/usr/local/hadoop
        wget -N https://storage.googleapis.com/marco-168219-model/savedmodel.zip
        spark-submit --packages org.apache.hadoop:hadoop-aws:2.7.1,org.postgresql:postgresql:42.1.4 --master spark://${spark_hosts[0]}:7077 --driver-memory 63G --num-executors 6 --executor-cores 15 --executor-memory 51GB --py-files classifyImages.py,classifyImagesMarcoPartition.py,classifyImagesSimplePartition.py --files savedmodel.zip classifyImages.py $AWS_ACCESS_KEY_ID $AWS_SECRET_ACCESS_KEY $AWS_DEFAULT_REGION ${postgresql_hosts[0]} $POSTGRES_USER $POSTGRES_PASSWORD $1
        "
}