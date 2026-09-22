# TuneLift

**Music Promotion Experimentation & Incrementality Platform**

TuneLift is a product analytics and experimentation platform for measuring whether music promotion actually creates incremental listener engagement.

It simulates a music streaming promotion environment with treatment and control groups and analyzes the impact of promotion on streaming, saves, skips, repeat listening, artist follows, playlist adds, and long-term retention.

## What TuneLift Measures

TuneLift evaluates promotion across several layers:

- Stream conversion
- Absolute and relative lift
- Incremental streams
- Statistical significance
- 95% confidence intervals
- Statistical power
- Minimum detectable effect
- Sample ratio mismatch
- Guardrail metrics
- Listener segmentation
- Campaign-level performance
- 7-day, 14-day, and 30-day retention

## Dashboard

The Streamlit dashboard is organized into separate product analytics views:

- **Overview** — core promotion KPIs and listener response
- **Experiment** — p-values, confidence intervals, power, MDE, and experiment health
- **Guardrails** — skips, saves, repeat listening, artist follows, and playlist adds
- **Retention** — 7/14/30-day listener retention
- **Campaigns** — campaign-level incremental lift
- **Audience** — treatment effects across listener segments
- **Tracks** — promoted-track performance

The interface uses a dark, music-streaming-inspired visual design.

## Architecture


Synthetic Listener Events
          |
          v
      PostgreSQL
          |
          v
      dbt Staging
          |
          v
   dbt Intermediate
          |
          v
    Analytics Marts
          |
          v
 Statistical Analysis
          |
          v
 Streamlit Dashboard
Data Pipeline

Raw PostgreSQL tables:

listeners
artists
tracks
campaigns
experiment_events
retention_events

dbt transforms these into analytics-ready models:

staging
   |
   v
int_listener_campaign_events
   |
   v
fct_promotion_events
fct_campaign_performance
fct_experiment_results

The Streamlit application reads from the dbt analytics layer rather than querying raw operational tables directly.

Experiment Design

Listeners are assigned to:

Treatment — receives the promotional recommendation
Control — receives the standard recommendation experience

TuneLift estimates promotion impact using:

Absolute Lift =
Treatment Conversion Rate - Control Conversion Rate

and:

Incremental Streams =
Absolute Lift × Treatment Impressions

Statistical inference includes a two-proportion z-test and 95% confidence interval.

Experiment Health

TuneLift also evaluates whether an experiment itself is trustworthy.

It measures:

statistical power
minimum detectable effect
treatment/control sample balance
sample ratio mismatch

This helps distinguish a real product result from an unreliable experiment.

Guardrail Metrics

A promotion should not be considered successful simply because streams increase.

TuneLift therefore monitors:

Skip Rate
Save Rate
Repeat Listening
Artist Follow Rate
Playlist Add Rate

These metrics help determine whether promotion produces meaningful listener engagement rather than short-term exposure alone.

Retention

TuneLift measures whether listeners return after their initial promoted stream.

Retention windows include:

7 Day
14 Day
30 Day

This helps distinguish temporary campaign activity from longer-term listener engagement.

Tech Stack

Data Science

Python
Pandas
NumPy
SciPy
Statsmodels
scikit-learn

Analytics Engineering

SQL
dbt
PostgreSQL

Visualization

Streamlit
Plotly

Infrastructure

Docker
Git
pytest
Running Locally

Clone the repository:

git clone <repository-url>
cd tunelift

Create a virtual environment:

python3 -m venv .venv
source .venv/bin/activate

Install dependencies:

pip install -r requirements.txt

Start PostgreSQL:

docker compose up -d

Generate the synthetic experiment data:

python src/generate_data.py
python src/generate_retention.py

Run dbt:

cd dbt_project
dbt run
dbt test
cd ..

Launch the dashboard:

python -m streamlit run dashboard/app.py

Then open:

http://localhost:8501
Testing

Run the Python test suite with:

pytest -v

Run dbt data-quality tests with:

cd dbt_project
dbt test
Data

TuneLift uses fully synthetic listener and campaign data generated locally for demonstration and experimentation purposes.

No Spotify proprietary data is used.

Purpose

TuneLift demonstrates how product data science can combine experimentation, analytics engineering, statistical inference, product metrics, and stakeholder-facing reporting to evaluate the incremental impact of music promotion.
