(SELECT latitude, longitude, (point(42.37645700595458, -71.14287029443811) <@> point(latitude, longitude)) AS distance, 'cambridge, ma' AS "from" FROM weather ORDER BY distance LIMIT 1)
-- closest point and distance to cambridge, ma
UNION ALL

(SELECT latitude, longitude, (point(45.37480404362509, -121.69541539938172) <@> point(latitude, longitude)) AS distance, 'mount hood, or' AS "from" FROM weather ORDER BY distance LIMIT 1)
-- closest point and distance to mount hood, or
UNION ALL

(SELECT latitude, longitude, (point(34.00816825128189, -118.49835404405773) <@> point(latitude, longitude)) AS distance, 'santa monica, ca' AS "from" FROM weather ORDER BY distance LIMIT 1)
-- closest point and distance to santa monica, ca
UNION ALL

(SELECT latitude, longitude, (point(25.68582930398322, -91.73386607114072) <@> point(latitude, longitude)) AS distance, 'gulf of mexico' AS "from" FROM weather ORDER BY distance LIMIT 1)
-- closest point and distance to point in gulf of mexico off texas coast
UNION ALL

(SELECT latitude, longitude, (point(64.13620359306964, -21.949299246522425) <@> point(latitude, longitude)) AS distance, 'reykjavík, iceland' AS "from" FROM weather ORDER BY distance LIMIT 1)
-- closest point and distance to reykjavík, iceland
UNION ALL

(SELECT latitude, longitude, (point(19.720375600306227, -155.08219780324657) <@> point(latitude, longitude)) AS distance, 'hilo, hawaii' AS "from" FROM weather ORDER BY distance LIMIT 1)
-- closest point and distance to hilo, hawaii
UNION ALL

(SELECT latitude, longitude, (point(57.05223939873137, -135.32788472043092) <@> point(latitude, longitude)) AS distance, 'sitka, alaska' AS "from" FROM weather ORDER BY distance LIMIT 1);
-- closest point to sitka, alaska



SELECT pg_size_pretty( pg_database_size('weather') );
-- db size in mb

SELECT 
    table_name AS `Table`, 
    round(((data_length + index_length) / 1024 / 1024 / 1000), 2) `Size in GB` 
FROM information_schema.TABLES 
WHERE table_schema = "weather_db"
    AND table_name = "weather";
-- db size in mb (mariadb)

CREATE INDEX time_lat ON weather (time_stop, latitude);
DROP INDEX time_lat ON weather; 

SELECT * FROM weather WHERE latitude > 37 AND latitude < 41 AND longitude > -109 AND longitude < -102 AND time_start = 1641762000;

SELECT UNIQUE time_start FROM weather ORDER BY time_start;
select * from weatherindex where prate > 0 order by t asc limit 10;

--index size in gb
SELECT weather, (data_length + index_length)/1073741824 AS size_gb
FROM information_schema.tables
WHERE table_schema = 'weather_db' AND table_name = 'my_table';

CREATE INDEX time ON weather (time_start);

CREATE INDEX lat_long ON weather (latitude, longitude);

DROP INDEX time ON weather;

alter table weather add index 'time_long_lat' (time_start, longitude, latitude);

CREATE INDEX time_long_lat ON weather (time_start, longitude, latitude),
ALGORITHM=INPLACE,
LOCK=NONE;

alter table weather add index time_long_lat (time_start, longitude, latitude),
ALGORITHM=INPLACE,
LOCK=NONE;


ALTER TABLE weather MODIFY sde FLOAT;
ALTER TABLE weather MODIFY prate FLOAT;
ALTER TABLE weather MODIFY gust FLOAT;
ALTER TABLE weather MODIFY t FLOAT;

SELECT DATA_TYPE from INFORMATION_SCHEMA. COLUMNS where table_schema = 'weather_db' and table_name = 'weather';

aws rds modify-db-instance \
    --db-instance-identifier weather-db \
    --allocated-storage 25 \
    --apply-immediately

SELECT table_name,Engine,table_rows,round(((data_length) / 1024 / 1024 / 1000), 2) AS data_size_gb,round(((index_length) / 1024 / 1024 / 1000), 2) AS index_size_gb, round(((data_length + index_length) / 1024 / 1024 / 1000), 2) AS total_size_gb FROM information_schema.tables
WHERE table_schema = DATABASE();