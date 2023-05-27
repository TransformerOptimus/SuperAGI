@echo off
echo Checking if config.yaml file exists...
if not exist config.yaml (
    echo ERROR: config.yaml file not found. Please create the config.yaml file.
    exit /b 1
)
echo Checking if virtual environment is activated...
if not defined VIRTUAL_ENV (
    echo Virtual environment not activated. Creating and activating virtual environment...
    python -m venv venv
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
@REM echo Running test.py with python...
@REM python test.py
@REM if errorlevel 1 (
@REM     echo Running test.py with python3...
@REM     python3 test.py
@REM )

echo Running %1...

if "%1" == "ui" (
    python ui.py
    if errorlevel 1 (
    python3 ui.py
    )
)

if "%1" == "cli" (
    python cli2.py
    if errorlevel 1 (
    python3 cli2.py
    )
)