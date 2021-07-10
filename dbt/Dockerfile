# AUTHOR: Nakul Bajaj

FROM docker:19.03.11 as static-docker-source
FROM debian:buster-slim


RUN apt-get update \
    && apt-get dist-upgrade -y \
    && apt-get install -y --no-install-recommends \
    git \
    software-properties-common \
    make \
    build-essential \
    ca-certificates \
    libffi-dev \
    libpq-dev \
    curl \
    python3-dev \
    python3-pip \
    apt-transport-https \
    gcc \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*



ENV GCLOUD_HOME="/opt/gcloud" 
RUN GCLOUD_VERSION="330.0.0" \
    && GCOUD_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${GCLOUD_VERSION}-linux-x86_64.tar.gz" \
    && GCLOUD_TMP_FILE="/tmp/gcloud.tar.gz" \
    && export CLOUDSDK_CORE_DISABLE_PROMPTS=1 \
    && mkdir -p /opt/gcloud \
    && curl "${GCOUD_URL}" -o "${GCLOUD_TMP_FILE}"\
    && tar xzf "${GCLOUD_TMP_FILE}" --strip-components 1 -C "${GCLOUD_HOME}" \
    && rm -rf "${GCLOUD_TMP_FILE}" \
    && ${GCLOUD_HOME}/bin/gcloud components install beta core bq

ENV PATH="$PATH:${GCLOUD_HOME}/bin"

COPY requirements.txt ./requirements.txt
RUN pip3 install --upgrade pip setuptools
RUN pip3 install --requirement requirements.txt
ENV PYTHONIOENCODING=utf-8
ENV LANG C.UTF-8


ENV SOURCE_PATH=/source
ENV DBT_PROFILES_DIR=${SOURCE_PATH}/.dbt/
ENV DBT_SERVICE_ACCOUNTS_PATH=${SOURCE_PATH}/service-accounts/
WORKDIR /${SOURCE_PATH}
COPY profiles.yml ${DBT_PROFILES_DIR}

WORKDIR /dbt

ADD dbt-projects dbt-projects

RUN adduser --disabled-password --gecos '' dbtuser

RUN chown -R dbtuser: ${SOURCE_PATH}/
RUN chown -R dbtuser: /dbt

USER dbtuser

ENTRYPOINT [ "sh" ]
