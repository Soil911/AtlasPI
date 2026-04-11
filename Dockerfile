FROM python:3.13-slim AS builder

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13-slim

WORKDIR /app
COPY --from=builder /install /usr/local
COPY src/ src/
COPY static/ static/
COPY data/ data/
COPY run.py .

ENV HOST=0.0.0.0
ENV PORT=10100
ENV RELOAD=false
ENV LOG_FORMAT=json
ENV AUTO_SEED=true

EXPOSE 10100

CMD ["python", "run.py"]
