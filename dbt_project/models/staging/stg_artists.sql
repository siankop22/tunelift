select
    artist_id,
    artist_name,
    genre,
    monthly_listeners,
    follower_count

from {{ source('raw', 'artists') }}
