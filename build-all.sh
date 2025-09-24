#!/bin/bash

# Goline Library Chatbot - Build All Docker Images Script
# This script builds both UI and backend Docker images

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
UI_IMAGE_NAME="goline-chatbot-ui"
BACKEND_IMAGE_NAME="goline-chatbot-backend"
VERSION=${1:-"latest"}  # Use first argument as version, default to "latest"

# Function to print colored messages
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if Docker is running
check_docker() {
    print_info "Checking Docker availability..."
    if ! docker info >/dev/null 2>&1; then
        print_error "Docker is not running or not accessible. Please start Docker and try again."
        exit 1
    fi
    print_success "Docker is running"
}

# Function to build UI image
build_ui() {
    print_info "Building Chatbot UI Docker image..."
    print_info "Image: ${UI_IMAGE_NAME}:${VERSION}"
    
    cd chabot_ui
    
    if docker build -t "${UI_IMAGE_NAME}:${VERSION}" .; then
        print_success "UI image built successfully: ${UI_IMAGE_NAME}:${VERSION}"
    else
        print_error "Failed to build UI image"
        exit 1
    fi
    
    cd ..
}

# Function to build Backend image
build_backend() {
    print_info "Building Chatbot Backend Docker image..."
    print_info "Image: ${BACKEND_IMAGE_NAME}:${VERSION}"
    
    cd chatbot_backend
    
    if docker build -t "${BACKEND_IMAGE_NAME}:${VERSION}" .; then
        print_success "Backend image built successfully: ${BACKEND_IMAGE_NAME}:${VERSION}"
    else
        print_error "Failed to build backend image"
        exit 1
    fi
    
    cd ..
}

# Function to show image sizes
show_images() {
    print_info "Docker images created:"
    echo ""
    docker images | grep -E "(${UI_IMAGE_NAME}|${BACKEND_IMAGE_NAME})" | head -10
    echo ""
}

# Function to cleanup build artifacts (optional)
cleanup() {
    print_info "Cleaning up Docker build cache..."
    docker builder prune -f >/dev/null 2>&1 || true
    print_success "Build cache cleaned"
}

# Function to tag images as latest if version is not latest
tag_latest() {
    if [ "${VERSION}" != "latest" ]; then
        print_info "Tagging images as latest..."
        docker tag "${UI_IMAGE_NAME}:${VERSION}" "${UI_IMAGE_NAME}:latest"
        docker tag "${BACKEND_IMAGE_NAME}:${VERSION}" "${BACKEND_IMAGE_NAME}:latest"
        print_success "Images tagged as latest"
    fi
}

# Main execution
main() {
    print_info "=== Goline Chatbot Docker Build Script ==="
    print_info "Building version: ${VERSION}"
    echo ""
    
    # Check prerequisites
    check_docker
    
    # Build images
    build_ui
    echo ""
    build_backend
    echo ""
    
    # Tag as latest if needed
    tag_latest
    
    # Show results
    show_images
    
    # Optional cleanup
    if [ "${CLEANUP:-false}" = "true" ]; then
        cleanup
    fi
    
    print_success "=== Build completed successfully! ==="
    print_info "To run the application, use: docker-compose up -d"
    
    echo ""
    print_info "Available images:"
    print_info "  • ${UI_IMAGE_NAME}:${VERSION}"
    print_info "  • ${BACKEND_IMAGE_NAME}:${VERSION}"
    if [ "${VERSION}" != "latest" ]; then
        print_info "  • ${UI_IMAGE_NAME}:latest"
        print_info "  • ${BACKEND_IMAGE_NAME}:latest"
    fi
}

# Help function
show_help() {
    echo "Usage: $0 [VERSION] [OPTIONS]"
    echo ""
    echo "Arguments:"
    echo "  VERSION        Docker image version tag (default: latest)"
    echo ""
    echo "Environment Variables:"
    echo "  CLEANUP=true   Cleanup Docker build cache after build"
    echo ""
    echo "Examples:"
    echo "  $0                    # Build with 'latest' tag"
    echo "  $0 v1.0.0            # Build with 'v1.0.0' tag"
    echo "  CLEANUP=true $0      # Build and cleanup cache"
    echo ""
    echo "Images built:"
    echo "  • ${UI_IMAGE_NAME}"
    echo "  • ${BACKEND_IMAGE_NAME}"
}

# Parse command line arguments
case "${1:-}" in
    -h|--help|help)
        show_help
        exit 0
        ;;
    *)
        main "$@"
        ;;
esac