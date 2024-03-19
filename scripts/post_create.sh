#!/bin/bash

# Define your environment name
ENV_NAME="venv"

# Get the default Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "Detected Python version: $PYTHON_VERSION"

# Check if the environment exists by searching for its path in the list of conda environments
ENV_PATH=$(conda env list | grep $ENV_NAME | awk '{print $2}')
if [ -z "$ENV_PATH" ]; then
    # Environment doesn't exist, so create it using the detected Python version
    echo "Creating Conda environment: $ENV_NAME with Python $PYTHON_VERSION"
    conda create --name $ENV_NAME python=$PYTHON_VERSION -y
else
    echo "Conda environment $ENV_NAME already exists."
fi

# Print the reminder message in light blue
echo -e "\033[1;34mTo activate the environment, run: 'source activate $ENV_NAME'\033[0m"
