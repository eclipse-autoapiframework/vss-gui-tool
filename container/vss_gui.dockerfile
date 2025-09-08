# Use the official Ubuntu 22.04 image as the base image
FROM ubuntu:22.04
 
# Set environment variables to avoid prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
 
# Update the package list and install necessary packages
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository universe && \
    apt-get update && \
    apt-get install -y \
    python3 \
    python3-venv \
    python3-dev \
    python3-pip \
    python3-tk \
    bash && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
 
# Create a virtual environment for Python 3.10
RUN python3.10 -m venv /opt/venv
 
# Activate the virtual environment and install Python libraries
RUN /opt/venv/bin/pip install --upgrade pip
RUN /opt/venv/bin/pip install anytree pyyaml screeninfo graphql-core
 
# Set the virtual environment as the default Python environment
ENV PATH="/opt/venv/bin:$PATH"
 
# Verify the installation
RUN python --version && pip list
 
# Set the working directory
WORKDIR /app
 
# Copy the files
COPY /scripts/gui/ /app/gui
COPY /scripts/vss/ /app/vss