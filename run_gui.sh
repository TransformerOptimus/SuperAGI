#!/bin/bash

api_process=""
ui_process=""

function check_command() {
  command -v "$1" >/dev/null 2>&1
  if [ $? -ne 0 ]; then
    echo "$1 is not installed. Please install $1 to proceed."
    exit 1
  fi
}

function run_npm_commands() {
  cd gui
  npm install
  if [ $? -ne 0 ]; then
    echo "Error during 'npm install'. Exiting."
    exit 1
  fi

  npm run build
  if [ $? -ne 0 ]; then
    echo "Error during 'npm run build'. Exiting."
    exit 1
  fi

  cd ..
}

function run_server() {
  uvicorn main:app --host 0.0.0.0 --port 8000 &
  api_process=$!
  cd gui && npm run dev &
  ui_process=$!
}

function cleanup() {
  echo "Shutting down processes..."
  kill $api_process
  kill $ui_process
  echo "Processes terminated. Exiting."
  exit 1
}

trap cleanup SIGINT

check_command "node"
check_command "npm"
check_command "uvicorn"

run_npm_commands
run_server

wait $api_process