# Symptom Triage Analytics Platform

A conversational symptom triage analytics platform built with Streamlit, OpenAI, deterministic Python rules, Snowflake, dbt, Power BI, Docker, and GitHub Actions.

This project is intentionally **not a diagnosis system**. It does not attempt to predict a disease or replace clinical judgment. The goal is to demonstrate a safe, explainable data platform pattern: use AI to structure messy user input, use deterministic logic for the actual triage decision, then store the full interaction as analytics-ready data.

## Project Idea

The user describes symptoms in a chat-style interface. The system extracts structured fields from the conversation, validates that enough information exists, applies a small risk-based triage rule set, returns a recommendation, and stores both the raw and structured data for analytics.

The three possible triage outcomes are:

- `SELF_CARE`
- `SEE_GP`
- `EMERGENCY`

The main design principle is separation of responsibility:

- AI extracts structured data only.
- Python rules make the triage decision.
- Snowflake stores raw and structured records.
- dbt transforms those records into analytics models.
- Power BI consumes the marts for dashboards and insight.

## High-Level Architecture

```text
Streamlit Chat UI
    |
    v
OpenAI Structured Extraction
    |
    v
Validation and Normalization
    |
    v
Deterministic Triage Engine
    |
    v
Snowflake RAW Tables
    |
    v
dbt Staging, Intermediate, and Mart Models
    |
    v
Power BI Dashboards
```

## Tech Stack

- `Streamlit`: simple chat-style UI for entering symptoms and showing results.
- `OpenAI API`: converts free-text symptom descriptions into strict JSON.
- `Python`: validates inputs, normalizes symptoms, derives severity, and applies triage rules.
- `Snowflake`: stores raw session records, rule hits, and symptom mentions.
- `dbt`: cleans and models raw data into analytics-ready facts and aggregates.
- `Power BI`: connects to dbt marts for reporting and exploration.
- `Docker`: provides repeatable local app and dbt environments.
- `GitHub Actions`: runs CI checks for tests, compile checks, Docker builds, and dbt parsing.

## Why AI Is Used Only for Extraction

The LLM is useful for converting unstructured text like:

```text
I am 42 and I have had severe chest pain and shortness of breath since this morning.
```

into structured fields:

```json
{
  "symptoms": ["chest_pain", "shortness_of_breath"],
  "duration_bucket": "hours",
  "age_years": 42,
  "severity_cues": ["severe"],
  "missing_fields": []
}
```

The LLM does **not** decide whether the user should self-care, see a GP, or seek emergency care. That decision is made by deterministic Python rules.

This choice was made because triage output should be:

- reproducible
- explainable
- testable
- auditable
- independent from model reasoning drift

For an interview project, this is one of the most important architectural decisions: the system gets the flexibility of AI input understanding without giving the LLM authority over the safety-critical recommendation.

## Triage Logic

The triage engine is risk-based rather than disease-based.

The rules evaluate in priority order:

1. Emergency rules
2. See-GP rules
3. Self-care fallback

Emergency rules include:

- severe shortness of breath
- severe chest pain
- confusion
- seizure
- loss of consciousness
- heavy bleeding

See-GP rules include:

- moderate symptoms lasting `3_7_days` or `over_1_week`
- persistent vomiting
- persistent fever
- worsening non-emergency symptoms

Self-care is only returned when no emergency or GP rules match and the symptoms are mild, short-duration, and low-risk.

Each decision returns:

- triage level
- headline
- explanation
- next step
- triggered rules
- explanation trace

Example trace:

```text
Detected normalized symptom: chest_pain
Detected normalized symptom: shortness_of_breath
Severity normalized to severe
Duration bucket normalized to hours
Evaluated rules in priority order and selected EMERGENCY
Triggered rule: ER001 (severe_shortness_of_breath)
Triggered rule: ER002 (severe_chest_pain)
```

## Severity Design

The project does not use the provided symptom severity CSV as the main triage decision engine. Static symptom weights are useful for enrichment, but they are not enough for triage because urgency depends on context.

For example:

