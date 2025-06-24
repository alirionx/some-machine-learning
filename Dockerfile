FROM python:3.13-slim

# Set workdir
WORKDIR /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements (if you have requirements.txt)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY src/ /app

# Expose the API port (set in settings.API_PORT, default 5000)
EXPOSE 5000

# Set environment variables if needed
# ENV APP_MODE=prod

# Run the FastAPI app with uvicorn
# CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "5000"]
CMD ["python", "api.py"]