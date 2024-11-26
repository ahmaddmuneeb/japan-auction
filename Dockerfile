FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Gunicorn
RUN pip install --no-cache-dir gunicorn

# Expose the Gunicorn port
EXPOSE 8000

# Create a non-root user
RUN addgroup --system django && \
    adduser --system --ingroup django django

# Change ownership of the application directory
RUN chown -R django:django /app

# Switch to the non-root user
USER django

# Command to apply migrations and then start Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 car_scraper.wsgi:application"]