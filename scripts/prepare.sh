#!/bin/bash

sudo apt-get update
sudo apt-get install graphviz -y

# Install Python dependencies
pip install -r requirements.txt
