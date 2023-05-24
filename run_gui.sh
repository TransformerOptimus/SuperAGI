#!/bin/bash
cd gui

command -v node >/dev/null 2>&1
if [ $? -eq 0 ]; then
  echo "Node.js is installed. Proceeding with npm commands..."

  # Run npm install, build, and start
  cd gui
  npm install
  if [ $? -ne 0 ]; then
    echo "Error during 'npm install'. Exiting."
    # exit 1
  fi

  npm run build
  if [ $? -ne 0 ]; then
    echo "Error during 'npm build'. Exiting."
    # exit 1
  fi
else
  echo "Node.js is not installed. Please install Node.js to proceed."
fi

cd ..

cd . && uvicorn main:app --host 0.0.0.0 --port 8000 &
cd gui && npm run dev
