## download database-instances
## need to download all files in MARCO database
function ingestMarcosFiles {
    ## source the configuration file
    source config/bash/env.sh
    
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
