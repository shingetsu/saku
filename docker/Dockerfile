FROM python:3.12-slim

COPY . /saku
WORKDIR /saku
RUN cp docker/saku.ini file/saku.ini
RUN python -m pip install --upgrade pip
RUN python -m pip install pipenv
RUN pipenv install

COPY ./docker/entrypoint.sh /
RUN chmod 755 /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]

