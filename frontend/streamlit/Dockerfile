# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
# Install streamlit and common dependencies
RUN pip install --no-cache-dir \
    streamlit \
    pandas \
    numpy \
    plotly \
    requests \
    python-dotenv

# Make port 8501 available to the world outside this container
EXPOSE 8501

# Define environment variable
ENV PYTHONPATH=/app

# Run streamlit when the container launches
CMD ["streamlit", "run", "run_dashboard.py", "--server.port=8501", "--server.address=0.0.0.0"]