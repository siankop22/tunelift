select
    e.impression_id,
    e.campaign_id,
    e.listener_id,
    e.track_id,

    e.treatment_group,
    e.genre_match,

    e.streamed,
    e.skipped,
    e.saved,
    e.followed_artist,
    e.repeat_stream,
    e.playlist_add,

    coalesce(r.returned_7d, 0) as returned_7d,
    coalesce(r.returned_14d, 0) as returned_14d,
    coalesce(r.returned_30d, 0) as returned_30d,

    l.country,
    l.age,
    l.subscription_type,
    l.preferred_genre,
    l.historical_stream_count,

    t.track_name,
    t.track_genre,
    t.popularity_score,

    a.artist_name,
    a.monthly_listeners,
    a.follower_count,

    c.campaign_budget,
    c.start_date,
    c.end_date

from {{ ref('stg_experiment_events') }} e

left join {{ ref('stg_retention_events') }} r
    on e.impression_id = r.impression_id

left join {{ ref('stg_listeners') }} l
    on e.listener_id = l.listener_id

left join {{ ref('stg_tracks') }} t
    on e.track_id = t.track_id

left join {{ ref('stg_artists') }} a
    on t.artist_id = a.artist_id

left join {{ ref('stg_campaigns') }} c
    on e.campaign_id = c.campaign_id
