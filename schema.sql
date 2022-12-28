CREATE TABLE weather(
    id          SERIAL PRIMARY KEY,
    time_start  INT,
    time_stop   INT,
    latitude    NUMERIC(8),
    longitude   NUMERIC(8),
    t           NUMERIC(4),
    vis         INT,
    gust        NUMERIC(4),
    sde         NUMERIC(4),
    prate       NUMERIC(4),
    crain       BOOLEAN,
    ltng        BOOLEAN
);