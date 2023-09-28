# Use an official Python runtime as the base image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install the required Python packages
RUN pip install -U g4f PyExecJS

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Run our Python script when the container launches
CMD ["python", "./customLLM.py"]
