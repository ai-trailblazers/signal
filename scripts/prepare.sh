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

# Check if pipreqs is installed and install if it isn't
if ! pip show pipreqs > /dev/null; then
    echo "pipreqs not installed. Installing pipreqs..."
    pip install pipreqs
else
    echo "pipreqs is already installed."
fi

# Install Python dependencies
pip install -r requirements.txt
