FROM debian:bookworm-slim

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

RUN update-alternatives --install /usr/bin/python python /usr/bin/python3 1

WORKDIR /usr/src/app

COPY API/requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt --break-system-packages

COPY API/ .

EXPOSE 3000



CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:3000", "--timeout", "60", "app:app"]
