# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install PDM
RUN pip install --no-cache-dir pdm

# Set the working directory in the container
WORKDIR /app

# Copy the PDM files
COPY pyproject.toml .
COPY pdm.lock .
# COPY pyproject.toml pdm.lock ./

# Install dependencies using PDM
#RUN pdm install --prod --no-lock
RUN pdm install --production --no-lock --no-editable

# Copy the rest of the application code
COPY . .

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the application
CMD ["pdm", "run", "uvicorn", "src.kollikissa.main:app", "--host", "0.0.0.0", "--port", "8000"]