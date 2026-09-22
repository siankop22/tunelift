select
    track_id,
    artist_id,
    track_name,
    genre as track_genre,
    release_date,
    popularity_score

from {{ source('raw', 'tracks') }}
