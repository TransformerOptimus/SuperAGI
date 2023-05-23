@echo off
echo Checking if config.yaml file exists...
if not exist config.yaml (
    echo ERROR: config.yaml file not found. Please create the config.yaml file.
    exit /b 1
)
echo Checking if virtual environment is activated...
if not defined VIRTUAL_ENV (
    echo Virtual environment not activated. Creating and activating virtual environment...
    python3 -m venv venv
    if errorlevel 1 (
      echo Error: Failed to create virtual environment.
      exit /b 1
    )
    call venv\Scripts\activate.bat
) else (
    echo Virtual environment is already activated.
)
echo Checking requirements...
pip show -r requirements.txt >nul 2>&1
if errorlevel 1 (
    echo Installing requirements...
    pip install -r requirements.txt >nul 2>&1
) else (
    echo All packages are already installed.
)
echo Running test.py with python...
python test.py
if errorlevel 1 (
    echo Running test.py with python3...
    python3 test.py
)