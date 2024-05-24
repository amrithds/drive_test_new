#!/bin/bash

# Variables
LOCAL_PROJECT_PATH="C:/Users/hi/Desktop/driving project/frontend"  # Path to your local Angular project
REMOTE_SERVER="super@192.168.1.108"  # SSH username and server IP address
REMOTE_PROJECT_PATH="/var/www/html"  # Path where you want to deploy the project on the server

# Build the Angular project
cd $LOCAL_PROJECT_PATH
npm install
ng build --prod

# Transfer files to the remote server
scp -r $LOCAL_PROJECT_PATH/dist/* $REMOTE_SERVER:$REMOTE_PROJECT_PATH

# Cleanup local build artifacts (optional)
rm -rf $LOCAL_PROJECT_PATH/dist

echo "Deployment completed successfully."
