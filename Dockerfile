# Pyptter does not support m1/arm it seems
FROM httpd:2.4.57-alpine3.18


# install git
RUN apk fix && \
    apk --no-cache --update add git git-lfs git-daemon gpg less openssh patch && \
    git lfs install


# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install  --upgrade pip setuptools


# we need to move to those to a temp machine and copy the output
RUN apk add libffi-dev
RUN apk add python3-dev

RUN apk add gcc
RUN apk add curl
RUN apk add cargo 

COPY ./requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt


ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD true
ENV PUPPETEER_EXECUTABLE_PATH /usr/bin/chromium-browser

# Installs latest Chromium package. Otherwise this does not work on ARM macs.
RUN apk upgrade --no-cache --available \
    && apk add --no-cache \
      chromium-swiftshader \
      ttf-freefont \
      font-noto-emoji \
    && apk add --no-cache \
      --repository=https://dl-cdn.alpinelinux.org/alpine/edge/testing \
      font-wqy-zenhei

RUN apk add bash

RUN mkdir -p /git-hooks/
CMD export PATH=$ADDITIONAL_PATH:$PATH;