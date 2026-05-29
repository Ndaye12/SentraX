FROM python:3.11-slim

LABEL maintainer="Patrick Ndaye <patrickndaye919@gmail.com>"
LABEL description="SENTRAX - Suite de cybersecurite professionnelle"
LABEL version="3.1.0"

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=web/api.py
ENV FLASK_ENV=production
ENV PORT=5000

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN useradd -m -s /bin/bash sentrax && chown -R sentrax:sentrax /app
USER sentrax

EXPOSE 5000

CMD ["python", "web/api.py"]
