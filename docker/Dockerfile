FROM python:3.13-slim

RUN groupadd -g 1000 saku && \
    useradd -m -d /saku -s /bin/bash -u 1000 -g 1000 saku

WORKDIR /saku
ENV PATH=/saku/.local/bin:$PATH

USER saku:saku
COPY Pipfile* ./
RUN python -m pip install pipenv && \
    pipenv install

USER root:root
COPY docker/entrypoint.sh /
RUN chmod 755 /entrypoint.sh && \
  chown -R root:root /saku
COPY file file
COPY shingetsu shingetsu
COPY template template
COPY www www
COPY saku.py .
COPY docker/saku.ini file

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
