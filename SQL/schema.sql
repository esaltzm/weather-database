DROP TABLE IF EXISTS weather;
CREATE TABLE weather(
    time_start  INT,
    time_stop   INT,
    latitude    NUMERIC(8, 5),
    longitude   NUMERIC(8, 5),
    t           REAL,
    gust        REAL,
    sde         REAL,
    prate       REAL,
    crain       BOOLEAN,
    ltng        BOOLEAN
) ENGINE=MyISAM;


DROP TABLE IF EXISTS weather;
CREATE TABLE weather (
    time_start  INT,
    latitude    NUMERIC(8, 5),
    longitude   NUMERIC(8, 5),
    t           REAL,
    gust        REAL,
    sde         REAL,
    prate       REAL,
    crain       BOOLEAN,
    ltng        BOOLEAN,
    INDEX time_lat (time_start, latitude)
)
ENGINE = MyISAM;

CREATE TABLE weather (
    time_start  INT,
    latitude    NUMERIC(8, 5),
    longitude   NUMERIC(8, 5),
    t           REAL,
    gust        REAL,
    sde         REAL,
    prate       REAL,
    ltng        BOOLEAN
)
ENGINE = MyISAM;

CREATE TABLE time_range (
    earliest    INT,
    latest      INT
);

