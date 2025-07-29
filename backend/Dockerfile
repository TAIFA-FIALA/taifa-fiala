# Use an official Python runtime as a parent image
# Using Python 3.12 to match development environment
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app/backend

# Copy requirements file from project root
COPY ../requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir streamlit

# Copy the rest of the backend application into the container at /app/backend
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run backend.main:app when the container launches
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
