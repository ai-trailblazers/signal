#!/bin/bash

# Find the path to the conda executable
CONDA_PATH=$(which conda)

# Exit if Conda is not found
if [ -z "$CONDA_PATH" ]; then
    echo "Conda not found. Please ensure Conda is installed and added to your PATH."
    return
fi

# Extract the directory by removing '/bin/conda'
CONDA_DIR=$(dirname $(dirname $CONDA_PATH))

# Initialize Conda
source "$CONDA_DIR/etc/profile.d/conda.sh"

# Activate the environment
conda activate venv  # Replace 'venv' with the name of your Conda environment
