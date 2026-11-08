-- Schema from docs/wayfinder/tickets/05 and 16. No vector indexes yet:
-- the learning plan starts with exact search, then adds HNSW and compares.
CREATE EXTENSION IF NOT EXISTS vector;

-- One row per activity. Key = COROS labelId so reloads never duplicate.
CREATE TABLE IF NOT EXISTS activities (
    label_id          bigint PRIMARY KEY,
    sport_type        integer NOT NULL,
    sport_name        text NOT NULL,
    started_at        timestamptz,
    ended_at          timestamptz,
    local_date        date NOT NULL,
    duration_s        integer,
    distance_km       numeric(8, 3),
    avg_pace_s_per_km integer,
    avg_hr            integer,
    calories          integer,
    avg_cadence       integer,
    avg_power         integer,
    elevation_gain_m  integer,
    elevation_loss_m  integer,
    training_load     integer,
    aerobic_te        numeric(3, 1),
    anaerobic_te      numeric(3, 1),
    training_focus    text,
    location_label    text,
    start_lat         double precision,
    start_lon         double precision,
    raw_file          text
);

-- Per-km laps. Distances are stored in km (connector sends centimetres).
CREATE TABLE IF NOT EXISTS laps (
    label_id            bigint NOT NULL REFERENCES activities (label_id) ON DELETE CASCADE,
    lap_index           integer NOT NULL,
    distance_km         numeric(8, 3),
    time_s              numeric(8, 2),
    avg_pace_s_per_km   numeric(8, 2),
    avg_power           integer,
    avg_hr              integer,
    max_hr              integer,
    ground_time_ms      integer,
    avg_cadence         integer,
    max_cadence         integer,
    stride_ratio        integer,
    stride_height       integer,
    avg_stride_length   integer,
    elev_gain_m         numeric(8, 1),
    total_descent_m     numeric(8, 1),
    adjusted_pace       integer,
    PRIMARY KEY (label_id, lap_index)
);

CREATE TABLE IF NOT EXISTS daily_metrics (
    metric_date       date PRIMARY KEY,
    resting_hr        integer,
    hrv_baseline_ms   integer,
    short_term_load   integer,
    long_term_load    integer,
    load_ratio        numeric(4, 2),
    load_comment      text,
    raw_file          text
);

-- Generated summary text and its vector, per activity or per ISO week.
CREATE TABLE IF NOT EXISTS embeddings (
    id          bigserial PRIMARY KEY,
    kind        text NOT NULL CHECK (kind IN ('activity', 'week')),
    label_id    bigint REFERENCES activities (label_id) ON DELETE CASCADE,
    week_start  date,
    content     text NOT NULL,
    model       text NOT NULL,
    embedding   vector(1024) NOT NULL,
    created_at  timestamptz NOT NULL DEFAULT now(),
    CHECK ((kind = 'activity' AND label_id IS NOT NULL AND week_start IS NULL)
        OR (kind = 'week' AND week_start IS NOT NULL AND label_id IS NULL))
);
CREATE UNIQUE INDEX IF NOT EXISTS embeddings_activity_uq ON embeddings (label_id, model) WHERE kind = 'activity';
CREATE UNIQUE INDEX IF NOT EXISTS embeddings_week_uq ON embeddings (week_start, model) WHERE kind = 'week';

-- Paraphrased expert guidance; the owner approves each card before it is usable.
CREATE TABLE IF NOT EXISTS guidance_cards (
    id               bigserial PRIMARY KEY,
    topic            text NOT NULL,
    content          text NOT NULL,
    source_url       text NOT NULL,
    related_metric   text,
    consensus_level  text NOT NULL CHECK (consensus_level IN ('consensus', 'mixed', 'contested')),
    approved_at      timestamptz,
    embedding        vector(1024)
);
