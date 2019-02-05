## launch the Dash web server
function runDashServer {
    ## get the needed config
    source config/bash/env.sh
    ## get the needed hostnames
    server_hosts=($(cat ${PEGASUS_HOME}/tmp/crystal-project-web-server/public_dns))
    postgresql_hosts=($(cat ${PEGASUS_HOME}/tmp/crystal-project-database-cluster/public_dns))
    ## copy the flask python scripts
    echo "Copying python scripts to web server..."
    for a in src/python/{runDashServer,classifyImagesMarcoPartitionOneOff}.py; do
        scp "$a" ubuntu@${server_hosts[0]}:
    done
    ## run the web app
    ssh ubuntu@${server_hosts[0]} "
        wget -N https://storage.googleapis.com/marco-168219-model/savedmodel.zip
        python3 runDashServer.py ${postgresql_hosts[0]} $POSTGRES_USER $POSTGRES_PASSWORD crystal-base
        "
}