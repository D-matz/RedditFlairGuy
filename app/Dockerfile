FROM python:3.6.12-alpine as builder

COPY requirements.txt /
RUN pip3 install -r /requirements.txt

COPY . /app
WORKDIR /app

EXPOSE 443

ENTRYPOINT ["gunicorn", "-c", "configgunicorn.py"]
