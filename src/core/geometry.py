import math
from typing import Union

from core.osm_classes.debug import debugprint

from core.osm_classes.Point import Point
from core.osm_classes.Line import Line
from core.osm_classes.Polygon import Polygon
from core.osm_classes.Edge import Edge


import core.tolerances as tolerances


def centroid(points: list[Point]) -> Point:
    """
    Finds the centroid of a polygon.
    """



    x = []
    y = []
    for p in points:
        x.append(p.x)
        y.append(p.y)
    return Point(sum(x) / len(x), sum(y) / len(y))


def in_interval(point1: Point, point2: Point, point3: Point) -> bool:
    """
    Checks whether point3 is between point_a and point_b.
    Should only be used for collinear points.
    """

    x1 = point1.x
    y1 = point1.y
    x2 = point2.x
    y2 = point2.y
    x3 = point3.x
    y3 = point3.y
    if Point.almost_same_point(Point(x1, y1), Point(x2, y2)) \
            or Point.almost_same_point(Point(x1, y1), Point(x3, y3)) \
            or Point.almost_same_point(Point(x2, y2), Point(x3, y3)):
        return False
    if x1 < x2:
        if x3 < x1 or x3 > x2:
            return False
    if x1 > x2:
        if x3 > x1 or x3 < x2:
            return False
    if y1 < y2:
        if y3 < y1 or y3 > y2:
            return False
    elif y1 > y2:
        if y3 > y1 or y3 < y2:
            return False

    return True


def distance(point1: Point, point2: Point) -> float:
    """
    Calculates the distance between two 2-dimensional points.
    """

    x1 = point1.x
    y1 = point1.y
    x2 = point2.x
    y2 = point2.y
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def get_line(point1: Point, point2: Point) -> Line:
    """
    Finds the values of the linear equation (y = mx + n) for 2 given points.
    """    

    x1 = point1.x
    y1 = point1.y
    x2 = point2.x
    y2 = point2.y
    if Edge.almost_same(x1, x2):  # Bei Senkrechten für b stattdessen den gemeinsamen x-Wert speichern
        return Line(None, x1)
    m = (y1 - y2) / (x1 - x2)
    n = y1 - m * x1
    return Line(m, n)


# the points in the polygon must be in order!
#           |
# ----------+-----------
#           |   x  <-- this point has only positive coordinates!
#           |

# ---> Gauß's area formula https://en.wikipedia.org/wiki/Shoelace_formula
def anti_clockwise(polygon: Polygon) -> bool:
    """
    Checks if a polygon (list of points) is given in an anticlockwise order.
    """

    result = 0
    x = y = []
    for point in polygon.points:
        x.append(point.x)
        y.append(point.y)
    length = len(polygon.points)
    index = length - 1
    index_next = 0
    while index_next < length:
        result += (y[index] + y[index_next]) * (x[index] - x[index_next])
        index = index_next
        index_next += 1
    return result < 0


def point_inside_polygon(point: Point, polygon: list[Point],
                         tolerance: float = tolerances.general_mapping_uncertainty) -> bool:
    """
    Checks if a point is inside a polygon (list of points).

    The point is also outside the polygon if it is on the line segment between two adjacent points of the polygon.
    """
    for point in polygon.points:
        debugprint(point)
    debugprint("========")
    if point in polygon.points:
        return False
    
    count = 0
    for polygon_point_a, polygon_point_b in wzip(polygon, polygon[1:] + polygon[:1]):
        debugprint(polygon_point_a)
        debugprint(polygon_point_b)
        if point_is_on_edge(point, Edge(polygon_point_a, polygon_point_b), tolerance):
            return False
        if polygon_point_a[0] >= point[0] or polygon_point_b[0] >= point[0]:
            if almost_same(point[1], polygon_point_a[1]):
                if polygon_point_a[1] < polygon_point_b[1]:
                    count += 1
            if almost_same(point[1], polygon_point_b[1]):
                if polygon_point_a[1] > polygon_point_b[1]:
                    count += 1
            else:
                m, n = get_line(polygon_point_a, polygon_point_b)
                # intersection with a horizontal line through the point
                intersection_point = intersection(m, 0, n, point[1])
                if intersection_point:
                    if intersection_point[0] > point[0]:
                        if in_interval(polygon_point_a, polygon_point_b, intersection_point):
                            count = count + 1

    return count % 2 == 1


def point_is_on_edge(point: Point,
                     edge: Edge,
                     tolerance: float = tolerances.general_mapping_uncertainty) -> bool:
    """
    Checks whether a point is on an edge (on the connection line between the two edge points).
    """
    if almost_same_point(point, edge.Point1) or almost_same_point(point, edge.Point2):
        return True
    debugprint("EdgePoint1: " + str(edge.Point1))
    debugprint("EdgePoint2: " + str(edge.Point2))
    tmpL = get_line(edge.Point1, edge.Point2)
    m, b = tmpL.m, tmpL.n
    m_orthogonal, b_orthogonal = get_orthogonal_line(m, point)
    intersection_point = intersection(m, m_orthogonal, b, b_orthogonal)
    if almost_same_point(point, intersection_point, tolerance) \
            and min(edge.Point1.x, edge.Point2.x) <= intersection_point.x <= max(edge.Point1.x, edge.Point2.x) \
            and min(edge.Point1.y, edge.Point2.y) <= intersection_point.y <= max(edge.Point1.y, edge.Point2.y):
        return True
    return False


def point_inside_room(point: Point, polygon: Polygon,
                      barriers: list[Polygon]) -> bool:
    """
    Checks whether a point is inside a room (polygon with barriers).
    """
    for barrier in barriers:
        if point in barrier.points:
            return False
        if point_inside_polygon(point, barrier):
            return False
    return point_inside_polygon(point, polygon)





