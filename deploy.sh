#!/bin/bash

# Exit on error
set -e

echo "Starting deployment process..."

# Build the React frontend
echo "Building React frontend..."
cd frontend
npm install
npm run build
cd ..

# Create a directory to serve static files
mkdir -p static
cp -r frontend/build/* static/

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt
pip install gunicorn

# Create or update database
echo "Setting up database..."
python migrations.py db upgrade
python create_admin.py

# Create a gunicorn service file
echo "Creating gunicorn service file..."
cat > /etc/systemd/system/event-manager.service << EOF
[Unit]
Description=Event Manager Gunicorn Service
After=network.target

[Service]
User=$USER
WorkingDirectory=$(pwd)
ExecStart=$(which gunicorn) --workers 3 --bind 0.0.0.0:5001 --timeout 120 'run:app'
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start the service
echo "Starting the service..."
sudo systemctl daemon-reload
sudo systemctl enable event-manager
sudo systemctl start event-manager

# Set up Nginx to serve both APIs and static content
echo "Setting up Nginx..."
cat > /etc/nginx/sites-available/event-manager << EOF
server {
    listen 80;
    server_name _;

    location /api {
        proxy_pass http://localhost:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }

    location /static {
        alias $(pwd)/static;
    }

    location / {
        root $(pwd)/static;
        try_files \$uri \$uri/ /index.html;
    }
}
EOF

# Enable the site and restart Nginx
sudo ln -sf /etc/nginx/sites-available/event-manager /etc/nginx/sites-enabled/
sudo systemctl restart nginx

echo "Deployment completed! Your application should be running."
echo "You can access it via the Lightsail instance's IP address." 