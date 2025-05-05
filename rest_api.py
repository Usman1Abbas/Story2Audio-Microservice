import os
import asyncio
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import grpc
import asmr_service_pb2
import asmr_service_pb2_grpc

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="ASMR Conspiracy Generator API",
    description="API for generating ASMR conspiracy stories and audio",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create a global gRPC channel for reuse
grpc_channel = None
grpc_stub = None

def get_grpc_stub():
    """Get or create a gRPC stub"""
    global grpc_channel, grpc_stub
    
    if grpc_stub is None:
        grpc_server = os.environ.get("GRPC_SERVER", "localhost:50051")
        grpc_channel = grpc.aio.insecure_channel(grpc_server)
        grpc_stub = asmr_service_pb2_grpc.AsmrServiceStub(grpc_channel)
    
    return grpc_stub

@app.get("/", response_class=JSONResponse)
async def root():
    """Root endpoint to check if the API is running"""
    return {"message": "ASMR Conspiracy Generator API is running."}

@app.post("/api/generate-story", response_class=JSONResponse)
async def generate_story(
    topic: str = Form(...),
    max_tokens: Optional[int] = Form(4000),
    temperature: Optional[float] = Form(0.8)
):
    """Generate a story based on the topic"""
    try:
        stub = get_grpc_stub()
        request = asmr_service_pb2.GenerateStoryRequest(
            topic=topic,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        response = await stub.GenerateStory(request)
        
        if "error" in response.status:
            raise HTTPException(status_code=500, detail=response.status)
        
        return {
            "success": True,
            "story": response.story,
            "file_path": response.file_path
        }
    except grpc.RpcError as e:
        logger.error(f"RPC Error: {e.code()}: {e.details()}")
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-audio", response_class=JSONResponse)
async def generate_audio(
    story_file: str = Form(...)
):
    """Generate audio from a story file"""
    try:
        stub = get_grpc_stub()
        request = asmr_service_pb2.GenerateAudioRequest(story_file=story_file)
        
        response = await stub.GenerateAudio(request)
        
        if "error" in response.status:
            raise HTTPException(status_code=500, detail=response.status)
        
        return {
            "success": True,
            "audio_file_path": response.audio_file_path
        }
    except grpc.RpcError as e:
        logger.error(f"RPC Error: {e.code()}: {e.details()}")
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate", response_class=JSONResponse)
async def generate_story_and_audio(
    topic: str = Form(...),
    max_tokens: Optional[int] = Form(4000),
    temperature: Optional[float] = Form(0.8)
):
    """Generate both a story and audio in one call"""
    try:
        stub = get_grpc_stub()
        request = asmr_service_pb2.GenerateStoryRequest(
            topic=topic,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        response = await stub.GenerateStoryAndAudio(request)
        
        if "error" in response.status:
            raise HTTPException(status_code=500, detail=response.status)
        
        return {
            "success": True,
            "story": response.story,
            "story_file_path": response.story_file_path,
            "audio_file_path": response.audio_file_path
        }
    except grpc.RpcError as e:
        logger.error(f"RPC Error: {e.code()}: {e.details()}")
        raise HTTPException(status_code=500, detail=f"gRPC error: {e.details()}")
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/audio/{filename}")
async def get_audio_file(filename: str):
    """Serve an audio file"""
    try:
        file_path = filename
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            media_type="audio/mpeg",
            filename=os.path.basename(file_path)
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/story/{filename}")
async def get_story_file(filename: str):
    """Serve a story file"""
    try:
        file_path = filename
        if not os.path.isabs(file_path):
            file_path = os.path.abspath(filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found")
        
        return FileResponse(
            path=file_path,
            media_type="text/plain",
            filename=os.path.basename(file_path)
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.on_event("startup")
async def startup_event():
    """Initialize gRPC stub on startup"""
    get_grpc_stub()

@app.on_event("shutdown")
async def shutdown_event():
    """Close gRPC channel on shutdown"""
    global grpc_channel
    if grpc_channel is not None:
        await grpc_channel.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("rest_api:app", host="0.0.0.0", port=8000, reload=True)