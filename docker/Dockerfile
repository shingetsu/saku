FROM python:3.14.6-slim@sha256:b877e50bd90de10af8d82c57a022fc2e0dc731c5320d762a27986facfc3355c1 as builder

ENV PATH=/saku/.local/bin:$PATH
ENV PYTHONUSERBASE=/saku/.local
ENV PIPENV_VENV_IN_PROJECT=1

WORKDIR /saku
RUN python -m pip install --user --no-cache-dir --root-user-action=ignore pipenv
COPY Pipfile* ./
RUN pipenv install

COPY shingetsu shingetsu
RUN python -m compileall shingetsu


FROM gcr.io/distroless/python3-debian13:nonrot@sha256:828da6b298ecebf90580c84476c29b847b6432b46dbfaa642726b87ac527ee22

ENV PYTHONPATH="/saku/.venv/lib/python3.14/site-packages"

WORKDIR /saku
COPY --from=builder /saku/.venv .venv
COPY --from=builder /saku/shingetsu shingetsu
COPY file file
COPY template template
COPY www www
COPY saku.py .
COPY docker/saku.ini file

EXPOSE 8000
ENTRYPOINT ["python", "./saku.py", "-v"]
