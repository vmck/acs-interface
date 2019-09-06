FROM python:3.7-stretch

ENV PATH="/root/.local/bin:${PATH}"
WORKDIR /opt/interface

RUN set -e \
 && pip install --user pipenv

COPY manage.py runinterface README.md Pipfile Pipfile.lock ./
RUN pipenv install

ADD interface ./interface

VOLUME /opt/interface/data
EXPOSE 8100
CMD ./runinterface
