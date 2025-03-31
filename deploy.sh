#!/bin/bash
set -e

# Configuration
REPO_URL="https://github.com/klncEmre/event-manager.git"  # Replace with your actual repo URL
APP_DIR="/home/ubuntu/event-manager"
VENV_DIR="$APP_DIR/venv"

echo "Starting deployment process..."

# Navigate to app directory or clone if it doesn't exist
if [ -d "$APP_DIR" ]; then
  echo "Repository exists, pulling latest changes..."
  cd $APP_DIR
  git pull
else
  echo "Cloning repository..."
  git clone $REPO_URL $APP_DIR
  cd $APP_DIR
fi

# Ensure virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
  echo "Creating virtual environment..."
  python3 -m venv $VENV_DIR
fi

# Activate virtual environment and install dependencies
echo "Installing dependencies..."
source $VENV_DIR/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Set up environment file if it doesn't exist
if [ ! -f "$APP_DIR/.env" ]; then
  echo "Creating .env file..."
  cp .env.example .env
  # Replace these with secure values in production
  sed -i "s/gen-a-long-random-string-here-for-production/$(openssl rand -hex 24)/" .env
  sed -i "s/use-a-different-secret-key-here-for-jwt/$(openssl rand -hex 24)/" .env
fi

# Run database migrations
echo "Running database migrations..."
flask db upgrade || echo "Migration failed. If this is the first run, you may need to initialize migrations."

# Restart the service
echo "Restarting application service..."
sudo systemctl restart event-manager

echo "Deployment completed successfully!" 