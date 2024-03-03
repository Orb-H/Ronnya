FROM python:3.12.0-slim-bullseye

COPY . /app
WORKDIR /app
EXPOSE 5000 5555
RUN apt-get update
RUN apt-get install -y build-essential libzmq3-dev
RUN pip install -r requirements.txt
CMD ["python", "client.py"]