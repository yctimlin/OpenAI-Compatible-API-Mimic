# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# Create and set the working directory
WORKDIR /app

# Copy requirements file first for better caching
COPY requirements.txt .

# Install required packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . .

# Create a non-root user to run the application
RUN adduser --disabled-password --gecos "" appuser && \
    chown -R appuser:appuser /app

# Switch to the non-root user
USER appuser

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application when the container launches
CMD ["python", "main.py"]
