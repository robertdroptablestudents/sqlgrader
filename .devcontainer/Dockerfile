# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.205.2/containers/python-3/.devcontainer/base.Dockerfile

# [Choice] Python version (use -bullseye variants on local arm64/Apple Silicon): 3, 3.10, 3.9, 3.8, 3.7, 3.6, 3-bullseye, 3.10-bullseye, 3.9-bullseye, 3.8-bullseye, 3.7-bullseye, 3.6-bullseye, 3-buster, 3.10-buster, 3.9-buster, 3.8-buster, 3.7-buster, 3.6-buster
ARG VARIANT="3.10-bullseye"
FROM mcr.microsoft.com/vscode/devcontainers/python:0-${VARIANT}

# amd64 only
# RUN apt-get update && apt-get install -y unixodbc unixodbc-dev
# RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
# RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
# RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
#     && ACCEPT_EULA=Y apt-get install -y msodbcsql17

# postgres driver steps
RUN apt-get update && apt-get install -y libpq-dev postgresql-client

# pyodbc driver steps, minimal requirements
# microsoft repo in apt sources breaks this
# RUN apt-get update && apt-get install -y unixodbc-dev

# [Optional] If your pip requirements rarely change, uncomment this section to add them to the image.
COPY requirements.txt /tmp/pip-tmp/
RUN pip3 --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
   && rm -rf /tmp/pip-tmp

# internal password for grader runtime databases
ENV DEFAULTPASSWORD="P@ssw0rd"
# django interface secret key
ENV secretkey="0xb8xKH!%TR!0Wv5zJA4#gMURq&HehOpxybf"
# django allowed host
ENV THISURL="localhost"
# app build number for webui
ENV BUILDNUMBER="TBD"
# flask app environment
ENV FLASK_APP=main.py
ENV FLASK_ENV=development
# [Optional] Uncomment this line to install global node packages.
# RUN su vscode -c "source /usr/local/share/nvm/nvm.sh && npm install -g <your-package-here>" 2>&1


# If "context" is set to ".." in devcontainer.json, use .devcontainer/library-scripts/*.sh
COPY .devcontainer/library-scripts/*.sh /tmp/library-scripts/

ENV DOCKER_BUILDKIT=1
RUN apt-get update && /bin/bash /tmp/library-scripts/docker-in-docker-debian.sh
ENTRYPOINT ["/usr/local/share/docker-init.sh"]
VOLUME [ "/var/lib/docker" ]
CMD ["sleep", "infinity"]