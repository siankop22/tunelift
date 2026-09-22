select
    listener_id,
    country,
    age,
    subscription_type,
    preferred_genre,
    historical_stream_count

from {{ source('raw', 'listeners') }}
