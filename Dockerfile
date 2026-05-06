FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


# Add this line to help Python find the 'src' package
ENV PYTHONPATH=/app/src

COPY . .

# Set a fallback default so the container doesn't crash if it's missing
ENV DATABASE_URL=sqlite+aiosqlite:///./test.db
ENV OTEL_PYTHON_DISTRO="aws_distro"
ENV OTEL_PYTHON_CONFIGURATOR="aws_configurator"

EXPOSE 8000
CMD ["opentelemetry-instrument", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
