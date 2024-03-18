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

# conda init

# Activate the environment
# echo "Activating environment: $ENV_NAME"
# source activate $ENV_NAME

# Note: Activating Conda environments in a script affects only the subshell created by the script.
# To have the environment activated in the parent shell, you need to run 'source' on this script or activate the environment manually.
