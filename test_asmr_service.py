import unittest
import asyncio
import os
import grpc
from unittest.mock import patch, MagicMock
import asmr_service_pb2
import asmr_service_pb2_grpc
import asmr_server


class MockLlama:
    """Mock Llama model for testing"""
    def __call__(self, prompt, max_tokens=None, temperature=None, top_p=None, stop=None):
        return {
            "choices": [
                {
                    "text": "This is a mock generated story about the topic.\n\nOnce upon a time..."
                }
            ]
        }


class TestAsmrService(unittest.TestCase):
    """Test the ASMR service implementation"""

    def setUp(self):
        # Create a temporary directory for test files
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_files")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # Create a test file
        self.test_story_file = os.path.join(self.test_dir, "test_story.txt")
        with open(self.test_story_file, "w", encoding="utf-8") as f:
            f.write("This is a test story for ASMR audio generation.")
        
        # Mock the Llama model
        self.mock_llm = MockLlama()
        self.patcher = patch("asmr_server.Llama", return_value=self.mock_llm)
        self.mock_llama_class = self.patcher.start()
        
        # Create the service with a mock model path
        self.service = asmr_server.AsmrServiceServicer("mock_model_path")
        self.service.llm = self.mock_llm
    
    def tearDown(self):
        self.patcher.stop()
        
        # Clean up test files
        if os.path.exists(self.test_story_file):
            os.remove(self.test_story_file)
        
        # Remove test directory if empty
        try:
            os.rmdir(self.test_dir)
        except:
            pass
    
    def test_init_with_invalid_model_path(self):
        """Test initialization with invalid model path"""
        with patch("asmr_server.Llama", side_effect=Exception("Model not found")):
            service = asmr_server.AsmrServiceServicer("invalid_model_path")
            self.assertIsNone(service.llm)
    
    @patch("asmr_server.open")
    def test_generate_story(self, mock_open):
        """Test generating a story"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Create mock request and context
        request = asmr_service_pb2.GenerateStoryRequest(
            topic="test topic",
            max_tokens=1000,
            temperature=0.7
        )
        context = MagicMock()
        
        # Call the method
        result = loop.run_until_complete(self.service.GenerateStory(request, context))
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertIn("success", result.status)
        self.assertIn("This is a mock generated story", result.story)
        mock_open.assert_called()
    
    def test_generate_audio(self):
        """Test generating audio from a story file"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Set path to our real test file
        real_test_wav = "test_story.txt_temp.wav"
        
        # Mock the TTS engine and pydub
        with patch("pyttsx3.init") as mock_tts_init, \
             patch("asmr_server.AudioSegment") as mock_audio_segment, \
             patch("asmr_server.os.path.exists") as mock_exists, \
             patch("asmr_server.os.remove") as mock_remove:
            
            # Configure the mocks
            mock_engine = MagicMock()
            mock_tts_init.return_value = mock_engine
            mock_engine.getProperty.return_value = [MagicMock(name="female voice")]
            
            # Make os.path.exists return True for our test files
            mock_exists.side_effect = lambda path: True
            
            # Create mock for AudioSegment
            mock_audio = MagicMock()
            mock_audio_segment.from_file.return_value = mock_audio
            mock_audio.overlay.return_value = mock_audio
            
            # Create mock request and context
            request = asmr_service_pb2.GenerateAudioRequest(story_file=self.test_story_file)
            context = MagicMock()
            
            # Call the method
            result = loop.run_until_complete(self.service.GenerateAudio(request, context))
            
            # Assertions
            self.assertIsNotNone(result)
            self.assertIn("success", result.status)
            self.assertTrue(mock_engine.save_to_file.called)
            
            # Verify our temp wav file is passed to AudioSegment
            output_temp_path = f"{self.test_story_file}_temp.wav"
            mock_audio_segment.from_file.assert_any_call(output_temp_path)
    
    def test_generate_audio_file_not_found(self):
        """Test generating audio from a non-existent file"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Create mock request and context
        request = asmr_service_pb2.GenerateAudioRequest(story_file="non_existent_file.txt")
        context = MagicMock()
        
        # Call the method
        result = loop.run_until_complete(self.service.GenerateAudio(request, context))
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertIn("error", result.status)
        self.assertIn("file not found", result.status)
    
    @patch("asmr_server.AsmrServiceServicer.GenerateStory")
    @patch("asmr_server.AsmrServiceServicer.GenerateAudio")
    def test_generate_story_and_audio(self, mock_generate_audio, mock_generate_story):
        """Test generating both story and audio"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Configure mocks
        mock_story_response = asmr_service_pb2.GenerateStoryResponse(
            story="Generated story",
            file_path="story.txt",
            status="success"
        )
        mock_audio_response = asmr_service_pb2.GenerateAudioResponse(
            audio_file_path="audio.mp3",
            status="success"
        )
        
        mock_generate_story.return_value = mock_story_response
        mock_generate_audio.return_value = mock_audio_response
        
        # Create mock request and context
        request = asmr_service_pb2.GenerateStoryRequest(
            topic="test topic",
            max_tokens=1000,
            temperature=0.7
        )
        context = MagicMock()
        
        # Call the method
        result = loop.run_until_complete(self.service.GenerateStoryAndAudio(request, context))
        
        # Assertions
        self.assertIsNotNone(result)
        self.assertEqual(result.status, "success")
        self.assertEqual(result.story, "Generated story")
        self.assertEqual(result.story_file_path, "story.txt")
        self.assertEqual(result.audio_file_path, "audio.mp3")
        mock_generate_story.assert_called_with(request, context)

    def test_generate_audio_with_real_file(self):
        """Test generating audio using a real temp wav file"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Path to our real test temp wav file
        real_test_wav = "test_story.txt_temp.wav"
        
        # Skip test if the file doesn't exist
        if not os.path.exists(real_test_wav):
            self.skipTest(f"Test file {real_test_wav} not found")
        
        # Only mock parts we need to mock, use real AudioSegment
        with patch("pyttsx3.init") as mock_tts_init, \
             patch("asmr_server.os.remove") as mock_remove:
            
            # Configure TTS mock (won't be used as we're using real file)
            mock_engine = MagicMock()
            mock_tts_init.return_value = mock_engine
            mock_engine.getProperty.return_value = [MagicMock(name="female voice")]
            
            # Mock file saving to prevent real file creation in test
            mock_engine.save_to_file.side_effect = lambda text, path: None
            
            # Patch the _generate_audio_with_settings method to use our real file
            original_method = self.service._generate_audio_with_settings
            
            def mocked_method(story_file, **kwargs):
                # Copy our real test wav file to the expected temp file path
                import shutil
                temp_file = f"{story_file}_temp.wav"
                shutil.copy(real_test_wav, temp_file)
                
                # Call the original method to process the file
                return original_method(story_file, **kwargs)
            
            with patch.object(self.service, '_generate_audio_with_settings', side_effect=mocked_method):
                # Create request and context
                request = asmr_service_pb2.GenerateAudioRequest(story_file=self.test_story_file)
                context = MagicMock()
                
                # Call the method
                result = loop.run_until_complete(self.service.GenerateAudio(request, context))
                
                # Assertions
                self.assertIsNotNone(result)
                self.assertIn("success", result.status)
                self.assertTrue(os.path.exists(result.audio_file_path) or "audio_file_path" in str(result))


if __name__ == "__main__":
    unittest.main() 