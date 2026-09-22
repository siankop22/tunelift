select
    impression_id,
    campaign_id,
    listener_id,
    track_id,

    treatment_group,
    genre_match,

    streamed,
    skipped,
    saved,
    followed_artist,
    repeat_stream,
    playlist_add,

    country,
    age,

    case
        when age < 25 then '18-24'
        when age < 35 then '25-34'
        when age < 45 then '35-44'
        else '45+'
    end as age_group,

    subscription_type,
    preferred_genre,
    historical_stream_count,

    case
        when historical_stream_count < 100 then 'Light'
        when historical_stream_count < 300 then 'Medium'
        else 'Heavy'
    end as listener_activity,

    track_name,
    track_genre,
    popularity_score,

    artist_name,
    monthly_listeners,
    follower_count,

    campaign_budget,
    start_date,
    end_date

from {{ ref('int_listener_campaign_events') }}
