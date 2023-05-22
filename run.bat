@echo off

REM Check if config.yaml file exists
if not exist "config.yaml" (
    echo ERROR: config.yaml file not found. Please create the config.yaml file using the command 'copy config_template.yaml config.yaml' and edit it.
    exit /b 1
)

REM Install requirements
echo Installing requirements...
pip install -r requirements.txt

REM Run test.py
echo Running test.py...
python test.py