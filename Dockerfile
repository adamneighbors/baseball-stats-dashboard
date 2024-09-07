FROM ubuntu:jammy

# Set Environment Variables
ENV APP_ROOT /opt/baseball-dashboard
ENV VIRTUAL_ENV $APP_ROOT/.venv
ENV PATH $PATH:${VIRTUAL_ENV}/bin
ENV TZ="America/Chicago"
ENV USERNAME baseball
ENV APP_GID 1500
ENV APP_UID 1500

# Install initial dependencies
RUN set -x; \
        apt-get update \
        && apt-get install -y \
            python3.12 \
            python3.12-venv \
            python3-pip

# Install additional packages

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE=1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED=1size
ENV LANG=C.UTF-8

# Copy Current dir to container
COPY . $APP_ROOT

# Install pip requirements
RUN set -x; \
    python3.12 -m venv $VIRTUAL_ENV \
    && $VIRTUAL_ENV/bin/pip install --upgrade pip \
    && $VIRTUAL_ENV/bin/pip install --no-cache-dir --disable-pip-version-check --trusted-host pypi.org --trusted-host files.pythonhosted.org -r $APP_ROOT/requirements.txt 

# Creates a non-root user with an explicit UID and adds permission to access the $APP_ROOT folder
# For more info, please refer to https://aka.ms/vscode-docker-python-configure-containers
RUN groupadd -g $APP_GID $USERNAME \
    && useradd -m -s /bin/bash -u $APP_UID -g $APP_GID $USERNAME \
    && chown -R $USERNAME:$USERNAME $APP_ROOT

USER baseball
WORKDIR ${APP_ROOT}

ENTRYPOINT ["python ${APP_ROOT}/manage.py runserver"]