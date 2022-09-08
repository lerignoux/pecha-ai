FROM python:3.10-alpine
LABEL org.opencontainers.image.authors="lerignoux@gmail.com"

COPY . /app
WORKDIR /app

RUN apk add --update git
RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]
