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
    playlist_add

from {{ source('raw', 'experiment_events') }}
