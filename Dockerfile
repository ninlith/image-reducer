# Set the base image.
ARG IMAGE=python:3-alpine

# ----------------------------------------------------------------------------
# Build stage.
# ----------------------------------------------------------------------------
FROM $IMAGE AS builder

# Set the working directory in the container.
WORKDIR /app

# Install PDM.
RUN pip install --no-cache-dir --disable-pip-version-check --root-user-action=ignore pdm

# Copy the source code into the container.
COPY . .

# Install the application and its dependencies into a virtual environment.
RUN pdm install --production --frozen-lockfile --no-editable --quiet

# Strip debugging symbols from pillow-avif-plugin to reduce size.
RUN apk --update add binutils
RUN strip --strip-debug .venv/lib/python*/site-packages/pillow_avif/*.so

# Activate the virtual environment in case the build is stopped at this stage (with --target).
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# ----------------------------------------------------------------------------
# Final stage.
# ----------------------------------------------------------------------------
FROM $IMAGE

# Set the working directory in the container.
WORKDIR /app

# Copy the virtual environment from the previous stage.
COPY --from=builder /app/.venv .venv

# Activate the virtual environment.
ENV VIRTUAL_ENV=/app/.venv
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

# Make port 8000 available to the world outside the container.
EXPOSE 8000

# Run the application.
CMD ["uvicorn", "image_reducer.main:app", "--host", "0.0.0.0", "--port", "8000"]
