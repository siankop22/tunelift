select
    campaign_id,
    treatment_group,

    count(*) as impressions,

    sum(streamed) as streams,
    sum(saved) as saves,
    sum(skipped) as skips,
    sum(followed_artist) as artist_follows,
    sum(repeat_stream) as repeat_streams,
    sum(playlist_add) as playlist_adds,

    avg(streamed::numeric) as stream_rate,
    avg(saved::numeric) as save_rate,
    avg(skipped::numeric) as skip_rate,
    avg(followed_artist::numeric) as follow_rate,
    avg(repeat_stream::numeric) as repeat_rate,
    avg(playlist_add::numeric) as playlist_add_rate

from {{ ref('int_listener_campaign_events') }}

group by
    campaign_id,
    treatment_group
