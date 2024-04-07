FROM python:3.10-slim-buster

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY app /app/app
COPY .env /app/.env
COPY run.py /app/run.py

CMD [ "python3", "run.py"] 