# Step 1: Use an official Python image
FROM python:3.11-slim

# Step 2: Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Step 3: Set working directory
WORKDIR /app

# Step 4: Install system dependencies for mysqlclient, OpenCV, and builds
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    build-essential \
    libssl-dev \
    pkg-config \
    curl \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Step 5: Copy requirements file first (Docker cache optimization)
COPY requirements.txt /app/

# Step 6: Upgrade pip and install pre-built wheels for heavy ML packages first
RUN pip install --upgrade pip setuptools wheel

# Optional: Split installation for faster builds
RUN pip install --no-cache-dir torch==2.9.0 torchvision==0.24.0 --index-url https://download.pytorch.org/whl/cpu

# Step 7: Install remaining dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Step 8: Copy the entire Django project to /app
#COPY . /app/
COPY Django_management/ /app/

# Step 9: Collect static files
RUN python manage.py collectstatic --noinput

# Step 10: Expose port 8000
EXPOSE 8000

# Step 11: Run the Django app
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

#CMD ["gunicorn", "-c", "python:config.gunicorn", "config.wsgi"]
CMD ["gunicorn", "django_management.wsgi:application", "--bind", "0.0.0.0:80", "--workers", "3"]
