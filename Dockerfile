# Use the official Python image from the Docker Hub
FROM python:3.11-slim

# Set working directory in the container
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project into the container
COPY . .

# Expose port 8000 for the FastAPI app
EXPOSE 8000

# Run the FastAPI app (this will be the default command)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
