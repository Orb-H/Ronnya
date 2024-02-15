FROM python:3.12.0-slim-bullseye

COPY . /app
WORKDIR /app
EXPOSE 5000
RUN pip install -r requirements.txt
CMD ["python", "client.py"]