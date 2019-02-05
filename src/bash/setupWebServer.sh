function setupWebServer {
    source config/bash/env.sh
    echo "Launching ec2 instances..."
    ## requires the use of peg
    peg up config/web-server/master.yml
    echo "Getting web server information..."
    ## get the cluster information
    peg fetch crystal-project-web-server
    
    ## install needed packages on web-server
    server_hosts=($(cat ${PEGASUS_HOME}/tmp/crystal-project-web-server/public_dns))
    ssh ubuntu@${server_hosts[0]} '
        sudo apt-get update
        sudo apt-get install python3-pip -y
        sudo pip3 install -U setuptools
        sudo pip3 install dash dash_core_components dash_html_components dash_table_experiments sqlalchemy sqlalchemy_utils pandas tensorflow psycopg2
        '
}