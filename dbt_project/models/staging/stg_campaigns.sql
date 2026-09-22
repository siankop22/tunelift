select
    campaign_id,
    track_id,
    artist_id,
    start_date,
    end_date,
    campaign_budget,
    target_genre

from {{ source('raw', 'campaigns') }}
