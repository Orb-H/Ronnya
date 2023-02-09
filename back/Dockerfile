FROM python:latest

LABEL maintainer="playjnj@khu.ac.kr"

RUN mkdir /usr/src/back
ADD . /usr/src/back

WORKDIR /usr/src/back

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt