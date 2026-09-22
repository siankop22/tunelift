SELECT
    campaign_id,
    treatment_group,

    COUNT(*) AS impressions,

    SUM(streamed) AS streams,
    SUM(saved) AS saves,
    SUM(skipped) AS skips,
    SUM(followed_artist) AS follows,
    SUM(repeat_stream) AS repeat_streams,
    SUM(playlist_add) AS playlist_adds,

    ROUND(
        AVG(streamed)::numeric,
        4
    ) AS stream_rate,

    ROUND(
        AVG(saved)::numeric,
        4
    ) AS save_rate,

    ROUND(
        AVG(skipped)::numeric,
        4
    ) AS skip_rate,

    ROUND(
        AVG(followed_artist)::numeric,
        4
    ) AS follow_rate,

    ROUND(
        AVG(repeat_stream)::numeric,
        4
    ) AS repeat_rate

FROM experiment_events

GROUP BY
    campaign_id,
    treatment_group

ORDER BY
    campaign_id,
    treatment_group;