def polygon_intersection(way: Polygon, polygon: Polygon) -> bool:
    """
    Checks whether a specific way crosses a part of a polygon.
    """
    for i in range(len(way.points) - 1):
        m_way_segment, n_way_segment = get_line(way.points[i], way.points[i + 1], )
        for polygon_point1, polygon_point2 in wzip(polygon, polygon.points[1:] + polygon.points[:1]):
            if polygon_point1 != polygon_point2:
                m_polygon_segment, n_polygon_segment = get_line(polygon_point1, polygon_point2)
                intersection_point = intersection(m_polygon_segment, m_way_segment, n_polygon_segment, n_way_segment)

                if intersection_point:
                    if in_interval(polygon_point1, polygon_point2, intersection_point) and \
                            in_interval(way[i], way[i + 1], intersection_point):
                        if not almost_same_point(intersection_point, way[i]) and \
                                not almost_same_point(intersection_point, way[i + 1]):
                            return True
    return False


def way_inside_room(way: Polygon, polygon: Polygon,
                    barriers: list[Polygon]) -> bool:
    """
    Checks whether a way is completely inside a room without intersections.
    """
    for i in range(len(way.points) - 1):
        centre = centroid(Polygon([way.points[i], way.points[i + 1]]))
        if not point_inside_room(centre, polygon, barriers):
            return False
    for barrier in barriers:
        if polygon_intersection(way.points, barrier.points):
            return False
    return not polygon_intersection(way.points, polygon.points)


def polygon_inside_polygon(potential_inner_polygon: Polygon,
                           potential_outer_polygon: Polygon,
                           tolerance: float = tolerances.general_mapping_uncertainty,
                           use_centroids: bool = False) -> bool:
    """
    Checks whether all points of a potential inner polygon are inside or on the edge of a potential outer polygon.

    If the check should be complete, checks whether the centroids of every three adjacent points of the barrier are
    inside the potential outer polygon.
    """
    if use_centroids:
        points = potential_inner_polygon[:] + potential_inner_polygon[:2]
        centroids = [centroid(points[i:i+3]) for i in range(len(potential_inner_polygon))]
        centroids_inside = 0
        for c in centroids:
            if point_inside_polygon(c, potential_outer_polygon, tolerance):
                centroids_inside += 1
        return centroids_inside / len(centroids) >= 1 - tolerances.ratio_barrier_in_barrier
    else:
        for point in potential_inner_polygon.points:
            if not point_inside_polygon(point, potential_outer_polygon, tolerance):
                return False
    return True


def get_orthogonal_line(m: Union[float, None], point: Point) -> Union[tuple[float, float], tuple[None, float]]:
    """
    Calculates an orthogonal line going through the given point.
    """
    x = point.x
    y = point.y
    if m == 0:
        m2 = None
        n2 = x
    elif m is None:
        m2 = 0
        n2 = y
    else:
        m2 = -1 / m
        n2 = y - m2 * x
    return m2, n2


def add_doors_to_polygon(polygon: Polygon, all_doors: list[Point]) -> list[Point]:
    """
    Inserts the door points into the polygon.
    """
    doors = []
    index = 0
    index_prev = len(polygon.points) - 1
    change = True
    while change:
        change = False
        while index < len(polygon.points):
            added_door = False
            tmpL = get_line(polygon[index_prev], polygon[index])
            m, b = tmpL.m, tmpL.n 
            for door in all_doors:
                if door not in doors:
                    if door in polygon:
                        doors.append(door)
                    else:
                        m2, b2 = get_orthogonal_line(m, door)
                        intersection_point = Edge.intersection(m, m2, b, b2)
                        point_distance = distance(intersection_point, door)
                        if (point_distance < tolerances.door_to_room and
                            in_interval(polygon[index_prev], polygon[index], intersection_point)) \
                                or Edge.almost_same_point(intersection_point, polygon[index] or
                                                     Edge.almost_same_point(intersection_point, polygon[index_prev])):
                            polygon.insert(index, door)
                            doors.append(door)
                            change = True
                            added_door = True
                            if index == 0:
                                index_prev += 1
            if not added_door:
                index_prev = index
                index += 1

    return doors


def way_is_valid(point1: Point, point2: Point, polygon: Polygon,
                 doors: list[Point], barriers: list[Polygon]) -> bool:
    """
    Checks whether a way is inside a room and does not collide .

    Excludes ways that lead into the corners of the room.
    """
    if way_inside_room(Polygon([point1, point2]), polygon, barriers):
        if point1 in doors and (point2 in doors or point_inside_room(point2, polygon, barriers)):
            return True
        if point_inside_room(point1, polygon, barriers) and (
                point2 in doors or point_inside_room(point2, polygon, barriers)):
            return True
    return False


def way_intersects_with_way(way: list[tuple[float, float]],
                            ways: list[dict[str, Union[list[tuple[float, float]], str]]]) -> bool:

    """
    list[
        dict[
            str, 
            Union[
                list[
                    tuple[
                            float, 
                            float
                        ]
                    ],
                     str
                ]
            ]
        ]
    """

    """
    Checks whether a specific way crosses another way.
    """
    m, n = get_line(way[0], way[1])
    for way2 in ways:
        for i in range(len(way2['way']) - 1):
            m2, n2 = get_line(way2['way'][i], way2['way'][i + 1])
            intersection_point = intersection(m, m2, n, n2)
            if intersection_point:
                if in_interval(way[0], way[1], intersection_point) \
                        and in_interval(way2['way'][i], way2['way'][i + 1], intersection_point):
                    return True
    return False
