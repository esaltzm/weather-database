SELECT latitude, longitude, (point(42.37645700595458, -71.14287029443811) <@> point(latitude, longitude)) AS distance FROM weather ORDER BY (point(42.37645700595458, -71.14287029443811) <@> point(latitude, longitude)) LIMIT 1;
-- closest point and distance to cambridge, ma

SELECT latitude, longitude, (point(45.37480404362509, -121.69541539938172) <@> point(latitude, longitude)) AS distance FROM weather ORDER BY (point(45.37480404362509, -121.69541539938172) <@> point(latitude, longitude)) LIMIT 1;
-- closest point and distance to mount hood, or

SELECT latitude, longitude, (point(34.00816825128189, -118.49835404405773) <@> point(latitude, longitude)) AS distance FROM weather ORDER BY (point(34.00816825128189, -118.49835404405773) <@> point(latitude, longitude)) LIMIT 1;
-- closest point and distance to santa monica, ca

SELECT latitude, longitude, (point(25.68582930398322, -91.73386607114072) <@> point(latitude, longitude)) AS distance FROM weather ORDER BY (point(25.68582930398322, -91.73386607114072) <@> point(latitude, longitude)) LIMIT 1;
-- closest point and distance to point in gulf of mexico off texas coast

SELECT latitude, longitude, (point(64.13620359306964, -21.949299246522425) <@> point(latitude, longitude)) AS distance FROM weather ORDER BY (point(64.13620359306964, -21.949299246522425) <@> point(latitude, longitude)) LIMIT 1;
-- closest point and distance to reykjavík, iceland

SELECT latitude, longitude, (point(19.720375600306227, -155.08219780324657) <@> point(latitude, longitude)) AS distance FROM weather ORDER BY (point(19.720375600306227, -155.08219780324657) <@> point(latitude, longitude)) LIMIT 1;
-- closest point and distance to hilo, hawaii