#!/bin/bash

# Exit on error
set -e

# Default environment
ENV=${1:-local}

# Function to run tests
run_tests() {
    local env=$1
    echo "Running tests in $env environment..."
    
    # Clean up any previous test containers
    docker-compose -f docker-compose.test.yml down -v

    # Build and run tests
    if [ "$env" = "prod" ]; then
        # Production environment - use production database settings
        docker-compose -f docker-compose.test.yml run \
            -e POSTGRES_USER=${POSTGRES_USER} \
            -e POSTGRES_PASSWORD=${POSTGRES_PASSWORD} \
            -e POSTGRES_DB=${POSTGRES_DB} \
            -e DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY} \
            test
    else
        # Local environment - use default test settings
        docker-compose -f docker-compose.test.yml run test
    fi

    # Capture the exit code
    local exit_code=$?

    # Clean up
    docker-compose -f docker-compose.test.yml down -v

    # Return the test exit code
    return $exit_code
}

# Main execution
if [ "$ENV" = "prod" ]; then
    echo "Running tests in production environment..."
    run_tests prod
else
    echo "Running tests in local environment..."
    run_tests local
fi 