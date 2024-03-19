#!/bin/bash

ENV_NAME="venv"
source activate $ENV_NAME

python tools/generate_diagrams.py