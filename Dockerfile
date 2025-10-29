FROM python:3.14.0-slim

WORKDIR /app
COPY requirements.txt .
RUN apt-get update && apt-get install -y --no-install-recommends     unzip curl && rm -rf /var/lib/apt/lists/* &&     pip install --no-cache-dir -r requirements.txt
COPY ./app ./app
ENV PYTHONPATH=/app
EXPOSE 3000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
