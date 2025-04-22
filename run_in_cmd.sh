#!/bin/bash

# Check if .env file exists
if [ -f ".env" ]; then
    # Read .env file and export variables
    while IFS='=' read -r key value; do
        # Skip empty lines and comments
        if [ -n "$key" ] && ! [[ "$key" =~ ^[[:space:]]*# ]]; then
            # Remove leading/trailing whitespace and quotes
            key=$(echo "$key" | xargs)
            value=$(echo "$value" | xargs | sed -e 's/^"//;s/"$//')
            export "$key=$value"
        fi
    done < .env
fi
if [ -z "$1" ]; then
    python agent_code.py
else
    python "$1"
fi