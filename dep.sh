#!/bin/bash
# CodeHub Deployment Terminal Script
#
# This script helps manage the CodeHub deployment container environment.
# It handles building and running the Docker container and provides various
# utility commands.
#
# Usage: ./dep.sh [command]
#

# =============================================================================
# Constants and Configuration
# =============================================================================
CONTAINER_NAME="codehub-deployment"

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Determine Docker Compose command based on availability
if command -v docker compose &> /dev/null; then
    DOCKER_COMPOSE="docker compose"
elif command -v docker-compose &> /dev/null; then
    DOCKER_COMPOSE="docker-compose"
else
    echo "Error: Docker Compose is not installed"
    exit 1
fi

# =============================================================================
# Helper Functions
# =============================================================================

# Display help information
show_help() {
    echo ""
    echo "Codehub Deployment Terminal — is a humble script created to help you deal with"
    echo "the Docker container encapsulating CodeHub deployment tooling and setup."
    echo ""
    echo "Run it without any parameters to build (if necessary), start, and connect to the container."
    echo "After you terminate the initial instance, the container will automatically shut down."
    echo "If the container is already running, the script will connect you to it."
    echo ""
    echo "Commands for sophisticated troubleshooting and development:"
    echo "  dep.sh --rebuild   - Force rebuild the container image"
    echo "  dep.sh --help      - Display this help message"
    echo ""
}

# Clean up resources when exiting
cleanup() {
    echo "Cleaning up..."
    $DOCKER_COMPOSE down
}

# Check if container is already running
is_container_running() {
    if docker ps --format "{{.Names}}" | grep -q "$CONTAINER_NAME"; then
        return 0
    else
        return 1
    fi
}

# Check if container needs to be built
check_and_build() {
    local force_rebuild=$1

    # Skip build if image exists and no force rebuild requested
    if docker images | grep -q "$CONTAINER_NAME" && [ "$force_rebuild" != "force" ]; then
        echo "Container image already exists and no force rebuild requested. Skipping build."
        return 0
    fi

    echo "Building container image..."
    if ! docker build --no-cache .; then
        echo "Error: Failed to build container image."
        return 1
    fi

    return 0
}

# Connect to a running container
connect_to_container() {
    cd "$SCRIPT_DIR"
    local running_container=$(docker ps --format "{{.Names}}" | grep "$CONTAINER_NAME" | head -n 1)

    if [ -z "$running_container" ]; then
        echo "Error: No running $CONTAINER_NAME container found."
        exit 1
    fi

    docker exec -it "$running_container" zsh -c "./utils/postrun.sh && zsh"
}

# =============================================================================
# Main Script Logic
# =============================================================================

# Make all .sh files in the utils directory executable
if [ -d "utils" ]; then
    chmod +x utils/*.sh
fi

# Default command is 'default' if none provided
if [ -z "$1" ]; then
    set -- "default"
fi

# Handle commands
case "$1" in
    "default")
        # Check if container is already running
        if ! is_container_running; then
            # Set up cleanup trap only if we're starting a new container
            trap cleanup EXIT

            # Build if necessary
            check_and_build

            # Start container
            if ! $DOCKER_COMPOSE up -d; then
                echo "Error: Failed to start the container."
                exit 1
            fi

            echo "Container started successfully."
        fi

        # Clear screen and connect regardless of whether container was already running
        clear
        connect_to_container
        ;;

    "--rebuild")
        echo "Force rebuilding the container..."
        check_and_build "force"
        ;;

    "--help")
        show_help
        ;;

    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
