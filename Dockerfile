# Use an official Python runtime as a parent image (Alpine version)
FROM python:3.12-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    build-base \
    cmake

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Final stage
FROM python:3.12-alpine

# Set the working directory in the container
WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=builder /app /app

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Expose port 8080 to the outside world
EXPOSE 8080

# Command to run your application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
