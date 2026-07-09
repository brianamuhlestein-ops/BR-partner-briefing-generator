FROM python:3.12-slim

WORKDIR /srv/partner-briefing

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV API_HOST=0.0.0.0
ENV API_PORT=8089
ENV DATABASE_PATH=/srv/partner-briefing/data/email_briefing.db
ENV GENERATED_DIR=/srv/partner-briefing/generated

COPY api/requirements.txt ./api/requirements.txt

RUN pip install --no-cache-dir -r ./api/requirements.txt

COPY api ./api

RUN mkdir -p ./data ./generated

EXPOSE 8089

CMD ["python", "-m", "api.run_api"]
