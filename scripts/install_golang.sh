#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# Adding Golang PPA
sudo add-apt-repository ppa:longsleep/golang-backports -y

# Installing Golang
sudo apt install golang-go -y