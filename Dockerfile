# Build stage.
FROM python:3.11-slim as builder

# Set the working directory in the container.
WORKDIR /app

# Install PDM.
RUN pip install --no-cache-dir --disable-pip-version-check --root-user-action=ignore pdm

# Copy the files needed by PDM for dependency installation.
COPY pyproject.toml .
COPY pdm.lock .
COPY README.md .

# Install dependencies in production mode.
# RUN pdm install --production --frozen-lockfile --no-editable --quiet

# Build the application.
RUN pdm build --no-sdist --quiet

# Copy the rest of the application.
COPY . .

# Final stage.
FROM python:3.11-alpine

# Set the working directory in the container.
WORKDIR /app

# Copy the application from the previous stage.
COPY --from=builder /app/dist dist
COPY --from=builder /app/src src

# Install dependencies.
RUN pip install --no-cache --disable-pip-version-check --root-user-action=ignore dist/*.whl

# Uninstall unneeded packages.
RUN pip uninstall --yes --root-user-action=ignore pip setuptools wheel

# Make port 8000 available to the world outside the container.
EXPOSE 8000

# Set environment variables to use the virtual environment.
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Run the application.
CMD ["uvicorn", "src.kollikissa.main:app", "--host", "0.0.0.0", "--port", "8000"]
