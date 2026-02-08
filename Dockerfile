FROM debian:bookworm-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    default-jdk \
    python3 \
    python3-pip \
    nodejs \
    npm && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Fix python naming
RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

# Create a non-root user
RUN useradd -m coder && \
    mkdir -p /usr/src/app && \
    chown coder:coder /usr/src/app

WORKDIR /usr/src/app

# Install python dependencies as root (system-wide)
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

# Copy application source
COPY --chown=coder:coder src/ .
COPY --chown=coder:coder migrations/ ./migrations/

USER coder

EXPOSE 3000

CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:3000", "--timeout", "60", "--access-logfile", "-", "app:app"]
