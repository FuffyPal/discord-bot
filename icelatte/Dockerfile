FROM docker.io/library/python:3.14.4-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends iputils-ping curl && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN \
mkdir -p /app/bin/ && \
curl https://gitlab.com/FluffyPal/vpet_main/-/package_files/314633939/download --output /app/bin/pet && \
chmod +x /app/bin/pet

CMD ["python", "main.py"]
