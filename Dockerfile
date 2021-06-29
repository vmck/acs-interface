FROM python:3.7.10-stretch

RUN set -e \
 && apt-get update -q \
 && apt-get install -yq libsasl2-dev python-dev libldap2-dev libssl-dev fortune \
 && apt-get clean && rm -rf /var/lib/apt/lists/* \
 && pip install pipenv \
 && ln -s /usr/games/fortune /usr/local/bin/fortune

WORKDIR /opt/interface
COPY Pipfile Pipfile.lock ./
RUN pipenv install --system --deploy --ignore-pipfile

COPY manage.py runinterface Readme.md ./
ADD interface ./interface
RUN export PROFILE=True && ./manage.py collectstatic --no-input

VOLUME /opt/interface/data
EXPOSE 8100
CMD ./runinterface
