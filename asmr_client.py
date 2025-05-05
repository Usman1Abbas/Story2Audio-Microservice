import grpc
import asyncio
import os
import argparse
import asmr_service_pb2
import asmr_service_pb2_grpc


async def generate_story(stub, topic, max_tokens=4000, temperature=0.8):
    """Generate a story based on the topic"""
    request = asmr_service_pb2.GenerateStoryRequest(
        topic=topic,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    try:
        response = await stub.GenerateStory(request)
        if "error" in response.status:
            print(f"Error: {response.status}")
            return None
        
        print(f"Story generated successfully at: {response.file_path}")
        return response
    except grpc.RpcError as e:
        print(f"RPC Error: {e.code()}: {e.details()}")
        return None


async def generate_audio(stub, story_file):
    """Generate audio from a story file"""
    request = asmr_service_pb2.GenerateAudioRequest(story_file=story_file)
    
    try:
        response = await stub.GenerateAudio(request)
        if "error" in response.status:
            print(f"Error: {response.status}")
            return None
        
        print(f"Audio generated successfully at: {response.audio_file_path}")
        return response
    except grpc.RpcError as e:
        print(f"RPC Error: {e.code()}: {e.details()}")
        return None


async def generate_story_and_audio(stub, topic, max_tokens=4000, temperature=0.8):
    """Generate both a story and audio in one call"""
    request = asmr_service_pb2.GenerateStoryRequest(
        topic=topic,
        max_tokens=max_tokens,
        temperature=temperature
    )
    
    try:
        response = await stub.GenerateStoryAndAudio(request)
        if "error" in response.status:
            print(f"Error: {response.status}")
            return None
        
        print(f"Story and audio generated successfully:")
        print(f"Story file: {response.story_file_path}")
        print(f"Audio file: {response.audio_file_path}")
        return response
    except grpc.RpcError as e:
        print(f"RPC Error: {e.code()}: {e.details()}")
        return None


async def main():
    parser = argparse.ArgumentParser(description="ASMR Conspiracy gRPC Client")
    parser.add_argument("--action", type=str, choices=["story", "audio", "both"], default="both",
                        help="Action to perform (story, audio, or both)")
    parser.add_argument("--topic", type=str, default="alien abductions",
                        help="The topic for the conspiracy story")
    parser.add_argument("--story-file", type=str,
                        help="Path to the story file for audio generation")
    parser.add_argument("--max-tokens", type=int, default=4000,
                        help="Maximum tokens for story generation")
    parser.add_argument("--temperature", type=float, default=0.8,
                        help="Temperature for story generation")
    parser.add_argument("--server", type=str, default="localhost:50051",
                        help="Server address in the format host:port")
    
    args = parser.parse_args()
    
    # Create channel and stub
    async with grpc.aio.insecure_channel(args.server) as channel:
        stub = asmr_service_pb2_grpc.AsmrServiceStub(channel)
        
        if args.action == "story":
            await generate_story(stub, args.topic, args.max_tokens, args.temperature)
        elif args.action == "audio":
            if not args.story_file:
                print("Error: --story-file is required for audio generation")
                return
            await generate_audio(stub, args.story_file)
        elif args.action == "both":
            await generate_story_and_audio(stub, args.topic, args.max_tokens, args.temperature)


if __name__ == "__main__":
    asyncio.run(main()) 