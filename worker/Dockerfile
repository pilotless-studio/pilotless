FROM google/cloud-sdk:slim
RUN apt-get update && apt-get install -y --no-install-recommends python3-pip git curl ca-certificates && rm -rf /var/lib/apt/lists/*
RUN pip3 install --break-system-packages --no-cache-dir google-cloud-firestore requests || pip3 install --no-cache-dir google-cloud-firestore requests
WORKDIR /workspace
COPY main.py /app/main.py
CMD ["python3", "/app/main.py"]
