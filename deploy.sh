#!/bin/bash

# ===========================================
# Chatbot Deployment Script
# ===========================================
# Usage: ./deploy.sh [command]
# Commands: setup, deploy, update, logs, stop, restart, nginx, status

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/opt/chatbot"
APP_SERVICE="chatbot"
NGINX_CONF="/opt/chatbot/deploy/nginx-chatbot.conf"

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Initial setup
setup() {
    print_status "Starting initial setup..."
    
    cd $APP_DIR/app
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        print_status "Creating virtual environment..."
        python3 -m venv venv
    fi
    
    # Activate and install dependencies
    print_status "Installing Python dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Check if .env exists
    if [ ! -f ".env" ]; then
        print_error ".env file not found! Please create it with OPENROUTER_API_KEY"
        exit 1
    fi
    
    print_status "Setup complete!"
    print_warning "Next step: ./deploy.sh nginx"
}

# Deploy application
deploy() {
    print_status "Deploying chatbot application..."
    
    cd $APP_DIR
    
    # Setup if needed
    if [ ! -d "app/venv" ]; then
        setup
    fi
    
    # Pull latest changes if git repo exists
    if [ -d "app/.git" ]; then
        print_status "Pulling latest changes..."
        cd app && git pull origin master && cd ..
    fi
    
    # Install/update dependencies
    print_status "Updating dependencies..."
    cd app
    source venv/bin/activate
    pip install -r requirements.txt
    cd ..
    
    # Restart service
    print_status "Restarting service..."
    sudo systemctl restart $APP_SERVICE
    
    # Wait and check status
    sleep 3
    if systemctl is-active --quiet $APP_SERVICE; then
        print_status "✓ Service is running"
    else
        print_error "Service failed to start!"
        sudo systemctl status $APP_SERVICE
        exit 1
    fi
    
    print_status "Deployment complete!"
    print_status "Chatbot available at: https://chat.meetopia.tech"
}

# Update application
update() {
    print_status "Updating application..."
    
    cd $APP_DIR/app
    
    # Pull latest changes
    if [ -d ".git" ]; then
        print_status "Pulling latest changes..."
        git pull origin master
    fi
    
    # Update dependencies
    print_status "Updating dependencies..."
    source venv/bin/activate
    pip install -r requirements.txt
    
    # Restart service
    print_status "Restarting service..."
    sudo systemctl restart $APP_SERVICE
    
    print_status "Update complete!"
}

# Install nginx configuration
nginx() {
    print_status "Configuring Nginx..."
    
    # Check if nginx config exists
    if [ ! -f "$NGINX_CONF" ]; then
        print_error "Nginx config not found at $NGINX_CONF"
        exit 1
    fi
    
    # Add rate limit zone to nginx.conf if not present
    if ! grep -q "limit_req_zone" /etc/nginx/nginx.conf; then
        print_status "Adding rate limit zone to nginx.conf..."
        sudo sed -i '/http {/a\    limit_req_zone $binary_remote_addr zone=one:10m rate=10r/s;' /etc/nginx/nginx.conf
    fi
    
    # Copy nginx config
    sudo cp $NGINX_CONF /etc/nginx/sites-available/chatbot
    
    # Create symlink if it doesn't exist
    if [ ! -f "/etc/nginx/sites-enabled/chatbot" ]; then
        sudo ln -s /etc/nginx/sites-available/chatbot /etc/nginx/sites-enabled/chatbot
    fi
    
    # Test nginx configuration
    if sudo nginx -t; then
        print_status "Reloading Nginx..."
        sudo systemctl reload nginx
        print_status "Nginx configured successfully!"
    else
        print_error "Nginx configuration test failed!"
        exit 1
    fi
}

# View logs
logs() {
    print_status "Showing chatbot logs (Ctrl+C to exit)..."
    sudo journalctl -u $APP_SERVICE -f
}

# Stop application
stop() {
    print_status "Stopping chatbot service..."
    sudo systemctl stop $APP_SERVICE
    print_status "Service stopped!"
}

# Start application
start() {
    print_status "Starting chatbot service..."
    sudo systemctl start $APP_SERVICE
    sleep 2
    if systemctl is-active --quiet $APP_SERVICE; then
        print_status "✓ Service is running"
    else
        print_error "Service failed to start!"
        sudo systemctl status $APP_SERVICE
    fi
}

# Restart application
restart() {
    print_status "Restarting chatbot service..."
    sudo systemctl restart $APP_SERVICE
    sleep 2
    if systemctl is-active --quiet $APP_SERVICE; then
        print_status "✓ Service restarted successfully"
    else
        print_error "Service failed to restart!"
        sudo systemctl status $APP_SERVICE
    fi
}

# Check system status
status() {
    print_status "Checking system status..."
    
    echo ""
    echo "=== Service Status ==="
    sudo systemctl status $APP_SERVICE --no-pager
    
    echo ""
    echo "=== Nginx Configuration ==="
    sudo nginx -t
    
    echo ""
    echo "=== Recent Logs ==="
    sudo journalctl -u $APP_SERVICE --no-pager -n 20
}

# Install systemd service
install_service() {
    print_status "Installing systemd service..."
    
    sudo cp /opt/chatbot/deploy/chatbot.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable chatbot
    
    print_status "Service installed and enabled!"
}

# Show help
help() {
    echo "Chatbot Deployment Script"
    echo ""
    echo "Usage: ./deploy.sh [command]"
    echo ""
    echo "Commands:"
    echo "  setup      - Initial setup (venv, dependencies)"
    echo "  install    - Install systemd service"
    echo "  deploy     - Full deployment (setup, install, start)"
    echo "  update     - Pull changes and update"
    echo "  nginx      - Configure Nginx"
    echo "  start      - Start the service"
    echo "  stop       - Stop the service"
    echo "  restart    - Restart the service"
    echo "  logs       - View application logs"
    echo "  status     - Check service status"
    echo "  help       - Show this help message"
}

# Main
case "$1" in
    setup)
        setup
        ;;
    install)
        install_service
        ;;
    deploy)
        deploy
        ;;
    update)
        update
        ;;
    nginx)
        nginx
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    status)
        status
        ;;
    help|*)
        help
        ;;
esac
