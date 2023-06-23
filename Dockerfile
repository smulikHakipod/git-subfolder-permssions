# Pyptter does not support m1/arm it seems
FROM httpd:2.4.57-alpine3.18



# Install python/pip
ENV PYTHONUNBUFFERED=1
RUN apk add --update python3 && ln -sf python3 /usr/bin/python
RUN python3 -m ensurepip
RUN pip3 install  --upgrade pip setuptools


# we need to move to those to a temp machine and copy the output
RUN apk add libffi-dev
RUN apk add python3-dev

RUN apk add gcc
RUN apk add curl curl-dev libcurl
RUN apk add openssl-dev zlib-dev

# install git
RUN apk --update add gcc make g++ zlib-dev autoconf
RUN apk add gettext asciidoc xmlto
RUN curl https://codeload.github.com/git/git/zip/refs/tags/v2.41.0 -o git-2.41.zip
RUN unzip git-2.41.zip
RUN cd git-2.41.0 && make configure && ./configure --prefix=/usr &&  make -j 4 all doc && make install install-doc install-html
RUN rm -rf git-lfs-3.3.0.zip git-2.41.0

# install git lfs
RUN curl https://codeload.github.com/git-lfs/git-lfs/zip/refs/tags/v3.3.0 -o git-lfs-3.3.0.zip
RUN unzip git-lfs-3.3.0.zip

RUN apk add go
RUN cd git-lfs-3.3.0 && make -j 8 && cp bin/git-lfs /usr/bin/git-lfs
RUN rm -rf git-lfs-3.3.0 git-lfs-3.3.0.zip

RUN apk fix && \
    apk --no-cache --update add gpg less openssh patch && \
    git lfs install

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
RUN apk add -U shadow
RUN mkdir -p /git-hooks/
RUN cp /usr/libexec/git-core/git /usr/libexec/git-core/git2