#!/bin/bash
# Audiobook Integrity Verification Runner
# This script runs the verification tool inside the Docker container

CONTAINER_NAME="audiobookDownloader"

# Check if container is running
if ! docker ps --format "table {{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo "❌ Container '${CONTAINER_NAME}' is not running."
    echo "Please start the container first."
    exit 1
fi

echo "🔍 Running audiobook integrity verification..."
echo "Container: ${CONTAINER_NAME}"
echo ""

# Run the verification script inside the container
docker exec -it "${CONTAINER_NAME}" python /app/verify_integrity.py "$@"