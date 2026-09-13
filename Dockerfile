FROM python:3.12-slim-bookworm
ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 PORT=8081 LIVE_ENABLED=false
WORKDIR /app
COPY requirements.lock ./
RUN pip install --no-cache-dir --require-hashes -r requirements.lock && useradd --create-home --uid 10002 portfolio
COPY app app
RUN chown -R portfolio:portfolio /app
USER portfolio
EXPOSE 8081
CMD ["sh","-c","exec python -m uvicorn app.main:app --factory --host 0.0.0.0 --port ${PORT:-8081} --no-access-log"]
