# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Create a non-root user for security
RUN useradd -m -r victimuser

# Set the working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY main.py .

# Switch to the non-root user
USER victimuser

# Expose the port the app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]