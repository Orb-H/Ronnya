FROM python:latest

LABEL maintainer="playjnj@khu.ac.kr"

RUN mkdir /usr/src/front
ADD . /usr/src/front

WORKDIR /usr/src/front

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt
