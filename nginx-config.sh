#!/bin/bash
set -e

# Replace placeholder IP with the actual IP address
sudo sed -i 's/YOUR_LIGHTSAIL_IP/44.222.152.93/g' /etc/nginx/sites-available/event-manager

# Test Nginx configuration
sudo nginx -t

# Reload Nginx to apply changes
sudo systemctl reload nginx

echo "Nginx configuration updated with IP: 44.222.152.93" 