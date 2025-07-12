# Use official Python image
FROM python:3.10-slim

# Install system dependencies for SUMO
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    wget \
    ca-certificates \
    libxml2 \
    libxerces-c3.2 \
    libfox-1.6-0 \
    libgl1-mesa-glx \
    libglu1-mesa \
    python3-tk \
    python3-pip \
    sumo \
    sumo-tools \
    sumo-doc \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy simulation files
COPY . /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Set entrypoint
ENV SUMO_HOME=/usr/share/sumo
ENV PYTHONPATH=$PYTHONPATH:/usr/share/sumo/tools
ENTRYPOINT ["python", "entrypoint.py"] 