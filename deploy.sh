#!/bin/bash

# Production Deployment Script for Conduit
# This script helps deploy and manage the Conduit application in production

set -e

COMPOSE_FILE="docker-compose.prod.yml"
PROJECT_NAME="conduit"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

echo_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

echo_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
check_env() {
    if [ ! -f .env ]; then
        echo_error ".env file not found!"
        echo_info "Please create .env from .env.example:"
        echo "  cp .env.example .env"
        echo "  nano .env  # Configure your environment variables"
        exit 1
    fi
}

# Check if required commands are available
check_requirements() {
    if ! command -v docker &> /dev/null; then
        echo_error "Docker is not installed. Please install Docker first."
        exit 1
    fi

    if ! command -v docker compose &> /dev/null; then
        echo_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
}

# Build all Docker images
build() {
    echo_info "Building Docker images..."
    check_env
    docker compose -f $COMPOSE_FILE build --no-cache
    echo_info "Build complete!"
}

# Start all services
start() {
    echo_info "Starting Conduit services..."
    check_env
    docker compose -f $COMPOSE_FILE up -d
    echo_info "Services started!"
    echo_info "Waiting for services to be healthy..."
    sleep 10
    status
}

# Stop all services
stop() {
    echo_info "Stopping Conduit services..."
    docker compose -f $COMPOSE_FILE stop
    echo_info "Services stopped!"
}

# Restart all services
restart() {
    echo_info "Restarting Conduit services..."
    stop
    start
}

# View logs
logs() {
    SERVICE=${1:-}
    if [ -z "$SERVICE" ]; then
        docker compose -f $COMPOSE_FILE logs -f --tail=100
    else
        docker compose -f $COMPOSE_FILE logs -f --tail=100 $SERVICE
    fi
}

# Check service status
status() {
    echo_info "Service Status:"
    docker compose -f $COMPOSE_FILE ps
    echo ""
    echo_info "Health Checks:"

    # Check backend health
    if curl -s http://localhost/api/health > /dev/null 2>&1; then
        echo_info "✓ Backend API is healthy"
    else
        echo_warn "✗ Backend API is not responding"
    fi

    # Check frontend health
    if curl -s http://localhost/health > /dev/null 2>&1; then
        echo_info "✓ Frontend is healthy"
    else
        echo_warn "✗ Frontend is not responding"
    fi
}

# Run database migrations
migrate() {
    echo_info "Running database migrations..."
    docker compose -f $COMPOSE_FILE exec backend alembic upgrade head
    echo_info "Migrations complete!"
}

# Create a new database migration
create_migration() {
    MESSAGE=${1:-"auto migration"}
    echo_info "Creating new migration: $MESSAGE"
    docker compose -f $COMPOSE_FILE exec backend alembic revision --autogenerate -m "$MESSAGE"
    echo_info "Migration created!"
}

# Access backend shell
shell() {
    echo_info "Opening backend shell..."
    docker compose -f $COMPOSE_FILE exec backend /bin/bash
}

# Access database shell
db_shell() {
    echo_info "Opening database shell..."
    docker compose -f $COMPOSE_FILE exec db psql -U conduit conduit_db
}

# View database
db_view() {
    echo_info "Database information:"
    docker compose -f $COMPOSE_FILE exec db psql -U conduit -d conduit_db -c "\dt"
}

# Backup database
backup() {
    BACKUP_FILE="backup_$(date +%Y%m%d_%H%M%S).sql"
    echo_info "Creating database backup: $BACKUP_FILE"
    docker compose -f $COMPOSE_FILE exec -T db pg_dump -U conduit conduit_db > $BACKUP_FILE
    echo_info "Backup saved to: $BACKUP_FILE"
}

# Restore database from backup
restore() {
    BACKUP_FILE=${1:-}
    if [ -z "$BACKUP_FILE" ]; then
        echo_error "Please provide backup file path"
        echo "Usage: $0 restore <backup_file.sql>"
        exit 1
    fi

    if [ ! -f "$BACKUP_FILE" ]; then
        echo_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi

    echo_warn "This will restore the database from: $BACKUP_FILE"
    read -p "Are you sure? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
        echo_info "Restore cancelled"
        exit 0
    fi

    echo_info "Restoring database..."
    docker compose -f $COMPOSE_FILE exec -T db psql -U conduit conduit_db < $BACKUP_FILE
    echo_info "Restore complete!"
}

# Clean up (remove containers and volumes)
clean() {
    echo_warn "This will remove all containers and volumes!"
    read -p "Are you sure? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy]es$ ]]; then
        echo_info "Clean cancelled"
        exit 0
    fi

    echo_info "Cleaning up..."
    docker compose -f $COMPOSE_FILE down -v
    echo_info "Cleanup complete!"
}

# Full deployment (build, start, migrate)
deploy() {
    echo_info "Starting full deployment..."
    check_requirements
    build
    start
    migrate
    echo_info "Deployment complete!"
    echo ""
    status
}

# Show help
help() {
    cat << EOF
Conduit Production Deployment Script

Usage: $0 [command]

Commands:
    deploy          Full deployment (build, start, migrate)
    build           Build Docker images
    start           Start all services
    stop            Stop all services
    restart         Restart all services
    status          Show service status and health
    logs [service]  View logs (optional: specify service name)
    migrate         Run database migrations
    create-migration <message>  Create new migration
    shell           Access backend shell
    db-shell        Access database shell
    db-view         View database tables
    backup          Create database backup
    restore <file>  Restore database from backup
    clean           Remove all containers and volumes
    help            Show this help message

Examples:
    $0 deploy                    # Full deployment
    $0 logs backend              # View backend logs
    $0 create-migration "add user field"
    $0 backup                    # Create backup
    $0 restore backup_20240101_120000.sql

Environment:
    Configuration is loaded from .env file
    Create .env from .env.example before deployment

For more information, see DEPLOYMENT.md
EOF
}

# Main command router
case "${1:-help}" in
    deploy)
        deploy
        ;;
    build)
        build
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
    status)
        status
        ;;
    logs)
        logs "${2:-}"
        ;;
    migrate)
        migrate
        ;;
    create-migration)
        create_migration "${2:-auto migration}"
        ;;
    shell)
        shell
        ;;
    db-shell)
        db_shell
        ;;
    db-view)
        db_view
        ;;
    backup)
        backup
        ;;
    restore)
        restore "${2:-}"
        ;;
    clean)
        clean
        ;;
    help|--help|-h)
        help
        ;;
    *)
        echo_error "Unknown command: $1"
        echo ""
        help
        exit 1
        ;;
esac
