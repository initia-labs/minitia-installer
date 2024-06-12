#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

sudo apt-get update
sudo apt install postgresql postgresql-contrib -y
