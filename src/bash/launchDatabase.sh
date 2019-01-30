## launch database instances
function launchDatabase {
    echo "Launching ec2 instances..."
    ## requires the use of peg
    for a in config/database-cluster/*yml; do
        peg up "$a"
    done
    
    ## get the cluster information
    echo "Getting cluster information..."
    peg fetch crystal-project-database-cluster
    
    ## install needed pegasus dependencies
    echo "Installing postgreSQL..."
    for a in ssh aws environment; do
        peg install crystal-project-database-cluster $a
    done
    
    ## get the needed hostnames
    database_hosts=($(cat ${PEGASUS_HOME}/tmp/crystal-project-database-cluster/public_dns))
    
    ## copy the needed files
    echo "Copying configuration files to databse..."
    scp config/database-cluster/*.conf ubuntu@${database_hosts[0]}:
    
    ## install postgresql
    echo "Setting up and launching postgreSQL..."
    ssh ubuntu@${database_hosts[0]} '
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
    
    ## error handling
    if [ $? == 0 ]; then
        echo "Launched databases!"
    else
        echo "Error in launching database cluster"
    fi
}