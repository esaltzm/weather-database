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