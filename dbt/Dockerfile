FROM python:3.11-slim

WORKDIR /dbt

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY dbt/requirements.txt /dbt/requirements.txt
RUN pip install --no-cache-dir -r /dbt/requirements.txt

COPY dbt /dbt

CMD ["dbt", "--version"]
