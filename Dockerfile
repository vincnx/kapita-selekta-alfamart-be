#builder stage
FROM python:3.12-slim-bullseye AS builder
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install  -y libpq-dev gcc

#create virtual environment
RUN python -m venv /opt/venv
ENV PATH="opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install -r requirements.txt


#Operational Stage
FROM python:3.12-slim-bullseye
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y libpq-dev
RUN rm -rf /var/lib/apt/lists/*

#get env from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:PATH"
ENV CLOUD_APPS CLOUD_RUN
WORKDIR /kapita-selekta
COPY . ./
CMD . /opt/venv/bin/activate && exec gunicorn --bind 0.0.0.0:8080 --workers 1 --threads 8 main:app