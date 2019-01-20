create table account (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    wk_api_key TEXT,
    pushover_user_key TEXT,
    username TEXT,
    last_alert_ts TEXT,
    alert_count INTEGER,
    joined_ts TEXT,
    active INTEGER,
    alert_type TEXT
);

create table wk_subject (
    id INTEGER PRIMARY KEY NOT NULL,
    subject_level INTEGER,
    subject_object text
);

create table wk_subject_info (
    id INTEGER PRIMARY KEY NOT NULL,
    cache_string text
);