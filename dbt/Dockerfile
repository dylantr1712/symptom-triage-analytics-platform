FROM python:3.11-slim

WORKDIR /dbt

COPY dbt/requirements.txt /dbt/requirements.txt
RUN pip install --no-cache-dir -r /dbt/requirements.txt

COPY dbt /dbt

CMD ["dbt", "--version"]

