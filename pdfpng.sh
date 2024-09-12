#!/usr/bin/env bash
pdfName=$1
pngPrefix=$2

# Convert PDF to PNG
pdftoppm "$pdfName" "$pngPrefix" -png

# Move PNGs to a subdirectory
mkdir -p imgs
mv *.png imgs/
