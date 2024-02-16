FROM python:3.12.0-slim-bullseye

COPY . /app
WORKDIR /app
EXPOSE 5555 5556
RUN pip install -r requirements.txt
CMD ["python", "router.py"]