import os
import sys
import subprocess

def compile_proto():
    """Compile the protobuf file into Python stubs."""
    try:
        # Check if the proto file exists
        if not os.path.exists("asmr_service.proto"):
            print("Error: asmr_service.proto not found.")
            return False

        # Compile the proto file
        print("Compiling proto file...")
        result = subprocess.run([
            "python", "-m", "grpc_tools.protoc",
            "-I.", 
            "--python_out=.", 
            "--grpc_python_out=.", 
            "asmr_service.proto"
        ], check=True)
        
        print("Proto compilation successful!")
        return True
    except subprocess.SubprocessError as e:
        print(f"Error during proto compilation: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

if __name__ == "__main__":
    compile_proto() 