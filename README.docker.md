# Docker Deployment for ASMR Conspiracy Generator

This guide explains how to deploy the ASMR Conspiracy Generator using Docker.

## Prerequisites

- Docker installed on your system
- Docker Compose installed on your system
- Mistral LLM model file (GGUF format)
- Background music file (optional)

## Setup Instructions

1. **Prepare model directory**:
   ```
   mkdir -p models
   ```

2. **Download the Mistral model**:
   
   Download the Mistral model file and place it in the `models` directory with the name:
   ```
   models/mistral-7b-instruct-v0.1.Q4_K_M.gguf
   ```
   
3. **Prepare background music**:
   
   Place your horror background music file in:
   ```
   models/background_music/horror-background-atmosphere-11-240870.mp3
   ```

## Deployment Commands

### Building the Docker Images

```bash
docker-compose build
```

### Starting All Services

```bash
docker-compose up -d
```

This will start the gRPC server, REST API, and Streamlit UI.

### Accessing the Services

- **Streamlit UI**: http://localhost:8501
- **REST API**: http://localhost:8000
- **gRPC Server**: localhost:50051

### Viewing Logs

```bash
docker-compose logs -f
```

### Stopping Services

```bash
docker-compose down
```

## Service-Specific Commands

### Starting Only the gRPC Server

```bash
docker-compose up -d grpc-server
```

### Starting Only the REST API

```bash
docker-compose up -d grpc-server rest-api
```

### Starting Only the UI

```bash
docker-compose up -d grpc-server rest-api ui
```

## Deployment Script (deploy.sh)

On Unix/Linux/Mac systems, you can use the included deployment script:

```bash
chmod +x deploy.sh
./deploy.sh start
```

On Windows, you can use PowerShell to run the Docker Compose commands directly:

```powershell
docker-compose up -d
```

## Troubleshooting

### Service Not Starting

Check the logs:
```bash
docker-compose logs -f [service-name]
```

### Model Loading Issues

Ensure the Mistral model file is correctly placed in the models directory and named correctly.

### Audio Generation Issues

Make sure the background music file exists and is correctly placed in the models directory.

## Environment Variables

You can customize the deployment by setting these environment variables:

- `MISTRAL_MODEL_PATH`: Path to the Mistral model file inside the container
- `GRPC_SERVER`: Address of the gRPC server
- `API_URL`: URL of the REST API for the UI to connect to 