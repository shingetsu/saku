FROM python:3.11.4-slim-bookworm

COPY . /saku
WORKDIR /saku
RUN python -m pip install pipenv
RUN pipenv install

EXPOSE 8000
ENTRYPOINT ["/bin/bash", "-c", "pipenv run python ./saku.py -v"]

