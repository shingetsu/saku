FROM python:3.11-slim

COPY . /opt/saku
WORKDIR /opt/saku
RUN mv file/saku.ini.docker file/saku.ini
RUN python -m pip install pipenv
RUN pipenv install

EXPOSE 8000
ENTRYPOINT ["/bin/bash", "-c", "pipenv run python ./saku.py -v"]

