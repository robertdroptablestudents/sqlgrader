# Based on the image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.202.3/containers/python-3/.devcontainer/base.Dockerfile
# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.10-bullseye"
FROM python:bullseye

# django default port, change in django-init.sh if needed
EXPOSE 80

# pip requirements
COPY webui/requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
   && rm -rf /tmp/pip-tmp

# django interface secret key
ENV secretkey="0xb8xKH!%TR!0Wv5zJA4#gMURq&HehOpxybf"
# django allowed host
ENV THISURL="localhost"
# app build number for webui
ENV BUILDNUMBER="TBD"

COPY webui/ /code/webui/

VOLUME /code/webui/sqlite
VOLUME /code/webui/media

RUN chmod +x /code/webui/django-init.sh
WORKDIR /code/webui

ENTRYPOINT [ "bash", "./django-init.sh" ]