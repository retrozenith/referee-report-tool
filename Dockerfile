# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies and uWSGI
RUN apt-get update && apt-get install -y \
    uwsgi \
    uwsgi-plugin-python3 \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /webapp

# Copy the current directory contents into the container at /app
COPY ./website /webapp

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variables for Flask (optional)
#ENV FLASK_APP=app.py
#ENV FLASK_ENV=production

# Run the Flask app
#CMD ["flask", "run", "--host=0.0.0.0"]

# Run proper production environment
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "-w", "4"]