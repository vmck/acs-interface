FROM python:3.7.5-stretch

ENV PATH="/root/.local/bin:${PATH}"
WORKDIR /opt/interface

COPY manage.py runinterface Readme.md Pipfile Pipfile.lock ./
ADD interface ./interface
RUN set -e \
 && apt-get update -q \
 && apt-get install -yq libsasl2-dev python-dev libldap2-dev libssl-dev fortune \
 && pip install --user pipenv \
 && pipenv install \
 && pipenv run ./manage.py collectstatic

VOLUME /opt/interface/data
EXPOSE 8100
CMD ./runinterface
