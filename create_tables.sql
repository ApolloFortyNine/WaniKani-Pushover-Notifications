create table account (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    wk_api_key TEXT,
    pushover_api_key TEXT
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