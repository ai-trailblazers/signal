#!/bin/bash

# Ensure conda is installed
if ! command -v conda &> /dev/null
then
    echo "conda could not be found, installing..."
    pip install conda
else
    echo "conda is already installed."
fi

# # Check the current Python version
# PYTHON_VERSION=$(python --version | cut -d ' ' -f 2 | cut -d '.' -f1-2)
# echo "Detected Python version: $PYTHON_VERSION"

# # Create a pipenv environment with the detected Python version
# pipenv --python $PYTHON_VERSION

# # Activate the pipenv environment
# echo "To activate the pipenv environment, run 'pipenv shell' or use 'pipenv run' before your commands."
