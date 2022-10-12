FROM python:3.10-alpine
LABEL org.opencontainers.image.authors="lerignoux@gmail.com"

RUN apk add --no-cache mupdf mupdf-tools mupdf-dev gcc musl-dev freetype-dev jpeg jbig2dec freetype openssl git
RUN ln -s /usr/include/freetype2/ft2build.h /usr/include/ft2build.h \
 && ln -s /usr/include/freetype2/freetype/ /usr/include/freetype

COPY . /app
WORKDIR /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python"]
CMD ["app.py"]
