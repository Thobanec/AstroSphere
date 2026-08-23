FROM python:3.13-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

ENV ASTROSPHERE_HOST=0.0.0.0
ENV ASTROSPHERE_PORT=5000
ENV ASTROSPHERE_DEBUG=false

COPY pyproject.toml .
COPY src ./src
COPY web ./web

RUN python -m pip install --upgrade pip \
    && python -m pip install .

EXPOSE 5000

CMD ["python", "-m", "web.app"]
