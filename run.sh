#!/bin/bash

echo "Stopping and removing existing containers..."
docker compose down

echo "Starting the application..."
docker compose up --build --detach