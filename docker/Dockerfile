FROM python:3.13-slim

COPY Pipfile /saku/Pipfile
WORKDIR /saku
RUN python -m pip install --upgrade pip
RUN python -m pip install pipenv
RUN pipenv install

COPY . /saku
COPY docker/saku.ini /saku/file/saku.ini
COPY docker/entrypoint.sh /
RUN chmod 755 /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
