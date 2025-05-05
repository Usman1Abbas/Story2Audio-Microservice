# ASMR Conspiracy Generator

A complete platform for generating immersive ASMR conspiracy stories and audio narrations using AI.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Standard Installation](#standard-installation)
  - [Docker Installation](#docker-installation)
- [Usage](#usage)
  - [Web Interface](#web-interface)
  - [REST API](#rest-api)
  - [gRPC Client](#grpc-client)
- [API Reference](#api-reference)
  - [gRPC Service](#grpc-service)
  - [REST Endpoints](#rest-endpoints)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [Voice and Audio Settings](#voice-and-audio-settings)
- [Development](#development)
  - [Project Structure](#project-structure)
  - [Testing](#testing)
- [Deployment](#deployment)
  - [Docker Deployment](#docker-deployment)
  - [Manual Deployment](#manual-deployment)
- [Troubleshooting](#troubleshooting)
- [License](#license)

## Overview

The ASMR Conspiracy Generator uses AI to create engaging and immersive conspiracy stories, then converts them to high-quality ASMR audio narrations with background music. The system is built with a microservices architecture providing both gRPC and REST interfaces, along with a user-friendly web interface.

## Architecture

The project consists of three main components:

1. **gRPC Server**: Core service handling story generation via the Mistral LLM and audio conversion with pyttsx3 and pydub
2. **REST API**: HTTP wrapper around the gRPC service, allowing easy integration with web applications
3. **Streamlit UI**: User-friendly web interface for generating and experiencing ASMR conspiracy content

![Architecture Diagram](https://mermaid.ink/img/pako:eNp1kU1PwzAMhv9KlHMrtcCBQ6UdNoaESdMEh10il7qlVfNh2ekGVf87SXdAGi2HyI7fR3beYGNEgYrmrS56bVZGRFDRs3HWF9q21lWSYvV0f_foYTOeOGjuQSQ5_xQhNrXvapMPVn4Ky6WV8N_IOK3AyHAC78FyHnKn3MbPMQBrSaL6WZJOlBUdxqjVVRqdzTwHQ-TDZV-HdU_-0K8FxpHt_F5WvdXO5LfIaLxAjEodqWbBcqH7fITeMYRGuxpDYZxMkBTuPF8LBJu0mKOCyqaK-vUkgbvk82UchvXG7QJQz_GNV_l2PF3LzUQa9QZLypJtj5WrJVY8Wkms1AZcHsLBFVYYXpSvozLOxsKf01_yGLwW)

## Features

- **Story Generation**: Create detailed and atmospheric conspiracy stories on any topic
- **Audio Conversion**: Transform written stories into ASMR audio with:
  - Voice modulation for optimal ASMR effect
  - Background music integration
  - Female voice prioritization
- **Voice Customization**: Control speech rate, volume, and pitch
- **Multiple Interfaces**: Access via web UI, REST API, or gRPC
- **Containerization**: Docker support for easy deployment
- **Extensive Testing**: Comprehensive test suite

## Prerequisites

- Python 3.8+ 
- Mistral LLM model file (GGUF format)
- Background music file (optional)
- Docker and Docker Compose (for containerized deployment)

## Installation

### Standard Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd asmr-generator
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Compile protobuf definitions:
```bash
python compile_proto.py
```

5. Download the Mistral model:
   - Place the Mistral model file in the root directory or set the `MISTRAL_MODEL_PATH` environment variable

6. Prepare background music:
   - Place the background music file at a location accessible by the application
   - Set the `BACKGROUND_MUSIC_PATH` environment variable if needed

### Docker Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd asmr-generator
```

2. Create model directories:
```bash
mkdir -p models/background_music
```

3. Download the Mistral model:
   - Place the model in `models/mistral-7b-instruct-v0.1.Q4_K_M.gguf`

4. Add background music:
   - Place the music in `models/background_music/horror-background-atmosphere-11-240870.mp3`

5. Build and run with Docker Compose:
```bash
docker-compose build
docker-compose up -d
```

## Usage

### Web Interface

1. Start the Streamlit UI:
   - If using Docker: `docker-compose up -d ui`
   - If standard installation: `streamlit run app.py`

2. Open your browser to http://localhost:8501

3. Use the interface to:
   - Generate new conspiracy stories with audio
   - Convert existing stories to audio
   - Browse generated files

### REST API

The REST API provides the following endpoints:

- **Generate a Story**: `POST /api/generate-story`
- **Generate Audio**: `POST /api/generate-audio`
- **Generate Both**: `POST /api/generate`
- **Access Audio File**: `GET /api/audio/{filename}`
- **Access Story File**: `GET /api/story/{filename}`

Example using cURL:
```bash
curl -X POST \
  http://localhost:8000/api/generate \
  -F "topic=alien abductions" \
  -F "max_tokens=3000" \
  -F "temperature=0.8"
```

### gRPC Client

Use the provided command-line client:

```bash
# Generate a story
python asmr_client.py --action story --topic "ancient aliens"

# Generate audio from a story file
python asmr_client.py --action audio --story-file "asmr_conspiracy_ancient_aliens.txt"

# Generate both story and audio
python asmr_client.py --action both --topic "illuminati"
```

## API Reference

### gRPC Service

The gRPC service defines the following methods:

#### GenerateStory
Generates a conspiracy story based on a topic.

**Request**:
- `topic` (string): The conspiracy topic to write about
- `max_tokens` (int, optional): Maximum token length for generation
- `temperature` (float, optional): Creativity level (0.0-1.0)

**Response**:
- `story` (string): The generated story text
- `file_path` (string): Path to the saved story file
- `status` (string): Status of the operation

#### GenerateAudio
Converts a story file to ASMR audio.

**Request**:
- `story_file` (string): Path to the story file
- `voice_settings` (VoiceSettings, optional): Custom voice parameters
- `use_background_music` (bool, optional): Whether to use background music
- `voice_index` (int, optional): Index of voice to use

**Response**:
- `audio_file_path` (string): Path to the generated audio file
- `status` (string): Status of the operation

#### GenerateStoryAndAudio
Generates both a story and audio in one call.

**Request**: (Same as GenerateStory)

**Response**:
- `story` (string): The generated story
- `story_file_path` (string): Path to the story file
- `audio_file_path` (string): Path to the audio file
- `status` (string): Status of the operation
- `used_voice_settings` (VoiceSettings): Voice settings used

### REST Endpoints

#### POST /api/generate-story
Generates a conspiracy story.

**Form Parameters**:
- `topic` (required): Conspiracy topic
- `max_tokens` (optional): Maximum tokens (default: 4000)
- `temperature` (optional): Creativity level (default: 0.8)

**Response**: JSON with story text and file path

#### POST /api/generate-audio
Converts a story to audio.

**Form Parameters**:
- `story_file` (required): Path to story file

**Response**: JSON with audio file path

#### POST /api/generate
Generates both story and audio.

**Form Parameters**: (Same as /api/generate-story)

**Response**: JSON with story text and both file paths

## Configuration

### Environment Variables

- `MISTRAL_MODEL_PATH`: Path to the Mistral LLM model file
- `BACKGROUND_MUSIC_PATH`: Path to the background music file
- `GRPC_SERVER`: Address of the gRPC server (default: "localhost:50051")
- `API_URL`: URL of the REST API for the UI (default: "http://localhost:8000/api")

### Voice and Audio Settings

The ASMR voice settings can be customized with:

- **Rate**: Speech speed (90-130, default: 130)
- **Volume**: Audio volume (0.0-1.0, default: 0.65)
- **Pitch**: Voice pitch adjustment (default: 1.0)
- **Background Music**: Optional atmospheric music with volume reduction

## Development

### Project Structure

```
asmr-generator/
├── asmr_server.py       # gRPC service implementation
├── asmr_client.py       # Command-line client
├── asmr_service.proto   # Protocol buffer definitions
├── rest_api.py          # REST API wrapper
├── app.py               # Streamlit UI
├── compile_proto.py     # Protobuf compiler script
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
├── deploy.sh            # Deployment script
├── test_asmr_service.py # Unit tests
├── run_without_docker.bat # Windows script for non-Docker execution
└── requirements.txt     # Python dependencies
```

### Testing

Run the test suite to ensure everything works correctly:

```bash
python test_asmr_service.py
```

The tests cover:
- Story generation
- Audio conversion
- Error handling
- Integration between components

## Deployment

### Docker Deployment

Use the provided docker-compose.yml:

```bash
# Build the images
docker-compose build

# Start all services
docker-compose up -d

# Start specific services
docker-compose up -d grpc-server
docker-compose up -d rest-api
docker-compose up -d ui

# View logs
docker-compose logs -f
```

For Unix/Linux systems, you can use the deployment script:

```bash
chmod +x deploy.sh
./deploy.sh start
```

### Manual Deployment

For Windows systems without Docker, use the batch script:

```bat
run_without_docker.bat all
```

Or start individual components:

```bat
run_without_docker.bat grpc
run_without_docker.bat rest
run_without_docker.bat ui
```

## Troubleshooting

### Docker Issues

- **Service not starting**: Check logs with `docker-compose logs [service-name]`
- **Model not found**: Ensure the model file is correctly placed in the models directory
- **Port conflicts**: Make sure ports 50051, 8000, and 8501 are available

### Non-Docker Issues

- **Missing dependencies**: Run `pip install -r requirements.txt`
- **Protobuf errors**: Run `python compile_proto.py`
- **Background music issues**: Verify the path in `BACKGROUND_MUSIC_PATH`
- **Model loading errors**: Check that the Mistral model file exists and is accessible

### Common Errors

- **gRPC connection errors**: Ensure the gRPC server is running
- **Audio generation fails**: Check that pyttsx3 and pydub are correctly installed
- **Network timeout**: Check your internet connection when loading the UI

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Created with ❤️ for ASMR and conspiracy enthusiasts everywhere 