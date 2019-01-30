#!/bin/bash

## setup ssh-agent if needed
if ! [ $SSH_AGENT_PID ]; then
    if ! [ $SSH_AUTH_SOCK ]; then
        eval $(ssh-agent -s)
    fi
else
    echo 'Need to launch ssh-agent with eval $(ssh-agent -s)'
fi

if [ ! -d tools ]; then
    mkdir tools
fi

## get needed tools
git clone https://github.com/bluerider/pegasus.git tools/pegasus

## NEED TO HAVE config/bash/env.sh
if [ ! -e config/bash/env.sh ]; then
    cat <<EOF
    Need to add a config/bash/env.sh with:
    ## needed variables for pegasus
    export AWS_ACCESS_KEY_ID=
    export AWS_SECRET_ACCESS_KEY=
    export AWS_DEFAULT_REGION=
    export REM_USER=ubuntu
    export PEGASUS_HOME=\$PWD/tools/pegasus
    export PATH=$PEGASUS_HOME:$PATH
    export POSTGRES_USER=
    export POSTGRES_PASSWORD=
    EOF
    ## return
    exit 1
fi

## need to source bash environment
source config/bash/env.sh

## source all bash source files
for fun in src/bash/*.sh; do
    source "$fun"
done;

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
