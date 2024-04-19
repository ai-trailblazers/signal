#!/bin/bash

for file in tools/*.py; do
    python "$file" --format png
done

for file in tools/*.py; do
    python "$file" --format svg
done