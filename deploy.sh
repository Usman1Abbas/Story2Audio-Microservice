#!/bin/bash
set -e

# ANSI colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to print colored messages
log() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
mkdir -p models generated

# Check for model file
MODEL_FILE="models/mistral-7b-instruct-v0.1.Q4_K_M.gguf"
if [ ! -f "$MODEL_FILE" ]; then
    warn "Mistral model file not found at $MODEL_FILE"
    echo "Do you want to download the model now? (y/n)"
    read -r answer
    if [[ "$answer" == "y" ]]; then
        log "Downloading Mistral model..."
        # Use curl or wget to download the model to the models directory
        # This is a placeholder - you'll need to provide the actual download URL
        # curl -L <model_url> -o $MODEL_FILE
        warn "Model download placeholder - please manually download the model"
        warn "and place it in the models directory as 'mistral-7b-instruct-v0.1.Q4_K_M.gguf'"
    else
        warn "Please manually place the model file at $MODEL_FILE before starting the services"
    fi
fi

# Check for background music file
MUSIC_DIR="models/background_music"
mkdir -p "$MUSIC_DIR"
if [ ! -f "$MUSIC_DIR/horror-background-atmosphere-11-240870.mp3" ]; then
    warn "Horror background music not found"
    echo "Do you want to use a placeholder silent audio file? (y/n)"
    read -r answer
    if [[ "$answer" == "y" ]]; then
        log "Creating placeholder silent audio..."
        # Requires ffmpeg to be installed
        if command -v ffmpeg &> /dev/null; then
            ffmpeg -f lavfi -i anullsrc=r=44100:cl=stereo -t 30 -q:a 9 -acodec libmp3lame "$MUSIC_DIR/horror-background-atmosphere-11-240870.mp3"
        else
            warn "ffmpeg not installed, skipping placeholder audio creation"
        fi
    fi
fi

# Function to show usage instructions
show_usage() {
    echo "Usage: $0 [COMMAND]"
    echo "Commands:"
    echo "  start        Start all services"
    echo "  stop         Stop all services"
    echo "  restart      Restart all services"
    echo "  logs         Show logs from all services"
    echo "  build        Rebuild the Docker images"
    echo "  status       Show status of the services"
    echo "  grpc         Start only the gRPC server"
    echo "  rest         Start only the REST API (requires gRPC server)"
    echo "  ui           Start only the UI (requires REST API)"
    echo "  clean        Remove containers, images, and volumes"
    echo "  help         Show this help message"
}

# Check if a command was provided
if [ "$#" -eq 0 ]; then
    show_usage
    exit 0
fi

# Process commands
case "$1" in
    start)
        log "Starting all services..."
        docker-compose up -d
        log "Services started. UI available at http://localhost:8501"
        ;;
    stop)
        log "Stopping all services..."
        docker-compose down
        log "Services stopped"
        ;;
    restart)
        log "Restarting all services..."
        docker-compose restart
        log "Services restarted"
        ;;
    logs)
        log "Showing logs..."
        docker-compose logs -f
        ;;
    build)
        log "Building Docker images..."
        docker-compose build --no-cache
        log "Build completed"
        ;;
    status)
        log "Service status:"
        docker-compose ps
        ;;
    grpc)
        log "Starting gRPC server only..."
        docker-compose up -d grpc-server
        log "gRPC server started on port 50051"
        ;;
    rest)
        log "Starting REST API only..."
        docker-compose up -d grpc-server rest-api
        log "REST API started on port 8000"
        ;;
    ui)
        log "Starting UI only..."
        docker-compose up -d grpc-server rest-api ui
        log "UI started at http://localhost:8501"
        ;;
    clean)
        log "Cleaning up containers and volumes..."
        docker-compose down -v
        log "Removing Docker images..."
        docker rmi $(docker images -q asmr-service-*) 2>/dev/null || true
        log "Clean up completed"
        ;;
    help)
        show_usage
        ;;
    *)
        error "Unknown command: $1"
        show_usage
        exit 1
        ;;
esac

exit 0 