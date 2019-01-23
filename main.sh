#!/bin/bash

## main insertion function
function main {
    ## setup ssh-agent if needed
    if ! [ $SSH_AGENT_PID ]; then
        if ! [ $SSH_AUTH_SOCK ]; then
           eval $(ssh-agent -s)
        fi
    else
        echo "requires the use of ssh"
    fi
    ## Run the setup file
    source src/setup.sh || echo "Failed to setup!"
    
    ## 
}

## run the main insertion function
main ${@}