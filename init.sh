#!/bin/bash

# Source the .env file to load variables
if [ -f .env ]; then
  source .env
else
  echo "You do not have the project's .env file in this directory"
  exit 1
fi

# Optionally, print the variables for debugging
echo "IP Address: $APP_IP_ADDRESS"
echo "Model Endpoint Key: $MODEL_ENDPOINT_KEY"

pip3 install -r requirements.txt

python3 script.py