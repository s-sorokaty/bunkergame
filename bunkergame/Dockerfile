FROM python:3.12


RUN apt update
RUN pip install poetry make

COPY pyproject.toml poetry.lock manage.py /bunkergame/
RUN cd /bunkergame/ && poetry install --no-root
WORKDIR /bunkergame
