# https://stackoverflow.com/a/42602591
import shapefile
from shapely.geometry import Point, Polygon

def get_borders():

    sf = shapefile.Reader('./state_data/cb_2015_us_state_20m-polygon')
    shapes = sf.shapes()
    records = sf.records()
    state_polygons = {}
    for i, record in enumerate(records):
        state = record[5]
        points = shapes[i].points
        poly = Polygon(points)
        state_polygons[state] = poly
    return state_polygons

state_polygons = get_borders()   

def in_us(lat, lon):
    p = Point(lon, lat)
    for state in list(state_polygons.values()):
        if state.contains(p):
            return True
    return False