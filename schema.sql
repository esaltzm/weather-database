CREATE TABLE weather(
    time_start  INT,
    time_stop   INT,
    latitude    NUMERIC(8, 5),
    longitude   NUMERIC(8, 5),
    t           REAL,
    gust        REAL,
    sde         REAL,
    prate       REAL,
    crain       BIT,
    ltng        BIT
);