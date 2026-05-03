.PHONY: test compile app docker-app dbt-debug dbt-run dbt-parse

test:
	pytest -q

compile:
	python -m compileall triage_app app tests

app:
	streamlit run app/streamlit_app.py

docker-app:
	docker compose up --build app

dbt-debug:
	docker compose run --rm dbt dbt debug --profiles-dir /dbt/profiles

dbt-run:
	docker compose run --rm dbt dbt run --profiles-dir /dbt/profiles

dbt-parse:
	docker compose run --rm dbt dbt parse --profiles-dir /dbt/profiles

