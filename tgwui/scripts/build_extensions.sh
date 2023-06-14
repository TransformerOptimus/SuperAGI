#!/bin/bash

# Specify the directory containing the top-level folders
directory="/app/extensions"

# Iterate over the top-level folders
for folder in "$directory"/*; do
    if [ -d "$folder" ]; then
        # Change directory to the current folder
        cd "$folder"

        # Check if requirements.txt file exists
        if [ -f "requirements.txt" ]; then
            echo "Installing requirements in $folder..."
            pip3 install -r requirements.txt
            echo "Requirements installed in $folder"
        else
            echo "Skipping $folder: requirements.txt not found"
        fi

        # Change back to the original directory
        cd "$directory"
    fi
done

