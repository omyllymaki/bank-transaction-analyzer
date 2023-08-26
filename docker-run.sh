#!/usr/bin/env bash
xhost +local:docker
if [ "$#" -eq "2" ]; then
    docker run -e "DISPLAY=$DISPLAY" -v "$HOME/.Xauthority:/root/.Xauthority:ro" -v "$2" --network host -it bank-transaction-analyzer $1
else
    docker run -e "DISPLAY=$DISPLAY" -v "$HOME/.Xauthority:/root/.Xauthority:ro" --network host -it bank-transaction-analyzer
fi
