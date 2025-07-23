# Use an official Python runtime as a parent image
# Using Python 3.12 to match development environment and satisfy pyproject.toml requirements
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app/backend

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy poetry files
COPY pyproject.toml poetry.lock* ./

# Configure poetry: Don't create virtual env (we're already in container)
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --only=main --no-root

# Copy the rest of the backend application into the container at /app/backend
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run app.main:app when the container launches
CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
