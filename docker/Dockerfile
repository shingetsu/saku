FROM python:3.14.7-slim@sha256:656d12e70054d5fda18a045e2494c96701e9792dd1445f95b3d038df954f57e9

RUN groupadd -g 1000 saku && \
    useradd -m -d /saku -s /bin/bash -u 1000 -g 1000 saku

WORKDIR /saku
ENV PATH=/saku/.local/bin:$PATH

USER saku:saku
COPY Pipfile* ./
RUN python -m pip install pipenv && \
    pipenv install && \
    rm -Rf .cache

USER root:root
COPY docker/entrypoint.sh /
RUN chmod 755 /entrypoint.sh && \
  chown -R root:root /saku && \
  chmod 755 /saku
COPY file file
COPY shingetsu shingetsu
COPY template template
COPY www www
COPY saku.py .
COPY docker/saku.ini file
RUN python -m compileall shingetsu

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
