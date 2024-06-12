#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Adding Golang PPA
sudo add-apt-repository ppa:longsleep/golang-backports -y

# Installing Golang
sudo apt install golang-go -y

# Set the GOPATH environment variable
export GOPATH=$HOME/go
# Update the PATH environment variable to include directories for Go binaries
export PATH=$PATH:$GOROOT/bin:$GOPATH/bin