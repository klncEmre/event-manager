#!/bin/bash
set -e

echo "Installing dependencies..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv nginx

# Setup Python virtual environment and install dependencies
cd ~/event-manager
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn  # For production server

# Install frontend dependencies and build
cd ~/event-manager/frontend
npm ci
npm run build

# Setup systemd service
cd ~/event-manager
sudo cp event-manager.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable event-manager
sudo systemctl restart event-manager

# Setup Nginx
sudo cp event-manager-nginx.conf /etc/nginx/sites-available/event-manager
sudo ln -sf /etc/nginx/sites-available/event-manager /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo systemctl restart nginx

echo "Deployment completed successfully!"
echo "Your application should be accessible at http://$(curl -s http://checkip.amazonaws.com)" 