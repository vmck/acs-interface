FROM python:3.7-stretch

ENV PATH="/root/.local/bin:${PATH}"
WORKDIR /opt/interface

COPY manage.py runinterface README.md Pipfile Pipfile.lock ./
ADD interface ./interface
RUN set -e \
 && pip install --user pipenv \
 && pipenv install \
 && pipenv run ./manage.py collectstatic

VOLUME /opt/interface/data
EXPOSE 8100
CMD ./runinterface
