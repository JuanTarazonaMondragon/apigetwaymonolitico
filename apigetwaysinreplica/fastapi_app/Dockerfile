FROM python:3.10-slim
ADD ./requirements.txt /app/requirements.txt
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT uvicorn --host 0.0.0.0 --port ${UVICORN_PORT} app:app
