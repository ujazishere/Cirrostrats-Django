#!/bin/bash

# Set DOCKER_CONFIG env variable
export DOCKER_CONFIG=${DOCKER_CONFIG:-$HOME/.docker}

# Create directory
mkdir -p $DOCKER_CONFIG/cli-plugins

# Download latest Docker Compose binary
LATEST_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep 'tag_name' | cut -d\" -f4)
curl -SL https://github.com/docker/compose/releases/download/$LATEST_VERSION/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose

# Apply executable permissions
chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose

# Install Docker
sudo yum install -y docker

# Start and enable(auto-start on reboot) Docker service
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker $USER

echo -e "\nDocker and Docker Compose installed successfully."
echo -e "\nIf permission/privileges error persists, you might need to logout and log back in for changes to take effect. Maybe give it few mins:\n"
echo "Alternatively, you can run: newgrp docker"