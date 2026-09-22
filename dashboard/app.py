import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# =========================================================
# PROJECT SETUP
# =========================================================

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.database import engine
from src.experiment_stats import analyze_binary_experiment
from src.guardrails import analyze_guardrails
from src.retention import (
    calculate_retention,
    calculate_retention_lift,
)
from src.experiment_health import (
    experiment_power,
    minimum_detectable_effect,
    sample_ratio_mismatch,
)

st.set_page_config(
    page_title="TuneLift",
    page_icon="♪",
    layout="wide",
)


# =========================================================
# STYLING
# =========================================================

st.markdown(
    """
    <style>

    /* --------------------------------------------------
       GLOBAL
    -------------------------------------------------- */

    html, body, [class*="css"] {
        font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
    }

    .stApp {
        background:
            radial-gradient(
                circle at 30% 0%,
                rgba(29, 185, 84, 0.12),
                transparent 26%
            ),
            linear-gradient(
                180deg,
                #121212 0%,
                #0a0a0a 100%
            );
        color: #ffffff;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 2rem;
        padding-bottom: 5rem;
        padding-left: 2.2rem;
        padding-right: 2.2rem;
    }

    /* --------------------------------------------------
       SIDEBAR
    -------------------------------------------------- */

    [data-testid="stSidebar"] {
        background: #000000;
        border-right: 1px solid #242424;
    }

    [data-testid="stSidebar"] > div:first-child {
        padding-top: 1.5rem;
    }

    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: #ffffff;
    }

    [data-testid="stSidebar"] label {
        color: #b3b3b3 !important;
        font-weight: 600;
    }

    /* --------------------------------------------------
       HEADINGS
    -------------------------------------------------- */

    h1 {
        color: #ffffff;
        font-weight: 800 !important;
        letter-spacing: -1.5px;
    }

    h2, h3 {
        color: #ffffff;
        font-weight: 750 !important;
        letter-spacing: -0.4px;
    }

    p {
        color: #b3b3b3;
    }

    /* --------------------------------------------------
       HERO
    -------------------------------------------------- */

    .tunelift-hero {
        padding: 30px 32px;
        border-radius: 20px;
        background:
            linear-gradient(
                120deg,
                rgba(29,185,84,0.24),
                rgba(29,185,84,0.04)
            ),
            #181818;
        border: 1px solid #292929;
        margin-bottom: 28px;
        box-shadow: 0px 12px 32px rgba(0,0,0,0.32);
    }

    .tunelift-brand {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 8px;
    }

    .tunelift-icon {
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: #1DB954;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: #000000;
        font-weight: 900;
    }

    .tunelift-title {
        font-size: 38px;
        font-weight: 850;
        color: white;
        letter-spacing: -1.4px;
    }

    .tunelift-subtitle {
        color: #b3b3b3;
        font-size: 16px;
        margin-top: 4px;
    }

    .tunelift-badge {
        display: inline-block;
        margin-top: 18px;
        padding: 6px 12px;
        border-radius: 999px;
        background: rgba(29,185,84,0.14);
        border: 1px solid rgba(29,185,84,0.35);
        color: #1ED760;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
    }

    /* --------------------------------------------------
       KPI / METRIC CARDS
    -------------------------------------------------- */

    [data-testid="stMetric"] {
        background: #181818;
        border: 1px solid #282828;
        border-radius: 14px;
        padding: 18px 18px 16px 18px;
        min-height: 132px;
        transition:
            transform 0.18s ease,
            background 0.18s ease,
            border 0.18s ease;
    }

    [data-testid="stMetric"]:hover {
        background: #202020;
        border-color: #3a3a3a;
        transform: translateY(-2px);
    }

    [data-testid="stMetricLabel"] {
        color: #b3b3b3 !important;
        font-size: 13px !important;
        font-weight: 650 !important;
    }

    [data-testid="stMetricValue"] {
        color: #ffffff !important;
        font-size: 29px !important;
        font-weight: 800 !important;
        letter-spacing: -0.7px;
    }

    [data-testid="stMetricDelta"] {
        color: #1ED760 !important;
        font-weight: 700 !important;
    }

    /* --------------------------------------------------
       TABS
    -------------------------------------------------- */

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #121212;
        padding: 5px;
        border-radius: 12px;
        border: 1px solid #242424;
    }

    .stTabs [data-baseweb="tab"] {
        height: 46px;
        border-radius: 8px;
        padding-left: 22px;
        padding-right: 22px;
        color: #b3b3b3;
        font-weight: 700;
        background: transparent;
    }

    .stTabs [aria-selected="true"] {
        background: #282828 !important;
        color: #ffffff !important;
    }

    .stTabs [data-baseweb="tab-highlight"] {
        background-color: #1DB954 !important;
    }

    /* --------------------------------------------------
       EXPANDERS
    -------------------------------------------------- */

    [data-testid="stExpander"] {
        background: #181818;
        border: 1px solid #282828;
        border-radius: 14px;
        overflow: hidden;
    }

    [data-testid="stExpander"] summary {
        font-weight: 700;
        color: #ffffff;
    }

    /* --------------------------------------------------
       INPUTS
    -------------------------------------------------- */

    div[data-baseweb="select"] > div {
        background: #242424 !important;
        border-color: #343434 !important;
        color: #ffffff !important;
    }

    [data-baseweb="tag"] {
        background-color: #1DB954 !important;
        color: #000000 !important;
        font-weight: 700;
    }

    /* --------------------------------------------------
       DATAFRAMES
    -------------------------------------------------- */

    [data-testid="stDataFrame"] {
        border: 1px solid #282828;
        border-radius: 14px;
        overflow: hidden;
    }

    /* --------------------------------------------------
       ALERTS
    -------------------------------------------------- */

    [data-testid="stAlert"] {
        background: rgba(29,185,84,0.08);
        border: 1px solid rgba(29,185,84,0.24);
        border-radius: 12px;
    }

    /* --------------------------------------------------
       DIVIDERS
    -------------------------------------------------- */

    hr {
        border-color: #282828 !important;
    }

    /* --------------------------------------------------
       HIDE STREAMLIT CHROME
    -------------------------------------------------- */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# DATA
# =========================================================

@st.cache_data
def load_data():
    query = """
    SELECT *
    FROM analytics.fct_promotion_events
    """

    return pd.read_sql(query, engine)


df = load_data()

# =========================================================
# HEADER
# =========================================================

st.title("TuneLift")
st.caption("Music Promotion Experimentation & Incrementality Platform")
st.markdown("---")

# =========================================================
# SIDEBAR FILTERS
# =========================================================

st.sidebar.header("Filters")

campaigns = sorted(df["campaign_id"].unique().tolist())
genres = sorted(df["track_genre"].dropna().unique().tolist())
countries = sorted(df["country"].dropna().unique().tolist())
subscriptions = sorted(
    df["subscription_type"].dropna().unique().tolist()
)

selected_campaigns = st.sidebar.multiselect(
    "Campaign",
    campaigns,
    default=campaigns,
)

selected_genres = st.sidebar.multiselect(
    "Track Genre",
    genres,
    default=genres,
)

selected_countries = st.sidebar.multiselect(
    "Listener Country",
    countries,
    default=countries,
)

selected_subscriptions = st.sidebar.multiselect(
    "Subscription Type",
    subscriptions,
    default=subscriptions,
)

filtered_df = df[
    df["campaign_id"].isin(selected_campaigns)
    & df["track_genre"].isin(selected_genres)
    & df["country"].isin(selected_countries)
    & df["subscription_type"].isin(selected_subscriptions)
].copy()

if filtered_df.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

# =========================================================
# EXPERIMENT METRICS
# =========================================================

treatment = filtered_df[
    filtered_df["treatment_group"] == "treatment"
]

control = filtered_df[
    filtered_df["treatment_group"] == "control"
]

treatment_rate = (
    treatment["streamed"].mean()
    if len(treatment) > 0
    else 0
)

control_rate = (
    control["streamed"].mean()
    if len(control) > 0
    else 0
)

absolute_lift = treatment_rate - control_rate

relative_lift = (
    absolute_lift / control_rate
    if control_rate > 0
    else 0
)

incremental_streams = (
    absolute_lift * len(treatment)
)

experiment_stats = analyze_binary_experiment(
    treatment_successes=int(treatment["streamed"].sum()),
    treatment_n=len(treatment),
    control_successes=int(control["streamed"].sum()),
    control_n=len(control),
)

srm_result = sample_ratio_mismatch(
    treatment_n=len(treatment),
    control_n=len(control),
)

achieved_power = experiment_power(
    treatment_rate=treatment_rate,
    control_rate=control_rate,
    treatment_n=len(treatment),
    control_n=len(control),
)

mde = minimum_detectable_effect(
    baseline_rate=control_rate,
    n_per_group=min(
        len(treatment),
        len(control),
    ),
)


guardrail_results = analyze_guardrails(
    filtered_df
)

retention_df = calculate_retention(
    filtered_df
)

retention_lift_df = calculate_retention_lift(
    filtered_df
)

# =========================================================
# CHART THEME
# =========================================================

SPOTIFY_GREEN = "#1DB954"
SPOTIFY_GREEN_LIGHT = "#1ED760"
SPOTIFY_GRAY = "#B3B3B3"
SPOTIFY_CARD = "#181818"


def style_chart(fig):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="#181818",
        font=dict(
            family="Inter, Arial, sans-serif",
            color="#B3B3B3",
        ),
        title_font=dict(
            color="#FFFFFF",
        ),
        legend_title_font=dict(
            color="#FFFFFF",
        ),
        margin=dict(
            l=20,
            r=20,
            t=35,
            b=20,
        ),
    )

    fig.update_xaxes(
        gridcolor="#282828",
        linecolor="#282828",
    )

    fig.update_yaxes(
        gridcolor="#282828",
        linecolor="#282828",
    )

    return fig



# =========================================================
# DASHBOARD TABS
# =========================================================

tab_overview, tab_experiment, tab_guardrails, tab_retention, tab_campaigns, tab_audience, tab_tracks = st.tabs(
    [
        "Overview",
        "Experiment",
        "Guardrails",
        "Retention",
        "Campaigns",
        "Audience",
        "Tracks",
    ]
)

# =========================================================
# OVERVIEW TAB
# =========================================================

with tab_overview:

    st.subheader("Promotion Overview")

    st.caption(
        "High-level performance of the selected music promotion experiments."
    )

    k1, k2, k3, k4, k5, k6 = st.columns(6)

    k1.metric(
        "Total Impressions",
        f"{len(filtered_df):,}",
    )

    k2.metric(
        "Treatment Stream Rate",
        f"{treatment_rate:.1%}",
    )

    k3.metric(
        "Control Stream Rate",
        f"{control_rate:.1%}",
    )

    k4.metric(
        "Absolute Lift",
        f"{absolute_lift:.1%}",
    )

    k5.metric(
        "Relative Lift",
        f"{relative_lift:.1%}",
    )

    k6.metric(
        "Incremental Streams",
        f"{incremental_streams:,.0f}",
    )

    with st.expander(
        "How to Read These Metrics",
        expanded=False,
    ):

        st.markdown(
            """
**Treatment** listeners received the promotional experience.

**Control** listeners received the normal recommendation experience.

Comparing the two groups helps estimate the incremental impact of promotion.
"""
        )

        g1, g2, g3 = st.columns(3)

        with g1:
            st.markdown(
                """
#### Total Impressions

The number of times songs were shown during the experiment.

#### Treatment Stream Rate

The percentage of treatment impressions that resulted in a stream.
"""
            )

        with g2:
            st.markdown(
                """
#### Control Stream Rate

The stream rate without the promotional treatment.

#### Absolute Lift

The direct difference between treatment and control.

Example:

`27.2% - 20.7% = 6.5 percentage points`
"""
            )

        with g3:
            st.markdown(
                """
#### Relative Lift

The percentage improvement compared with the control baseline.

#### Incremental Streams

Estimated additional streams associated with promotion.

`Absolute Lift × Treatment Impressions`
"""
            )

    st.markdown("### Listener Response")

    summary = (
        filtered_df
        .groupby("treatment_group")
        .agg(
            stream_rate=("streamed", "mean"),
            save_rate=("saved", "mean"),
            repeat_rate=("repeat_stream", "mean"),
            follow_rate=("followed_artist", "mean"),
            skip_rate=("skipped", "mean"),
            playlist_add_rate=("playlist_add", "mean"),
        )
        .reset_index()
    )

    summary_long = summary.melt(
        id_vars="treatment_group",
        var_name="metric",
        value_name="rate",
    )

    summary_long["metric"] = (
        summary_long["metric"]
        .str.replace("_", " ")
        .str.title()
    )

    fig_overview = px.bar(
        summary_long,
        x="metric",
        y="rate",
        color="treatment_group",
        barmode="group",
        labels={
            "metric": "",
            "rate": "Rate",
            "treatment_group": "Group",
        },
    )

    fig_overview.update_yaxes(
        tickformat=".0%"
    )

    style_chart(fig_overview)

    st.plotly_chart(
        fig_overview,
        use_container_width=True,
    )


# =========================================================
# EXPERIMENT TAB
# =========================================================

with tab_experiment:

    st.subheader("Experiment Readout")

    st.caption(
        "Statistical evidence for whether promotion changed stream conversion."
    )

    e1, e2, e3, e4 = st.columns(4)

    e1.metric(
        "Sample Size",
        f"{experiment_stats['total_n']:,}",
    )

    e2.metric(
        "P-value",
        f"{experiment_stats['p_value']:.4f}",
    )

    e3.metric(
        "95% Confidence Interval",
        (
            f"{experiment_stats['ci_lower']:.1%} "
            f"to {experiment_stats['ci_upper']:.1%}"
        ),
    )

    e4.metric(
        "Statistical Result",
        (
            "Significant"
            if experiment_stats["significant"]
            else "Not Significant"
        ),
    )

    if experiment_stats["significant"]:
        st.success(
            "The treatment and control stream rates are statistically "
            "different at the 5% significance level."
        )
    else:
        st.warning(
            "The current experiment does not provide enough statistical "
            "evidence to distinguish the observed difference from random variation."
        )

    st.markdown("### Experiment Health")

    h1, h2, h3 = st.columns(3)

    h1.metric(
        "Statistical Power",
        f"{achieved_power:.0%}",
    )

    h2.metric(
        "Minimum Detectable Effect",
        f"{mde:.1%}",
    )

    h3.metric(
        "Randomization Check",
        (
            "Review"
            if srm_result["has_srm"]
            else "Healthy"
        ),
    )

    with st.expander(
        "Understanding the statistics",
        expanded=False,
    ):
        st.markdown(
            f"""
#### P-value

Measures how surprising the observed difference would be if promotion had
no real effect.

A common threshold is **0.05**.

Current p-value:

`{experiment_stats['p_value']:.4f}`

---

#### 95% Confidence Interval

A plausible range for the true treatment effect.

Current estimate:

`{experiment_stats['ci_lower']:.2%} to {experiment_stats['ci_upper']:.2%}`

---

#### Statistical Power

The probability of detecting an effect of this size when one exists.

Current power:

`{achieved_power:.1%}`

---

#### Minimum Detectable Effect

The approximate smallest effect this experiment can reliably detect.

Current MDE:

`{mde:.2%}`

---

#### Randomization Check

Checks whether traffic was distributed between treatment and control roughly
as expected.

SRM p-value:

`{srm_result['p_value']:.4f}`
"""
        )


# =========================================================
# GUARDRAILS TAB
# =========================================================

with tab_guardrails:

    st.subheader("Guardrail Metrics")

    st.caption(
        "Check whether higher streaming comes at the expense of listener "
        "satisfaction or deeper engagement."
    )

    guardrail_rows = []

    for metric_name, result in guardrail_results.items():

        if metric_name == "Skip Rate":
            better = result["absolute_change"] < 0
        else:
            better = result["absolute_change"] > 0

        if result["absolute_change"] == 0:
            direction = "No Change"
        elif better:
            direction = "Better"
        else:
            direction = "Worse"

        guardrail_rows.append(
            {
                "Metric": metric_name,
                "Treatment": result["treatment_rate"],
                "Control": result["control_rate"],
                "Change": result["absolute_change"],
                "P-value": result["p_value"],
                "Significant": (
                    "Yes"
                    if result["significant"]
                    else "No"
                ),
                "Direction": direction,
            }
        )

    guardrail_df = pd.DataFrame(
        guardrail_rows
    )

    st.dataframe(
        guardrail_df.style.format(
            {
                "Treatment": "{:.2%}",
                "Control": "{:.2%}",
                "Change": "{:+.2%}",
                "P-value": "{:.4f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    skip_result = guardrail_results[
        "Skip Rate"
    ]

    positive_engagement = [
        guardrail_results["Save Rate"],
        guardrail_results["Repeat Listening"],
        guardrail_results["Artist Follow Rate"],
        guardrail_results["Playlist Add Rate"],
    ]

    harmful_skip_change = (
        skip_result["significant"]
        and skip_result["absolute_change"] > 0
    )

    harmful_engagement_changes = any(
        result["significant"]
        and result["absolute_change"] < 0
        for result in positive_engagement
    )

    if (
        not harmful_skip_change
        and not harmful_engagement_changes
    ):
        st.success(
            "No statistically significant guardrail deterioration "
            "was detected."
        )
    else:
        st.warning(
            "At least one guardrail shows statistically significant "
            "deterioration."
        )

    with st.expander(
        "What are guardrail metrics?",
        expanded=False,
    ):
        st.markdown(
            """
**Skip Rate** — lower is generally better.

**Save Rate** — shows stronger interest than a stream alone.

**Repeat Listening** — indicates listeners came back to the song.

**Artist Follow Rate** — connects promotion with audience growth.

**Playlist Add Rate** — indicates intent to listen again later.

A strong experiment should improve its primary metric without causing
meaningful deterioration in these supporting metrics.
"""
        )


# =========================================================
# RETENTION TAB
# =========================================================

with tab_retention:

    st.subheader("Listener Retention")

    st.caption(
        "Do listeners acquired through promotion continue engaging after "
        "their initial stream?"
    )

    retention_chart = px.line(
        retention_df,
        x="period",
        y="retention_rate",
        color="treatment_group",
        markers=True,
        category_orders={
            "period": [
                "7 Day",
                "14 Day",
                "30 Day",
            ]
        },
        labels={
            "period": "Retention Window",
            "retention_rate": "Retention Rate",
            "treatment_group": "Group",
        },
    )

    retention_chart.update_yaxes(
        tickformat=".0%"
    )

    style_chart(retention_chart)

    st.plotly_chart(
        retention_chart,
        use_container_width=True,
    )

    st.markdown("### Retention Lift")

    st.dataframe(
        retention_lift_df.style.format(
            {
                "treatment": "{:.2%}",
                "control": "{:.2%}",
                "absolute_lift": "{:+.2%}",
                "relative_lift": "{:+.2%}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

    with st.expander(
        "How to interpret retention",
        expanded=False,
    ):
        st.markdown(
            """
**7-Day Retention**

Whether listeners returned during the first week.

**14-Day Retention**

Whether engagement continued beyond the initial promotional period.

**30-Day Retention**

A stronger signal of longer-term listener interest.

Retention helps distinguish temporary promotional activity from lasting
listener engagement.
"""
        )


# =========================================================
# CAMPAIGNS TAB
# =========================================================

with tab_campaigns:

    st.subheader("Campaign Performance")

    campaign_rates = (
        filtered_df
        .groupby(
            [
                "campaign_id",
                "treatment_group",
            ]
        )["streamed"]
        .mean()
        .unstack()
        .reset_index()
    )

    if (
        "treatment" in campaign_rates.columns
        and "control" in campaign_rates.columns
    ):

        campaign_rates[
            "absolute_lift"
        ] = (
            campaign_rates["treatment"]
            - campaign_rates["control"]
        )

        campaign_rates[
            "relative_lift"
        ] = (
            campaign_rates["absolute_lift"]
            / campaign_rates[
                "control"
            ].replace(0, pd.NA)
        )

        campaign_rates = (
            campaign_rates
            .sort_values(
                "absolute_lift",
                ascending=False,
            )
        )

        fig_campaign = px.bar(
            campaign_rates,
            x="campaign_id",
            y="absolute_lift",
            labels={
                "campaign_id": "Campaign",
                "absolute_lift": "Absolute Stream Lift",
            },
        )

        fig_campaign.update_yaxes(
            tickformat=".1%"
        )

        style_chart(fig_campaign)

        st.plotly_chart(
            fig_campaign,
            use_container_width=True,
        )

        st.dataframe(
            campaign_rates.style.format(
                {
                    "treatment": "{:.2%}",
                    "control": "{:.2%}",
                    "absolute_lift": "{:+.2%}",
                    "relative_lift": "{:+.2%}",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# AUDIENCE TAB
# =========================================================

with tab_audience:

    st.subheader("Audience Insights")

    st.caption(
        "Identify listener groups where music promotion has the largest impact."
    )

    segment_label = st.selectbox(
        "Analyze promotion lift by",
        [
            "Preferred Genre",
            "Country",
            "Subscription Type",
            "Genre Match",
            "Age Group",
            "Listener Activity",
        ],
    )

    segment_mapping = {
        "Preferred Genre": "preferred_genre",
        "Country": "country",
        "Subscription Type": "subscription_type",
        "Genre Match": "genre_match",
        "Age Group": "age_group",
        "Listener Activity": "listener_activity",
    }

    segment = segment_mapping[
        segment_label
    ]

    segment_rates = (
        filtered_df
        .groupby(
            [
                segment,
                "treatment_group",
            ]
        )["streamed"]
        .mean()
        .unstack()
        .reset_index()
    )

    if (
        "treatment" in segment_rates.columns
        and "control" in segment_rates.columns
    ):

        segment_rates[
            "absolute_lift"
        ] = (
            segment_rates["treatment"]
            - segment_rates["control"]
        )

        segment_rates = (
            segment_rates
            .sort_values(
                "absolute_lift",
                ascending=False,
            )
        )

        fig_segment = px.bar(
            segment_rates,
            x=segment,
            y="absolute_lift",
            labels={
                segment: segment_label,
                "absolute_lift": "Absolute Stream Lift",
            },
        )

        fig_segment.update_yaxes(
            tickformat=".1%"
        )

        style_chart(fig_segment)

        st.plotly_chart(
            fig_segment,
            use_container_width=True,
        )

        st.dataframe(
            segment_rates.style.format(
                {
                    "treatment": "{:.2%}",
                    "control": "{:.2%}",
                    "absolute_lift": "{:+.2%}",
                }
            ),
            use_container_width=True,
            hide_index=True,
        )


# =========================================================
# TRACKS TAB
# =========================================================

with tab_tracks:

    st.subheader("Promoted Track Performance")

    st.caption(
        "Compare reach and downstream listener engagement for promoted tracks."
    )

    track_summary = (
        filtered_df
        .groupby(
            [
                "track_id",
                "track_name",
                "artist_name",
                "track_genre",
            ]
        )
        .agg(
            impressions=(
                "impression_id",
                "count",
            ),
            streams=(
                "streamed",
                "sum",
            ),
            saves=(
                "saved",
                "sum",
            ),
            repeats=(
                "repeat_stream",
                "sum",
            ),
            follows=(
                "followed_artist",
                "sum",
            ),
            playlist_adds=(
                "playlist_add",
                "sum",
            ),
        )
        .reset_index()
    )

    track_summary[
        "stream_rate"
    ] = (
        track_summary["streams"]
        / track_summary["impressions"]
    )

    track_summary = (
        track_summary
        .sort_values(
            "stream_rate",
            ascending=False,
        )
    )

    st.dataframe(
        track_summary.style.format(
            {
                "stream_rate": "{:.2%}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# FOOTER
# =========================================================

st.markdown("---")

st.caption(
    "TuneLift · Music Promotion Experimentation & Incrementality Platform · "
    "Synthetic listener data"
)
