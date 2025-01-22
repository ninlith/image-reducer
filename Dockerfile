# Use an official Python runtime as a parent image.
FROM python:3.11-slim

# Install PDM.
RUN pip install --no-cache-dir pdm

# Set the working directory in the container.
WORKDIR /app

# Copy the files needed by PDM for dependency installation.
COPY pyproject.toml .
COPY pdm.lock .
COPY README.md .

# Install dependencies in production mode.
RUN pdm install --production --no-lock --no-editable

# Copy the rest of the application.
COPY . .

# Make port 8000 available to the world outside the container.
EXPOSE 8000

# Set environment variables to use the virtual environment.
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Run the application.
CMD ["uvicorn", "src.kollikissa.main:app", "--host", "0.0.0.0", "--port", "8000"]
