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
    for a in ssh aws environment; do
        peg install crystal-project-database-cluster "$a"
    done
    
    ## fetch the cluster information
    peg fetch crystal-project-database-cluster
    
    ## get the needed hostnames
    aws_hosts=($(cat ${PEGASUS_HOME}/tmp/crystal-project-database-cluster/public_dns))
    
    ## copy the needed files
    scp config/database-cluster/*.conf ubuntu@${aws_hosts[0]}:
    
    ## install postgresql
    ssh ubuntu@${aws_hosts[0]} '
        sudo apt-get install postgresql{,-contrib}
        for file in pg_hba.conf postresql.conf; do
            sudo chown postgres:postgres "$file"
            sudo chmod o-rw "$file"
            sudo chmod g-w "$file"
            sudo mv "$file" /etc/postgresql/9.5/main/
        done
        sudo service postgresql start
        sudo -u postgres createdb crystal-base
        sudo -u postgres psql << EOSQL
        \connect crystal-base
        CREATE TABLE  marcos (
            ID         integer,
            crystal    bool
            );q
        EOSQL
    '

    ## error checking
    if [ $? == 0 ]; then
        echo "Launched hadoop hdfs cluster!"
    else
        echo "Error in launching hadoop cluster"
    fi
}
