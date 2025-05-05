FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libespeak-dev \
    build-essential \
    cmake \
    libsndfile1 \
    gcc \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Compile proto files
RUN python compile_proto.py

# Create directories for models and generated content
RUN mkdir -p /app/models /app/generated

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    MISTRAL_MODEL_PATH=/app/models/mistral-7b-instruct-v0.1.Q4_K_M.gguf \
    GRPC_SERVER=0.0.0.0:50051

# Expose ports
EXPOSE 50051 8000 8501

# Create an entrypoint script
RUN echo '#!/bin/bash\n\
if [ "$1" = "grpc" ]; then\n\
    exec python asmr_server.py\n\
elif [ "$1" = "rest" ]; then\n\
    exec python rest_api.py\n\
elif [ "$1" = "ui" ]; then\n\
    exec streamlit run app.py\n\
else\n\
    exec "$@"\n\
fi' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["grpc"] 