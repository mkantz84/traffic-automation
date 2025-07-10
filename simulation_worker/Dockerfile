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
        libgdal30 \
        libproj22 \
        libgl1-mesa-glx \
        libglu1-mesa \
        python3-tk \
        python3-pip \
        && rm -rf /var/lib/apt/lists/*

# Install SUMO (latest stable release)
RUN wget https://sumo.dlr.de/releases/1.18.0/sumo_1.18.0+dfsg1-1~bpo12+1_amd64.deb && \
    apt-get update && \
    apt-get install -y ./sumo_1.18.0+dfsg1-1~bpo12+1_amd64.deb && \
    rm sumo_1.18.0+dfsg1-1~bpo12+1_amd64.deb

# Set working directory
WORKDIR /app

# Copy simulation files
COPY . /app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Set entrypoint
ENTRYPOINT ["python", "entrypoint.py"] 