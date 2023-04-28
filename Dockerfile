FROM python:3.9.15-slim
WORKDIR /app

RUN apt-get update && apt-get install -y curl vim
RUN apt-get clean

RUN pip install --upgrade pip


#poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:${PATH}"
# RUN poetry config virtualenvs.create false
COPY pyproject.toml /app
COPY poetry.lock /app
RUN poetry install --no-dev
RUN yes | poetry cache clear . --all
# RUN rm pyproject.toml
# RUN rm poetry.lock
# RUN rm -rf /root/.poetry

RUN mkdir ./log
COPY ./app /app

ENTRYPOINT [ "sh" ]
CMD ["db_init.sh"]
