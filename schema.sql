CREATE TABLE weather(
    id          SERIAL PRIMARY KEY,
    time_start  INT,
    time_stop   INT,
    latitude    NUMERIC(8, 5),
    longitude   NUMERIC(8, 5),
    t           NUMERIC(4, 2),
    vis         INT,
    gust        NUMERIC(4, 2),
    sde         NUMERIC(4, 2),
    prate       NUMERIC(4, 2),
    crain       BOOLEAN,
    ltng        BOOLEAN
);