FROM python:3.12.0-slim-bullseye

COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["python", "worker.py"]