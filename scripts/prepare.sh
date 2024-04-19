#!/bin/bash

sudo apt-get update
sudo apt-get install graphviz -y

# Check if the 'diagrams' directory exists
if [ -d "diagrams" ]; then
    echo "Directory 'diagrams' already exists."
else
    echo "Creating directory 'diagrams'..."
    mkdir diagrams
    echo "Directory 'diagrams' created successfully."
fi

# Check if the virtual environment 'venv' exists
if [ -d "venv" ]; then
    echo "Virtual environment 'venv' already exists."
else
    echo "Creating virtual environment 'venv'..."
    python3 -m venv venv
    echo "Virtual environment 'venv' created successfully."
fi

# Install Python dependencies
pip install -r requirements.txt