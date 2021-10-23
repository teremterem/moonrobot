FROM python:3.8.12

ENV PYTHONUNBUFFERED 1
# https://stackoverflow.com/questions/59812009/what-is-the-use-of-pythonunbuffered-in-docker-file
# https://github.com/awslabs/amazon-sagemaker-examples/issues/319

RUN mkdir /code
WORKDIR /code

RUN pip install pipenv==2021.5.29

COPY Pipfile /code/
COPY Pipfile.lock /code/

RUN pipenv install --deploy

COPY . /code/