- mild chest discomfort is different from severe chest pain with shortness of breath
- vomiting for one hour is different from persistent vomiting over multiple days
- fever alone is different from fever with confusion or worsening symptoms

The implemented approach is:

- OpenAI extracts severity cues from the user text.
- Python normalizes those cues into `mild`, `moderate`, `severe`, or `unknown`.
- The triage engine uses that normalized severity plus symptoms and duration.

This keeps the decision explainable and deterministic.

## Validation and Insufficient Information

The system does not triage if required fields are missing.

Required fields are:

- symptoms
- duration bucket
- age
- severity cues

If information is missing, the pipeline returns `INSUFFICIENT_INFORMATION` with a follow-up question. This prevents the system from guessing when the user has not provided enough context.

The current scope is adults only. Users under 18 are routed to an unsupported path rather than evaluated by the adult rule set.

## Data Stored in Snowflake

The app writes to three raw Snowflake tables:

- `TRIAGE_PLATFORM.RAW.TRIAGE_SESSIONS`
- `TRIAGE_PLATFORM.RAW.TRIAGE_RULE_HITS`
- `TRIAGE_PLATFORM.RAW.TRIAGE_SESSION_SYMPTOMS`

The session table stores:

- raw user text
- extracted fields
- normalized severity
- triage outcome
- validation status
- pipeline status
- raw OpenAI response
- unmapped symptoms
- severity reasons
- app version

Rule hits and symptoms are stored separately so analytics can count symptom trends and rule frequency without parsing nested JSON from the session record.

## dbt Model Design

The dbt project follows a simple layered structure:

```text
sources
  -> staging
  -> intermediate
  -> marts
```

Staging models clean the raw Snowflake tables:

- `stg_triage_sessions`
- `stg_triage_rule_hits`
- `stg_triage_session_symptoms`

Intermediate models prepare session-level records:

- `int_session_latest_decision`

Fact models support Power BI:

- `fct_triage_sessions`
- `fct_triage_rule_hits`
- `fct_session_symptoms`

Aggregate marts include:

- `agg_daily_triage_metrics`
- `agg_symptom_trends`
- `agg_insufficient_information_rate`
- `agg_rule_trigger_frequency`
- `agg_unmapped_symptoms`

Incremental models are used for growing fact tables because sessions, symptoms, and rule hits are append-heavy event-style data.

## Power BI Insights

Power BI should connect to the dbt marts in the `ANALYTICS` schema, not the raw tables.

Useful dashboard pages include:

1. Triage Overview
- sessions by triage level
- daily session volume
- percentage of `SELF_CARE`, `SEE_GP`, and `EMERGENCY`
- trend over time

2. Symptom Trends
- top symptoms
- symptom counts by day
- symptoms associated with emergency outcomes
- symptom combinations that appear often

3. Rule Monitoring
- most frequently triggered rules
- emergency rule frequency
- rule trends over time
- sessions with multiple rule hits

4. Extraction Quality
- insufficient information rate
- top unmapped symptoms
- sessions missing duration, severity, age, or symptoms
- how often follow-up questions are needed

5. Operational Quality
- app version comparison
- extraction behavior after prompt/schema changes
- changes in unmapped symptom rates after vocabulary updates

These insights are useful because they show not only what users report, but also whether the triage flow itself is working well.

## Why This Is Not Disease Prediction

An alternative approach would be to use the provided disease/symptom dataset to predict likely conditions. That was intentionally not chosen for the core system.

Reasons:

- the project goal is triage, not diagnosis
- disease prediction would require stronger clinical validation
- symptom-disease datasets can create a false sense of medical certainty
- a disease model would be harder to explain to users
- deterministic triage rules are easier to test and audit

The dataset can still be useful later for analytics enrichment, such as symptom grouping, educational descriptions, or non-decision support features.

## ML Improvement Opportunities

Machine learning could improve the platform, but it should be introduced carefully.

Good ML extension points:

- symptom synonym mapping and normalization
- detection of unmapped symptom clusters
- predicting which follow-up question is most useful
- identifying sessions likely to need escalation review
- monitoring drift in user symptom language
- clustering sessions for analytics exploration

