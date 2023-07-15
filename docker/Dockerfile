FROM python:3.9

COPY ../routes/ /instagram/routes
COPY ../*.py /instagram/
COPY ../*.ini /instagram/
COPY ../*.txt /instagram/

WORKDIR /instagram/

RUN pip install -r requirements.txt

