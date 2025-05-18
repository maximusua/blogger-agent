#!/bin/bash

# Build Docker image
docker build -t travel-blog-crew .

# Run container with environment variables
docker run --env-file .env travel-blog-crew 