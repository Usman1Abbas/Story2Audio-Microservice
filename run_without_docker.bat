@echo off
setlocal enabledelayedexpansion

echo ====================================
echo ASMR Conspiracy Generator Launcher
echo ====================================

:: Check if Python is installed
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in your PATH
    echo Please install Python 3.8 or higher
    goto :eof
)

:: Create virtual environment if it doesn't exist
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Failed to create virtual environment.
        goto :eof
    )
)

:: Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

:: Install dependencies if needed
if not exist "venv\Scripts\pip.exe" (
    echo Installing pip...
    python -m ensurepip
)

echo Checking/installing dependencies...
pip install -r requirements.txt

:: Compile protobuf definitions if they don't exist
if not exist "asmr_service_pb2.py" (
    echo Compiling proto files...
    python compile_proto.py
)

:: Set model path for audio file
set "BACKGROUND_MUSIC_PATH=%cd%\models\background_music\horror-background-atmosphere-11-240870.mp3"
set "MISTRAL_MODEL_PATH=%cd%\models\mistral-7b-instruct-v0.1.Q4_K_M.gguf"

:: Check if model exists
if not exist "%MISTRAL_MODEL_PATH%" (
    echo.
    echo WARNING: Mistral model file not found at %MISTRAL_MODEL_PATH%
    echo Please download the model and place it in the models directory before running the gRPC server.
    echo.
)

:: Start the services based on command-line argument
if "%1"=="" goto help
if "%1"=="grpc" goto start_grpc
if "%1"=="rest" goto start_rest
if "%1"=="ui" goto start_ui
if "%1"=="all" goto start_all
goto help

:start_grpc
echo.
echo Starting gRPC server...
start "ASMR gRPC Server" cmd /c "venv\Scripts\python.exe asmr_server.py"
echo.
echo gRPC server started on localhost:50051
echo.
goto :eof

:start_rest
echo.
echo Starting REST API (ensure gRPC server is running)...
start "ASMR REST API" cmd /c "venv\Scripts\python.exe rest_api.py"
echo.
echo REST API started on http://localhost:8000
echo.
goto :eof

:start_ui
echo.
echo Starting Streamlit UI (ensure REST API is running)...
start "ASMR Streamlit UI" cmd /c "venv\Scripts\streamlit.exe run app.py"
echo.
echo UI started - please open http://localhost:8501 in your browser
echo.
goto :eof

:start_all
echo.
echo Starting all services...
call :start_grpc
timeout /t 3 > nul
call :start_rest
timeout /t 2 > nul
call :start_ui
echo.
echo All services started!
echo.
echo - gRPC server on localhost:50051
echo - REST API on http://localhost:8000
echo - Streamlit UI on http://localhost:8501
echo.
goto :eof

:help
echo.
echo Usage: %0 [command]
echo.
echo Commands:
echo   grpc     Start the gRPC server only
echo   rest     Start the REST API (requires gRPC server)
echo   ui       Start the Streamlit UI (requires REST API)
echo   all      Start all services
echo.
echo Example: %0 all
echo.

:eof
endlocal 