#!/bin/bash

# This script reliably starts the AI Career Predictor application.

echo "--- Stopping any old server processes on port 5000 ---"
# Use fuser to find and kill any process using TCP port 5000.
fuser -k 5000/tcp

echo "--- Navigating to the application directory ---"
cd "/workspaces/ai-powered-work-in-progress/ai powered"

echo "--- Starting the Flask application ---"
# Run the python server, which is now configured to be accessible externally.
python app.py
