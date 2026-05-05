FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Auto-install all OTel instrumentation packages
RUN opentelemetry-bootstrap --action=install

COPY . .

EXPOSE 8000
WORKDIR /src/
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
