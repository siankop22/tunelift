select
    impression_id,
    campaign_id,
    listener_id,
    track_id,
    treatment_group,
    returned_7d,
    returned_14d,
    returned_30d

from {{ source('raw', 'retention_events') }}
