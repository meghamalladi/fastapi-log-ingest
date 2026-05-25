#Base image
FROM python:3.11-slim

# Setting the working directory
WORKDIR ./app

# Prevent python from writing .pyc files and enable unbuffered logging
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy fastapi files etc to working directory
COPY /app /app

# Purely descriptive: listen to the requests on port 8000
EXPOSE 8000


CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]