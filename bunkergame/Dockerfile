FROM python:3.12


RUN apt update
RUN pip install poetry

COPY pyproject.toml poetry.lock manage.py /workspace/
RUN cd /workspace/ && poetry install --no-root
WORKDIR /workspace
