#!/bin/bash

# The URL of your backend service
URL="http://localhost:3000/api/tools/get/1"

# In an infinite loop, send a GET request to your backend service
while true; do
  # Try to send a GET request to the backend service
  RESPONSE=$(curl --silent --write-out "HTTPSTATUS:%{http_code}" --request GET $URL)
  
  # Separate the HTTP status code
  HTTP_STATUS=$(echo $RESPONSE | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')

  # If the HTTP status code is 200, then the backend service is ready
  if [ $HTTP_STATUS -eq 200 ]; then
    echo "Backend is up"
    break
  else
    echo "Waiting for backend"
    sleep 10
  fi
done
