#!/bin/sh
set -e

if [ -z "$DOPPLER_TOKEN" ]; then
    echo "Doppler token is not set"
    exit 1
fi

doppler configure set token "$DOPPLER_TOKEN" --scope project --scope config