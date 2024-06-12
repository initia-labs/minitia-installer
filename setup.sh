#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

sudo apt update
sudo apt upgrade
sudo apt install python3-pip -y

chmod +x scripts/*.sh
pip install typer