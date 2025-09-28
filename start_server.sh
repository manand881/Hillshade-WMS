#!/bin/bash

# =============================================================================
# WMS Server Startup Script
# =============================================================================
# This script starts the Gunicorn server with optimized settings for the WMS service.
# It's designed to handle concurrent requests efficiently while maintaining stability.

# Server Configuration
# -----------------------------------------------------------------------------
# Binding and Network
#   --bind 0.0.0.0:8080    Listen on all network interfaces on port 8080
#
# Worker Configuration
#   --workers $WORKERS       # Number of worker processes (ceil(CPU cores / 2))
#                           # Using half the CPU cores to prevent memory contention
#                           # and leave resources for other system processes
#   --threads 2             # Number of threads per worker
#   --worker-class gthread  # Use thread-based workers for I/O-bound operations
#   --preload               # Load application code before forking workers
#
# Timeouts and Keep-Alive
#   --timeout 60          # Maximum request processing time (60 seconds)
#                         # Set to balance between preventing hanging requests and
#                         # allowing sufficient time for complex WMS operations
#   --keep-alive 5         # Keep-alive timeout for connections (seconds)
#
# Worker Lifecycle
#   --max-requests 1000    # Restart workers after this many requests
#   --max-requests-jitter 50  # Add randomness to worker restarts to prevent thundering herd
#
# Logging
#   --log-level info       # Logging level (debug, info, warning, error, critical)
#   --access-logfile -     # Send access logs to stdout
#   --error-logfile -      # Send error logs to stderr
#
# Performance
#   --worker-tmp-dir /dev/shm  # Use shared memory for worker temp files

# Start the Gunicorn server with the specified configuration
rm /tmp/wms_tile_*
mkdir -p logs

# Calculate half the number of CPU cores, with a minimum of 1
NUM_CORES=$(nproc)
WORKERS=$(( (NUM_CORES + 1) / 2 ))  # This ensures we get ceil(NUM_CORES/2)

exec gunicorn \
    --bind 0.0.0.0:8080 \
    --workers $WORKERS \
    --threads 2 \
    --timeout 60 \
    --keep-alive 5 \
    --max-requests 1000 \
    --max-requests-jitter 50 \
    --worker-class gthread \
    --log-level info \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log \
    --worker-tmp-dir /dev/shm \
    --preload \
    app:app