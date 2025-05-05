import grpc
import asyncio
import logging
import time
import concurrent.futures
import os
import sys
from concurrent import futures

# Add the current directory to the path to ensure modules are found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asmr_service_pb2
import asmr_service_pb2_grpc
from llama_cpp import Llama
import pyttsx3
from pydub import AudioSegment

# Configure logging with increased level
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AsmrServiceServicer(asmr_service_pb2_grpc.AsmrServiceServicer):
    def __init__(self, model_path):
        self.model_path = model_path
        self.llm = None
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
        
        # Initialize the LLM (could be lazy loaded)
        try:
            self.llm = Llama(model_path=model_path, n_ctx=4096)
            logger.info("LLM model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading LLM model: {e}")
            # Will attempt to load on first request
    
    def _ensure_model_loaded(self):
        """Ensure the model is loaded"""
        if self.llm is None:
            try:
                self.llm = Llama(model_path=self.model_path, n_ctx=4096)
                logger.info("LLM model loaded successfully")
            except Exception as e:
                logger.error(f"Error loading LLM model: {e}")
                raise RuntimeError(f"Failed to load LLM model: {e}")
    
    def _generate_story(self, topic, max_tokens=4000, temperature=0.8):
        """Generate a story based on the topic"""
        self._ensure_model_loaded()
        
        # Build the prompt
        prompt = f"""
Write a fictional story that explores a long-buried conspiracy surrounding {topic}.

The narrative should feel atmospheric and immersive, gradually uncovering chilling secrets hidden from the public eye. Use vivid sensory descriptions to evoke a sense of mystery and unease—abandoned corridors, flickering lights, classified documents, and forgotten witnesses.

Incorporate elements like:

Hidden files and cryptic notes
Shadowy figures or secret organizations
Anonymous sources or whistleblowers
Suppressed evidence or erased records
Strange sounds, encrypted messages, or unexplainable events

Structure the story to build suspense, with each reveal deepening the reader's sense that something vast and sinister lies just beneath the surface.

End with a haunting twist or unresolved question that leaves the reader wondering what's real… and what's been kept from them.
"""

        try:
            output = self.llm(
                prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95,
                stop=None
            )
            generated_script = output["choices"][0]["text"].strip()

            # Save to a .txt file
            filename = f"asmr_conspiracy_{topic.replace(' ', '_').lower()}.txt"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(generated_script)
            
            return generated_script, filename
        except Exception as e:
            logger.error(f"Error generating story: {e}")
            raise RuntimeError(f"Failed to generate story: {e}")
    
    def _adjust_voice_properties(self, text):
        """Determine voice features based on the text content"""
        # Default ASMR settings
        voice_properties = {'rate': 130, 'volume': 0.65, 'pitch': 1.0}  # Faster ASMR tempo and intimate volume
        
        # Keywords and their corresponding voice adjustments
        adjustments = {
            "exciting": {'rate': 140, 'volume': 0.7, 'pitch': 1.05},  # More subdued for ASMR but faster
            "sad": {'rate': 120, 'volume': 0.6, 'pitch': 0.9},  # Slow, softer, lower pitch
            "mysterious": {'rate': 125, 'volume': 0.65, 'pitch': 0.95},  # Moderate, slightly low pitch
            "dramatic": {'rate': 115, 'volume': 0.7, 'pitch': 0.9},  # Slower, moderate, low pitch
            "calm": {'rate': 130, 'volume': 0.6, 'pitch': 1.0},  # Standard ASMR tempo, soft, neutral pitch
        }

        # Check for mood-indicating words in the text
        for mood, properties in adjustments.items():
            if mood in text.lower():
                voice_properties = properties
                break

        return voice_properties

    def _generate_audio(self, story_file):
        """Generate audio from a story file"""
        try:
            logger.info(f"Starting audio generation for {story_file}")
            logger.info(f"File exists: {os.path.exists(story_file)}")
            
            # Read the content of the story file
            with open(story_file, "r", encoding="utf-8") as f:
                story_text = f.read()
            logger.info(f"Successfully read file content: {len(story_text)} characters")
            
            # Initialize the TTS engine
            logger.info("Initializing TTS engine")
            engine = pyttsx3.init()
            logger.info("TTS engine initialized successfully")
            
            # Adjust voice properties for ASMR
            voice_properties = self._adjust_voice_properties(story_text)
            logger.info(f"ASMR voice properties adjusted: {voice_properties}")
            engine.setProperty('rate', voice_properties['rate'])      # ASMR tempo (updated to 130)
            engine.setProperty('volume', voice_properties['volume'])  # Intimate volume level
            engine.setProperty('pitch', voice_properties['pitch'])    # Pitch adjustment
            
            # Display available voices
            voices = engine.getProperty('voices')
            logger.info(f"Available voices for ASMR: {len(voices)}")
            
            # Voice selection logic
            for i, voice in enumerate(voices):
                logger.info(f"{i}: {voice.name} - {voice.id}")
            
            # Track female voices
            female_voices = []
            for i, voice in enumerate(voices):
                if 'female' in voice.name.lower() or any(name in voice.name.lower() for name in ['zira', 'microsoft eva', 'microsoft hazel', 'microsoft heera']):
                    female_voices.append((i, voice))
            
            # Prioritize female voices
            if female_voices:
                # Use the first female voice found
                index, voice = female_voices[0]
                engine.setProperty('voice', voice.id)
                logger.info(f"Selected female voice: {voice.name}")
                voice_found = True
            else:
                # Select voice - try to find a good ASMR voice
                voice_found = False
                for voice in voices:
                    voice_name = voice.name.lower()
                    # Prioritize softer voices for ASMR
                    if any(keyword in voice_name for keyword in ['soft', 'calm']):
                        engine.setProperty('voice', voice.id)
                        voice_found = True
                        logger.info(f"Selected ASMR-appropriate voice: {voice.name}")
                        break
                    
            if not voice_found:
                logger.info("No ideal ASMR voice found, using default voice")
            
            # Save the speech to a temporary audio file
            output_audio_path = f"{story_file}_temp.wav"
            logger.info(f"Saving ASMR speech to temporary file: {output_audio_path}")
            engine.save_to_file(story_text, output_audio_path)
            engine.runAndWait()
            logger.info("ASMR TTS engine completed processing")
            
            # Check if temp file was created
            logger.info(f"Temp file exists after TTS: {os.path.exists(output_audio_path)}")
            
            # Process with background music if possible
            try:
                # Load narration
                logger.info(f"Loading ASMR narration from {output_audio_path}")
                narration = AudioSegment.from_file(output_audio_path)
                logger.info(f"ASMR narration loaded successfully: {len(narration)}ms")
                
                # Try to use background music if available
                # Get music path from environment or use default
                default_music = os.environ.get(
                    "BACKGROUND_MUSIC_PATH", 
                    os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                "models", "background_music", 
                                "horror-background-atmosphere-11-240870.mp3")
                )
                logger.info(f"Attempting to use background music from: {default_music}")
                if os.path.exists(default_music):
                    try:
                        logger.info("Adding background music to ASMR narration")
                        background_music = AudioSegment.from_file(default_music)
                        
                        # Adjust music for ASMR (lower volume)
                        background_music = background_music - 12  # Reduced volume to achieve ~0.30 level
                        
                        if len(background_music) < len(narration):
                            background_music *= (len(narration) // len(background_music)) + 1
                        background_music = background_music[:len(narration)]
                        
                        # Overlay narration on background
                        final_audio = background_music.overlay(narration)
                        logger.info("ASMR audio with background music created successfully")
                    except Exception as e:
                        logger.error(f"Error adding background music: {e}")
                        final_audio = narration
                else:
                    logger.info("Background music file not found, using narration only")
                    final_audio = narration
                
                # Export final audio with explicit parameters
                output_mp3 = f"{os.path.splitext(story_file)[0]}_asmr.mp3"
                logger.info(f"Exporting final ASMR audio to: {output_mp3}")
                final_audio.export(
                    output_mp3,
                    format="mp3",
                    bitrate="192k",
                    parameters=["-ac", "2", "-ar", "44100"]
                )
                logger.info("ASMR audio export completed")
                
                # Cleanup
                logger.info(f"Removing temporary file: {output_audio_path}")
                os.remove(output_audio_path)
                
                return output_mp3
            except Exception as e:
                logger.error(f"Error in ASMR audio conversion: {e}", exc_info=True)
                raise RuntimeError(f"Failed to convert ASMR audio: {e}")
                
        except Exception as e:
            logger.error(f"Error generating ASMR audio: {e}", exc_info=True)
            raise RuntimeError(f"Failed to generate ASMR audio: {e}")
    
    async def GenerateStory(self, request, context):
        """Generate a story based on the topic"""
        try:
            logger.info(f"Generating story for topic: {request.topic}")
            
            # Extract parameters with defaults
            max_tokens = request.max_tokens if request.HasField("max_tokens") else 4000
            temperature = request.temperature if request.HasField("temperature") else 0.8
            
            # Run in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            story, file_path = await loop.run_in_executor(
                self.executor,
                lambda: self._generate_story(request.topic, max_tokens, temperature)
            )
            
            return asmr_service_pb2.GenerateStoryResponse(
                story=story, 
                file_path=file_path, 
                status="success"
            )
        except Exception as e:
            logger.error(f"Error in GenerateStory: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return asmr_service_pb2.GenerateStoryResponse(status=f"error: {e}")
    
    async def GenerateAudio(self, request, context):
        """Generate audio from a story file"""
        try:
            logger.info(f"Generating audio for file: {request.story_file}")
            
            # Check if file exists
            if not os.path.exists(request.story_file):
                logger.error(f"File not found: {request.story_file}")
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details(f"File {request.story_file} not found")
                return asmr_service_pb2.GenerateAudioResponse(
                    status=f"error: file not found"
                )
            
            # Extract ASMR voice settings if provided
            voice_settings = None
            use_background_music = True  # Default to true
            voice_index = -1  # Default to auto-select
            
            if request.HasField("voice_settings"):
                voice_settings = request.voice_settings
                logger.info(f"Using custom voice settings: {voice_settings}")
            
            if request.HasField("use_background_music"):
                use_background_music = request.use_background_music
                logger.info(f"Background music setting: {use_background_music}")
                
            if request.HasField("voice_index"):
                voice_index = request.voice_index
                logger.info(f"Using voice index: {voice_index}")
            
            # Run audio generation with the specified settings
            audio_file = self._generate_audio_with_settings(
                request.story_file, 
                voice_settings=voice_settings,
                use_background_music=use_background_music,
                voice_index=voice_index
            )
            logger.info(f"ASMR audio generation completed, file at: {audio_file}")
            
            # Prepare response with the used voice settings
            response = asmr_service_pb2.GenerateAudioResponse(
                audio_file_path=audio_file, 
                status="success"
            )
            
            return response
        except Exception as e:
            logger.error(f"Error in GenerateAudio: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return asmr_service_pb2.GenerateAudioResponse(status=f"error: {e}")
            
    def _generate_audio_with_settings(self, story_file, voice_settings=None, use_background_music=True, voice_index=-1):
        """Generate audio from a story file with the specified settings"""
        try:
            logger.info(f"Starting ASMR audio generation for {story_file}")
            logger.info(f"File exists: {os.path.exists(story_file)}")
            
            # Read the content of the story file
            with open(story_file, "r", encoding="utf-8") as f:
                story_text = f.read()
            logger.info(f"Successfully read file content: {len(story_text)} characters")
            
            # Initialize the TTS engine
            logger.info("Initializing TTS engine")
            engine = pyttsx3.init()
            logger.info("TTS engine initialized successfully")
            
            # Get voice properties
            if voice_settings:
                # Use provided settings
                props = {}
                if voice_settings.HasField("rate"):
                    props['rate'] = voice_settings.rate
                if voice_settings.HasField("volume"):
                    props['volume'] = voice_settings.volume
                if voice_settings.HasField("pitch"):
                    props['pitch'] = voice_settings.pitch
                    
                # Fill in any missing settings with ASMR defaults
                if 'rate' not in props:
                    props['rate'] = 130  # Updated ASMR default speed
                if 'volume' not in props:
                    props['volume'] = 0.65  # ASMR default
                if 'pitch' not in props:
                    props['pitch'] = 1.0  # ASMR default
            else:
                # Use auto-detected settings based on content
                props = self._adjust_voice_properties(story_text)
                
            logger.info(f"ASMR voice properties set: {props}")
            engine.setProperty('rate', props['rate'])
            engine.setProperty('volume', props['volume'])
            if 'pitch' in props:
                engine.setProperty('pitch', props['pitch'])
            
            # Voice selection
            voices = engine.getProperty('voices')
            logger.info(f"Available voices for ASMR: {len(voices)}")
            
            # Log available voices
            female_voices = []
            for i, voice in enumerate(voices):
                logger.info(f"{i}: {voice.name} - {voice.id}")
                # Track any female voices for prioritization
                if 'female' in voice.name.lower() or any(name in voice.name.lower() for name in ['zira', 'microsoft eva', 'microsoft hazel', 'microsoft heera']):
                    female_voices.append((i, voice))
            
            # Set voice based on index or auto-select
            if 0 <= voice_index < len(voices):
                # Use specified voice index
                engine.setProperty('voice', voices[voice_index].id)
                logger.info(f"Using specified voice: {voices[voice_index].name}")
            else:
                # Prioritize female voices
                if female_voices:
                    # Use the first female voice found
                    index, voice = female_voices[0]
                    engine.setProperty('voice', voice.id)
                    logger.info(f"Selected female voice: {voice.name}")
                else:
                    # Auto-select voice based on ASMR preferences if no female voices found
                    voice_found = False
                    for voice in voices:
                        voice_name = voice.name.lower()
                        # Prioritize softer voices for ASMR
                        if any(keyword in voice_name for keyword in ['soft', 'calm']):
                            engine.setProperty('voice', voice.id)
                            voice_found = True
                            logger.info(f"Selected ASMR-appropriate voice: {voice.name}")
                            break
                            
                    if not voice_found:
                        logger.info("No ideal ASMR voice found, using default voice")
            
            # Save the speech to a temporary audio file
            output_audio_path = f"{story_file}_temp.wav"
            logger.info(f"Saving ASMR speech to temporary file: {output_audio_path}")
            engine.save_to_file(story_text, output_audio_path)
            engine.runAndWait()
            logger.info("ASMR TTS engine completed processing")
            
            # Check if temp file was created
            logger.info(f"Temp file exists after TTS: {os.path.exists(output_audio_path)}")
            
            # Process with background music if requested
            try:
                # Load narration
                logger.info(f"Loading ASMR narration from {output_audio_path}")
                narration = AudioSegment.from_file(output_audio_path)
                logger.info(f"ASMR narration loaded successfully: {len(narration)}ms")
                
                final_audio = narration
                
                # Add background music if requested
                if use_background_music:
                    # Get music path from environment or use default
                    default_music = os.environ.get(
                        "BACKGROUND_MUSIC_PATH", 
                        os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                                    "models", "background_music", 
                                    "horror-background-atmosphere-11-240870.mp3")
                    )
                    logger.info(f"Attempting to use background music from: {default_music}")
                    if os.path.exists(default_music):
                        try:
                            logger.info("Adding background music to ASMR narration")
                            background_music = AudioSegment.from_file(default_music)
                            
                            # Adjust music for ASMR (lower volume)
                            background_music = background_music - 5 # Reduced volume to achieve ~0.30 level
                            
                            if len(background_music) < len(narration):
                                background_music *= (len(narration) // len(background_music)) + 1
                            background_music = background_music[:len(narration)]
                            
                            # Overlay narration on background
                            final_audio = background_music.overlay(narration)
                            logger.info("ASMR audio with background music created successfully")
                        except Exception as e:
                            logger.error(f"Error adding background music: {e}")
                    else:
                        logger.info("Background music file not found, using narration only")
                else:
                    logger.info("Background music disabled, using narration only")
                
                # Export final audio with explicit parameters
                output_mp3 = f"{os.path.splitext(story_file)[0]}_asmr.mp3"
                logger.info(f"Exporting final ASMR audio to: {output_mp3}")
                final_audio.export(
                    output_mp3,
                    format="mp3",
                    bitrate="192k",
                    parameters=["-ac", "2", "-ar", "44100"]
                )
                logger.info("ASMR audio export completed")
                
                # Cleanup
                logger.info(f"Removing temporary file: {output_audio_path}")
                os.remove(output_audio_path)
                
                return output_mp3
            except Exception as e:
                logger.error(f"Error in ASMR audio conversion: {e}", exc_info=True)
                raise RuntimeError(f"Failed to convert ASMR audio: {e}")
                
        except Exception as e:
            logger.error(f"Error generating ASMR audio: {e}", exc_info=True)
            raise RuntimeError(f"Failed to generate ASMR audio: {e}")
    
    async def GenerateStoryAndAudio(self, request, context):
        """Generate both a story and audio in one call"""
        try:
            logger.info(f"Generating ASMR story and audio for topic: {request.topic}")
            
            # First generate the story
            story_response = await self.GenerateStory(request, context)
            if "error" in story_response.status:
                return asmr_service_pb2.GenerateStoryAndAudioResponse(
                    status=story_response.status
                )
            
            # Create audio request with ASMR voice settings
            audio_request = asmr_service_pb2.GenerateAudioRequest(story_file=story_response.file_path)
            
            # Create default ASMR voice settings with increased rate
            voice_settings = asmr_service_pb2.VoiceSettings(
                rate=130,
                volume=0.65,
                pitch=1.0
            )
            audio_request.voice_settings.CopyFrom(voice_settings)
            audio_request.use_background_music = True
            
            # Generate the audio with ASMR settings
            audio_response = await self.GenerateAudio(audio_request, context)
            if "error" in audio_response.status:
                return asmr_service_pb2.GenerateStoryAndAudioResponse(
                    story=story_response.story,
                    story_file_path=story_response.file_path,
                    status=f"story generated, but audio failed: {audio_response.status}"
                )
            
            # Create response with the voice settings used
            response = asmr_service_pb2.GenerateStoryAndAudioResponse(
                story=story_response.story,
                story_file_path=story_response.file_path,
                audio_file_path=audio_response.audio_file_path,
                status="success"
            )
            response.used_voice_settings.CopyFrom(voice_settings)
            
            return response
        except Exception as e:
            logger.error(f"Error in GenerateStoryAndAudio: {e}", exc_info=True)
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return asmr_service_pb2.GenerateStoryAndAudioResponse(status=f"error: {e}")


async def serve():
    # Get model path from environment variable or use default
    model_path = os.environ.get(
        "MISTRAL_MODEL_PATH", 
        os.path.join(os.path.dirname(os.path.abspath(__file__)), 
                    "models", "mistral-7b-instruct-v0.1.Q4_K_M.gguf")
    )
    logger.info(f"Loading Mistral model from: {model_path}")
    
    # Create gRPC server
    server = grpc.aio.server(
        futures.ThreadPoolExecutor(max_workers=10),
        options=[
            ('grpc.max_send_message_length', 50 * 1024 * 1024),  # 50 MiB
            ('grpc.max_receive_message_length', 50 * 1024 * 1024),  # 50 MiB
        ]
    )
    
    # Add the servicer to the server
    asmr_service_pb2_grpc.add_AsmrServiceServicer_to_server(
        AsmrServiceServicer(model_path), server
    )
    
    # Add port
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    
    # Start server
    logger.info(f"Starting gRPC server on {listen_addr}")
    await server.start()
    
    try:
        await server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Server stopping...")
        await server.stop(0)


if __name__ == "__main__":
    asyncio.run(serve()) 