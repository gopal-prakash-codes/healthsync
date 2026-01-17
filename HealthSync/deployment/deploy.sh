#!/bin/bash

# HealthSync Deployment Script

set -e

# Variables
APP_NAME="healthsync"
REPO_URL="https://github.com/yourusername/healthsync.git"
BRANCH="main"
DOCKER_IMAGE="yourdockerhubusername/$APP_NAME:latest"
DATABASE_URL="postgresql://user:password@localhost:5432/healthsync"
FRONTEND_DIR="HealthSync/frontend"
BACKEND_DIR="HealthSync/backend"

# Function to deploy backend
deploy_backend() {
    echo "Deploying backend..."
    cd $BACKEND_DIR
    # Build Docker image for FastAPI
    docker build -t $DOCKER_IMAGE .
    # Run migrations
    docker run --rm -e DATABASE_URL=$DATABASE_URL $DOCKER_IMAGE alembic upgrade head
    # Start backend service
    docker run -d -p 8000:8000 -e DATABASE_URL=$DATABASE_URL $DOCKER_IMAGE
    echo "Backend deployed successfully."
}

# Function to deploy frontend
deploy_frontend() {
    echo "Deploying frontend..."
    cd $FRONTEND_DIR
    # Build Next.js application
    npm install
    npm run build
    # Start frontend service
    npm start &
    echo "Frontend deployed successfully."
}

# Function to set up CI/CD
setup_cicd() {
    echo "Setting up CI/CD..."
    # Example CI/CD setup using GitHub Actions
    cat <<EOL > .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches:
      - $BRANCH

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v1

      - name: Login to Docker Hub
        uses: docker/login-action@v1
        with:
          username: yourdockerhubusername
          password: \${{ secrets.DOCKER_HUB_PASSWORD }}

      - name: Build and push Docker image
        uses: docker/build-push-action@v2
        with:
          context: .
          push: true
          tags: $DOCKER_IMAGE

      - name: Deploy to server
        run: ssh user@yourserver "cd /path/to/deployment && ./deploy.sh"
EOL
    echo "CI/CD setup completed."
}

# Main script execution
echo "Starting deployment process..."
deploy_backend
deploy_frontend
setup_cicd
echo "Deployment process completed."