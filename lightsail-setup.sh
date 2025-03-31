#!/bin/bash

# Update packages
sudo apt-get update
sudo apt-get upgrade -y

# Install Python and required tools
sudo apt-get install -y python3-pip python3-dev build-essential libssl-dev libffi-dev python3-setuptools python3-venv git nginx

# Create a Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Clone repository (replace with your Git repository URL)
# git clone YOUR_REPOSITORY_URL
# cd YOUR_PROJECT_DIRECTORY

# Install dependencies
pip install -r requirements.txt

# Set up Nginx
sudo bash -c 'cat > /etc/nginx/sites-available/event-manager << EOL
server {
    listen 80;
    server_name YOUR_LIGHTSAIL_IP;

    location / {
        proxy_pass http://localhost:5001;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOL'

sudo ln -s /etc/nginx/sites-available/event-manager /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx

# Create a systemd service file
sudo bash -c 'cat > /etc/systemd/system/event-manager.service << EOL
[Unit]
Description=Event Manager Flask App
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/event-manager
Environment="PATH=/home/ubuntu/event-manager/venv/bin"
ExecStart=/home/ubuntu/event-manager/venv/bin/gunicorn --workers 3 --bind 0.0.0.0:5001 run:app
Restart=always

[Install]
WantedBy=multi-user.target
EOL'

# Enable and start the service
sudo systemctl enable event-manager
sudo systemctl start event-manager

echo "Deployment completed!" 