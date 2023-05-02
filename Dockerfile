FROM python:3.10-bullseye AS builder
RUN apt-get update && apt-get install -y curl vim --no-install-recommends
RUN apt-get clean
RUN curl -sSL https://install.python-poetry.org | python3 -

FROM python:3.10-bullseye AS APP
WORKDIR /app

COPY --from=builder /usr/bin/vim /usr/bin/vim
COPY --from=builder /usr/bin/curl /usr/bin/curl
COPY --from=builder /root/.local /root/.local

ENV PATH="/root/.local/bin:${PATH}"

COPY pyproject.toml /app
COPY poetry.lock /app
RUN poetry install --no-dev
RUN poetry cache clear . --all

RUN mkdir ./log
COPY ./app /app

ENTRYPOINT [ "sh" ]
CMD ["db_init.sh"]
 
