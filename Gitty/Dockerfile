FROM python:3.13.11-slim

WORKDIR /workspace

COPY . .

RUN  \
pip install --no-cache-dir -r requirements.txt && \
chmod +x /workspace/script/run.sh

CMD ["./script/run.sh"]
