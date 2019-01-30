#!/bin/bash

#################### THIS IS WHERE THE CODE RUNS #############################
## setup ssh-agent if needed
if ! [ $SSH_AGENT_PID ]; then
    if ! [ $SSH_AUTH_SOCK ]; then
        eval $(ssh-agent -s)
    fi
else
    echo "ssh-agent not found, launching ssh-agent..."
    eval $(ssh-agent -s)
fi

## need to source bash environment
echo "sourcing config/bash/env.sh..."
if [ ! -e config/bash/env.sh ]; then
    echo "Missing config/bash/env.sh. Please run main.sh --setup-config"
else
    source config/bash/env.sh
fi

## source all bash source files
for fun in src/bash/*.sh; do
    source "$fun"
done;

## main insertion function
function main {
    ## setup pegasus
    setupPegasus
    ## setup environment variables
    setupConfig
    ## setup the hadoop cluster
    launchHadoop
    ## setup the spark cluster
    launchSpark
    ## setup the database cluster
    launchDatabase
    ## ingest marcos data files
    ingestMarcosFiles
    ## multiply the marcos images
    multiplyImages
    ## classify images and write results to database
    classifyImages
}
############ AFTER THIS IS LIBRARY FUNCTIONS AND SWITCHES #####################

function setupPegasus {
    if [ ! -d tools ]; then
        mkdir tools
    fi

    ## get needed tools
    if [ ! -d tools/pegasus ]; then
        echo "Couldn't find pegasus. Cloning from git repo..."
        git clone https://github.com/bluerider/pegasus.git tools/pegasus
    else
        echo "Found pegasus"
    fi
}

function setupConfig {
    ## generate the needed environment variables
    ## setup config/bash/env.sh if it isn't already setup
    if [ ! -e config/bash/env.sh ]; then
        if [ ! -d config/bash ]; then
            mkdir config/bash
        fi
        echo "Creating bash environment variables..."
        read -p "AWS Access Key: " -a AWS_ACCESS_KEY_ID
        read -p "AWS Secret Access Key: " -a AWS_SECRET_ACCESS_KEY
        read -p "AWS Default Region: " -a AWS_DEFAULT_REGION
        read -p "Postgres User: " -a POSTGRES_USER
        read -p "Postgres Password: " -a POSTGRES_PASSWORD
        printf '%s\n' "
        export AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
        export AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
        export AWS_DEFAULT_REGION=$AWS_DEFAULT_REGION
        export REM_USER=ubuntu
        export PEGASUS_HOME=\$PWD/tools/pegasus
        export PATH=$PEGASUS_HOME:$PATH
        export POSTGRES_USER=$POSTGRES_USER
        export POSTGRES_PASSWORD=$POSTGRES_PASSWORD
        " > config/bash/env.sh &&
        echo "Wrote conifg/bash/env.sh"
    else
        echo "Found config/bash/env.sh..."
    fi
}

## let's have some switches
case $1 in
    --run)
        main
        ;;
    --config)
        setupPegasus
        setupConfig
        launchHadoop
        launchSpark
        launchDatabase
        ;;
    --setup-config)
        setupConfig
        ;;
    --setup-pegasus)
        setupPegasus
        ;;
    --setup-hadoop)
        launchHadoop
        ;;
    --setup-spark)
        launchSpark
        ;;
    --setup-postgres)
        launchDatabase
        ;;
    --classify-images|--run-pipeline)
        classifyImages
        ;;
    --multiply-images)
        multiplyImages
        ;;
    --help|*)
        cat <<EOF
        
Unknown option : $1
Usage : main.sh [option]

    --run                   Setup and run the crystal-base pipeline
    --config                Setup the crystal-base pipeline
    --setup-config          Setup the bash environment variables
    --setup-pegasus         Setup and install pegasus
    --setup-hadoop          Setup hadoop clusters
    --setup-spark           Setup spark clusters
    --setup-database        Setup database clusters
    --classify-images       Classify images from S3
    --multiply-images       Transform and multiply images from S3 and save back to bucket
    --run-pipeline          Run the crystal-base pipeline
    --help                  Print this help function
    
EOF
esac