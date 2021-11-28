# Based on the image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.202.3/containers/python-3/.devcontainer/base.Dockerfile
# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.10-bullseye"

FROM --platform=linux/arm64 python:${VARIANT} as arm64

FROM --platform=linux/amd64 python:${VARIANT} as amd64
RUN apt-get update && apt-get install -y unixodbc unixodbc-dev
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

FROM ${TARGETARCH} as sqlgrader
ARG BUILDID="TBD"

# django default port, change in django-init.sh if needed
EXPOSE 80
# open flask port
EXPOSE 5000

# postgres driver steps
RUN apt-get update && apt-get install -y libpq-dev postgresql-client

# pyodbc driver steps, minimal requirements
RUN apt-get update && apt-get install -y unixodbc-dev

# pip requirements
COPY api/requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
   && rm -rf /tmp/pip-tmp

# bring in webUI and api code
COPY webui/ /code/webui/  
COPY api/ /code/api/
COPY webui.Dockerfile /code/Dockerfile

# passing persistent volumes through
VOLUME /code/webui/sqlite
VOLUME /code/webui/media

# internal password for grader runtime databases
ENV DEFAULTPASSWORD="P@ssw0rd"

# flask app environment
ENV FLASK_APP=main.py

# django allowed host
ENV THISURL="localhost"

# app build number for webui
ENV BUILDNUMBER=${BUILDID}

RUN chmod +x /code/api/entrypoint.sh

# If "context" is set to ".." in devcontainer.json, use .devcontainer/library-scripts/*.sh
COPY docker-build-scripts/*.sh /tmp/library-scripts/

ENV DOCKER_BUILDKIT=1
RUN apt-get update && /bin/bash /tmp/library-scripts/docker-in-docker-debian.sh
ENTRYPOINT ["/usr/local/share/docker-init.sh", "/code/api/entrypoint.sh"]
VOLUME [ "/var/lib/docker" ]
CMD ["sleep", "infinity"]