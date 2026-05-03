# symptom-triage-analytics-platform

Rule-based conversational symptom triage platform with AI extraction only. This project is not a diagnosis system.

## Architecture

- `Streamlit` collects chat-style symptom input
- `OpenAI API` extracts strict JSON only
- `Python` validates, normalizes, and triages with deterministic rules
- `Snowflake` stores structured interactions
- `dbt` transforms raw records into analytics-ready marts
- `Power BI` consumes marts for dashboards

## Repo structure

- [app/streamlit_app.py](/C:/Project%20MDS/symptom-triage-analytics-platform/app/streamlit_app.py)
- [triage_app](/C:/Project%20MDS/symptom-triage-analytics-platform/triage_app)
- [tests](/C:/Project%20MDS/symptom-triage-analytics-platform/tests)
- [dbt](/C:/Project%20MDS/symptom-triage-analytics-platform/dbt)
- [docs/snowflake-setup-checklist.md](/C:/Project%20MDS/symptom-triage-analytics-platform/docs/snowflake-setup-checklist.md)
- [.github/workflows/ci.yml](/C:/Project%20MDS/symptom-triage-analytics-platform/.github/workflows/ci.yml)

## Local development

1. Create a virtual environment and install dependencies from `requirements.txt`
2. Create `.env` from `.env.example` with your Snowflake and OpenAI credentials
3. Set `SNOWFLAKE_SCHEMA=ANALYTICS` and `SNOWFLAKE_RAW_SCHEMA=RAW`
4. Add `OPENAI_API_KEY` if you want live extraction
5. Run `streamlit run app/streamlit_app.py`

If `OPENAI_API_KEY` is missing, the app falls back to a simple stub extractor for local development.

## Tests

Run:

```bash
pytest -q
```

## CI/CD

GitHub Actions runs Python tests, compile checks, Docker image builds, and `dbt parse` on pull requests and pushes to `main`.

## Snowflake migrations

For an existing v1 database, run:

```sql
-- in Snowsight
-- docs/snowflake-phase2-migration.sql
```

## Docker

Start the local app:

```bash
docker compose up --build app
```

Check dbt connectivity later after Snowflake is configured:

```bash
docker compose run --rm dbt dbt debug --profiles-dir /dbt/profiles
```
