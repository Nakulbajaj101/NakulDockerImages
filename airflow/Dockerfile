# VERSION 1.10.10
# AUTHOR: Matthieu "Puckel_" Roisil
# DESCRIPTION: Basic Airflow container
# BUILD: docker build --rm -t puckel/docker-airflow for original one.
# SOURCE: https://github.com/puckel/docker-airflow
# MODIFIED BY: "Nakul Bajaj"
# MODIFIED DATE: "2020-July-23"

FROM python:3.7-slim-buster
LABEL maintainer="Nakul"

# Never prompt the user for choices on installation/configuration of packages
ENV DEBIAN_FRONTEND noninteractive
ENV TERM linux


# Airflow
ARG AIRFLOW_VERSION=1.10.11
ARG AIRFLOW_USER_HOME=/usr/local/airflow
ARG AIRFLOW_DEPS=""
ARG PYTHON_DEPS=""
# ARG GCLOUD_SDK_VERSION="300.0.7"
ARG PYTHON_MAJOR_MINOR_VERSION="3.7"
ARG GOOGLE_PROJECT="bridge_data_analytics"
ENV AIRFLOW_HOME=${AIRFLOW_USER_HOME}
ENV GOOGLE_CLOUD_PROJECT=${GOOGLE_PROJECT}

# Define en_US.
ENV LANGUAGE en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8
ENV LC_CTYPE en_US.UTF-8
ENV LC_MESSAGES en_US.UTF-8
ENV GCLOUD_HOME="/opt/gcloud" CLOUDSDK_PYTHON=python${PYTHON_MAJOR_MINOR_VERSION}


# Disable noisy "Handling signal" log messages:
# ENV GUNICORN_CMD_ARGS --log-level WARNING

RUN set -ex \
    && buildDeps=' \
        freetds-dev \
        libkrb5-dev \
        libsasl2-dev \
        libssl-dev \
        libffi-dev \
        libpq-dev \
        git \
    ' \
    && apt-get update -yqq \
    && apt-get upgrade -yqq \
    && apt-get install -yqq --no-install-recommends \
        $buildDeps \
        freetds-bin \
        build-essential \
        default-libmysqlclient-dev \
        apt-utils \
        curl \
        rsync \
        netcat \
        locales \
    && apt-get install -y wget && rm -rf /var/lib/apt/lists/* \
    && sed -i 's/^# en_US.UTF-8 UTF-8$/en_US.UTF-8 UTF-8/g' /etc/locale.gen \
    && locale-gen \
    && update-locale LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 \
    && useradd -ms /bin/bash -d ${AIRFLOW_USER_HOME} airflow \
    && pip install -U pip setuptools wheel \
    && pip install pytz \
    && pip install pyOpenSSL \
    && pip install ndg-httpsclient \
    && pip install httplib2 \
    && pip install pyasn1 \
    && pip install apache-airflow[async,crypto,sendgrid,celery,postgres,hive,jdbc,gcp,google_auth,slack,mysql,ssh,kubernetes,virtualenv${AIRFLOW_DEPS:+,}${AIRFLOW_DEPS}]==${AIRFLOW_VERSION} --use-feature=2020-resolver \
    && pip install 'redis==3.2' \
    && pip install matplotlib \
    && pip install scipy \
    && pip install fastavro==0.23.6 \
    && pip install pyarrow==0.17.1 \
    && pip install tqdm==4.42.1 \
    && pip install google-cloud-bigquery-storage==1.0.0 --use-feature=2020-resolver \
    && pip install google-cloud-bigquery==1.24.0 --use-feature=2020-resolver \
    && pip install pandas==1.0.1 \
    && pip install pandas-gbq==0.13.2 \
    && pip install plotly \
    && pip install -U kaleido \
    && pip install folium \
    && pip uninstall SQLAlchemy -y \
    && pip install SQLAlchemy==1.3.15 --use-feature=2020-resolver \
    && pip install apache-beam[gcp] \
    && if [ -n "${PYTHON_DEPS}" ]; then pip install ${PYTHON_DEPS}; fi \
    && apt-get purge --auto-remove -yqq $buildDeps \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf \
        /var/lib/apt/lists/* \
        /tmp/* \
        /var/tmp/* \
        /usr/share/man \
        /usr/share/doc \
        /usr/share/doc-base \
    && mkdir ${AIRFLOW_USER_HOME}/packages \
    && GCLOUD_VERSION="300.0.0" \
    && GCOUD_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-${GCLOUD_VERSION}-linux-x86_64.tar.gz" \
    && GCLOUD_TMP_FILE="/tmp/gcloud.tar.gz" \
    && export CLOUDSDK_CORE_DISABLE_PROMPTS=1 \
    && mkdir -p /opt/gcloud \
    && curl "${GCOUD_URL}" -o "${GCLOUD_TMP_FILE}"\
    && tar xzf "${GCLOUD_TMP_FILE}" --strip-components 1 -C "${GCLOUD_HOME}" \
    && rm -rf "${GCLOUD_TMP_FILE}" \
    && ${GCLOUD_HOME}/bin/gcloud components install beta core gsutil bq kubectl



ENV PATH="$PATH:${GCLOUD_HOME}/bin"
ENV GOOGLE_APPLICATION_CREDENTIALS="${AIRFLOW_USER_HOME}/.config/gcloud/application_default_credentials.json"
ENV AIRFLOW_CONN_BIGQUERY_DEFAULT="google-cloud-platform://:@:?extra__google_cloud_platform__project=${GOOGLE_PROJECT}"
COPY script/entrypoint.sh /entrypoint.sh
COPY config/airflow.cfg ${AIRFLOW_USER_HOME}/airflow.cfg

RUN chown -R airflow: ${AIRFLOW_USER_HOME}

EXPOSE 8080 5555 8793

USER airflow
WORKDIR ${AIRFLOW_USER_HOME}


ENTRYPOINT ["/entrypoint.sh"]
