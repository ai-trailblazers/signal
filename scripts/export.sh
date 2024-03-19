#!/bin/bash

# Define your environment name
ENV_NAME="venv"

source activate $ENV_NAME
conda env export > environment.yml