ML should not replace the deterministic triage decision without a much stronger validation process. A practical next step would be to keep rule-based triage as the source of truth and use ML to improve extraction quality, vocabulary coverage, and analytics.

## Approaches Considered but Not Used

Several approaches were considered but intentionally kept out of v1:

- Disease prediction model: too close to diagnosis and not aligned with the project scope.
- End-to-end LLM triage: flexible, but less deterministic and harder to audit.
- Weighted score from symptom severity CSV: useful for analytics, but too static for safe triage decisions.
- Microservices architecture: unnecessary for an interview-scale project.
- Kafka/event streaming: useful at scale, but overengineering for this version.
- Full clinical ontology integration: valuable later, but too large for the current timeline.
- Per-symptom severity scoring: more detailed, but harder to extract consistently in v1.

The chosen design keeps the system simple, explainable, and realistic for a data/analytics engineering project.

## CI/CD

GitHub Actions runs on pull requests and pushes to `main`.

The CI workflow checks:

- Python dependencies install
- unit tests pass
- Python files compile
- app Docker image builds
- dbt Docker image builds
- dbt project parses

The regular CI job does not require real Snowflake credentials. This keeps pull request checks fast and safe.

Real Snowflake `dbt run` and `dbt test` should be handled through a protected GitHub environment such as `snowflake-dev`, using GitHub Actions secrets.

## Repository Structure

```text
app/
  streamlit_app.py

triage_app/
  app.py
  extractor.py
  models.py
  normalization.py
  pipeline.py
  storage.py
  symptom_vocabulary.py
  triage.py
  validation.py

dbt/
  models/
    staging/
    intermediate/
    marts/

docs/
  snowflake-bootstrap.sql
  snowflake-phase2-migration.sql
  snowflake-setup-checklist.md

tests/
  test_*.py

.github/workflows/
  ci.yml
```

## Local Development

Create a virtual environment and install dependencies:

```bash
pip install -r requirements-dev.txt
```

Create `.env` from `.env.example` and set:

```text
OPENAI_API_KEY=
SNOWFLAKE_ACCOUNT=
SNOWFLAKE_USER=
SNOWFLAKE_PASSWORD=
SNOWFLAKE_WAREHOUSE=TRIAGE_WH
SNOWFLAKE_DATABASE=TRIAGE_PLATFORM
SNOWFLAKE_SCHEMA=ANALYTICS
SNOWFLAKE_RAW_SCHEMA=RAW
SNOWFLAKE_ROLE=TRIAGE_APP_ROLE
```

Run the app locally:

```bash
streamlit run app/streamlit_app.py
```

Or with Docker:

```bash
docker compose up --build app
```

## Snowflake Setup

For a new Snowflake setup, run:

```sql
-- docs/snowflake-bootstrap.sql
```

For an existing v1 setup, run:

```sql
-- docs/snowflake-phase2-migration.sql
```

Then run dbt:

```bash
docker compose run --rm dbt dbt debug --profiles-dir /dbt/profiles
docker compose run --rm dbt dbt run --profiles-dir /dbt/profiles
docker compose run --rm dbt dbt test --profiles-dir /dbt/profiles
```

## Testing

Run:

```bash
pytest -q
python -m compileall triage_app app tests
docker compose run --rm dbt dbt parse --profiles-dir /dbt/profiles
```

## Current Limitations

- Adult-only triage scope.
- Small manually curated symptom vocabulary.
- No clinical validation.
- No production authentication layer.
- No deployed Power BI report included in the repo.
- The rule set is intentionally small and should be expanded carefully.
- The app is designed for demonstration and analytics workflow validation, not real medical use.

## Future Improvements

- Add more symptom aliases and phrase normalization.
- Add follow-up question flow in the UI.
- Add Power BI dashboard templates or screenshots.
- Add a protected GitHub Actions job for Snowflake-backed `dbt run` and `dbt test`.
- Add ML-assisted symptom clustering for unmapped symptoms.
- Add monitoring for extraction drift and rule distribution shifts.
- Add role-based access and stricter audit controls before any public deployment.
