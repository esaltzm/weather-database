CREATE TABLE weathertable(
    id          SERIAL PRIMARY KEY,
    time_start  TIMESTAMP,
    time_stop   TIMESTAMP,
    latitude    NUMERIC(9),
    longitude   NUMERIC(9),
    t           NUMERIC(4),
    vis         INT,
    gust        NUMERIC(4),
    sde         NUMERIC(4),
    prate       NUMERIC(4),
    crain       BOOLEAN,
    ltng        BOOLEAN
);