FROM python:alpine3.18

WORKDIR /src

COPY . . 

RUN apk add vim curl busybox-extras iputils-ping

RUN pip install --no-cache-dir -r requirements.txt


ENTRYPOINT python main.py
