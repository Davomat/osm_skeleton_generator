import math
from typing import Union
# from core.osm_classes import Point, Line, Polygon, Edge, Way, Barrier

from core.osm_classes.Point import Point
from core.osm_classes.Line import Line
from core.osm_classes.Polygon import Polygon
from core.osm_classes.Edge import Edge
from core.osm_classes.Barrier import Barrier

import core.tolerances as tolerances


def centroid(points: list[Point]) -> Point:
    """
    Finds the centroid of a polygon.
    """

    # !! Extrem dreckiger code, der entfernt werden sollte, wenn alle Klassen konvertiert sind
    # convert Polygon to list[Point] if it isnt already
    if not isinstance(points[0], Point):
        print("Converting tupel to Point")
        new_polygon = []
        for p in points:
            new_polygon.append(Point(p[0], p[1]))
        points = new_polygon


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

    # !! Extrem dreckiger code, der entfernt werden sollte, wenn alle Klassen konvertiert sind
    # convert Polygon to list[Point] if it isnt already
    if not isinstance(point1, Point):
        print("get_line konvertiert tupel zu Point")
        point1 = Point(point1[0], point1[1])
    if not isinstance(point2, Point):
        point2 = Point(point2[0], point2[1])
    if not isinstance(point3, Point):
        point3 = Point(point3[0], point3[1])

    x1 = point1.x
    y1 = point1.y
    x2 = point2.x
    y2 = point2.y
    x3 = point3.x
    y3 = point3.y
    if almost_same_point(Point(x1, y1), Point(x2, y2)) \
            or almost_same_point(Point(x1, y1), Point(x3, y3)) \
            or almost_same_point(Point(x2, y2), Point(x3, y3)):
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
     # !! Extrem dreckiger code, der entfernt werden sollte, wenn alle Klassen konvertiert sind
    # convert Polygon to list[Point] if it isnt already
    if not isinstance(point1, Point):
        print("distance() konvertiert tupel zu Point")
        point1 = Point(point1[0], point1[1])
    if not isinstance(point2, Point):
        point2 = Point(point2[0], point2[1])   


    x1 = point1.x
    y1 = point1.y
    x2 = point2.x
    y2 = point2.y
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def get_line(point1: Point, point2: Point) -> Line: #TODO: Was zum fick!?
    """
    Finds the values of the linear equation (y = mx + n) for 2 given points.
    """

    # !! Extrem dreckiger code, der entfernt werden sollte, wenn alle Klassen konvertiert sind
    # convert Polygon to list[Point] if it isnt already
    if not isinstance(point1, Point):
        print("get_line konvertiert tupel zu Point")
        point1 = Point(point1[0], point1[1])
    if not isinstance(point2, Point):
        point2 = Point(point2[0], point2[1])
    


    x1 = point1.x
    y1 = point1.y
    x2 = point2.x
    y2 = point2.y
    if almost_same(x1, x2):  # Bei Senkrechten für b stattdessen den gemeinsamen x-Wert speichern
        return Line(None, x1)
    m = (y1 - y2) / (x1 - x2)
    n = y1 - m * x1
    return Line(m, n)


def intersection(m1: float, m2: float, n1: float, n2: float) -> Union[None, Point]:
    """
    Finds the intersection between two lines (if there is exactly one) given with y = mx + n.
    """
    if m1 is None and m2 is None:
        return None  # either no intersection or infinite number of intersections

    if m1 is None:
        x2 = n1
        y2 = m2 * x2 + n2

    elif m2 is None:
        x2 = n2
        y2 = m1 * x2 + n1

    elif almost_same(m1, m2):
        return None

    else:
        x2 = (n2 - n1) / (m1 - m2)
        y2 = m1 * x2 + n1
    return Point(x2, y2)


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
        print(point)
    print("========")
    if point in polygon.points:
        return False
    
    count = 0
    for polygon_point_a, polygon_point_b in wzip(polygon, polygon[1:] + polygon[:1]):
        print(polygon_point_a)
        print(polygon_point_b)
         # todo: Wie zum fick bekomme ich da die ZIP-Funktion raus!?
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


def point_is_on_edge(point: Point, ## TODO: Weiteres ersetzen 
                     edge: Edge,
                     tolerance: float = tolerances.general_mapping_uncertainty) -> bool:
    """
    Checks whether a point is on an edge (on the connection line between the two edge points).
    """
    if almost_same_point(point, edge.Point1) or almost_same_point(point, edge.Point2):
        return True
    print("EdgePoint1: " + str(edge.Point1))
    print("EdgePoint2: " + str(edge.Point2))
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
                      barriers: list[Barrier]) -> bool:
    """
    Checks whether a point is inside a room (polygon with barriers).
    """
    for barrier in barriers:
        if point in barrier.polygon:
            return False
        if point_inside_polygon(point, barrier.polygon):
            return False
    return point_inside_polygon(point, polygon)


def almost_same_point(point_a: Point, point_b: Point,
                      tolerance: float = tolerances.general_mapping_uncertainty) -> bool:
    """
    Checks whether 2 points have almost the same coordinates
    """
    # Wir sind hier noch nicht fertig!

    # check if the points are of class Point or tuple
    # if tuple, convert to Point
    if not isinstance(point_a, Point):
        point_a = Point(point_a[0], point_a[1])
    if not isinstance(point_b, Point):
        point_b = Point(point_b[0], point_b[1])


    if point_a is None or point_b is None:
        return False
    return almost_same(point_a.x, point_b.x, tolerance) and almost_same(point_a.y, point_b.y, tolerance)


def almost_same(value1: float, value2: float, tolerance: float = tolerances.general_mapping_uncertainty) -> bool:
    """
    Checks whether 2 values are in the same range within a specific tolerance.
    """
    return math.isclose(value1, value2, abs_tol=tolerance)


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
                    barriers: list[Barrier]) -> bool:
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
                        intersection_point = intersection(m, m2, b, b2)
                        point_distance = distance(intersection_point, door)
                        if (point_distance < tolerances.door_to_room and
                            in_interval(polygon[index_prev], polygon[index], intersection_point)) \
                                or almost_same_point(intersection_point, polygon[index] or
                                                     almost_same_point(intersection_point, polygon[index_prev])):
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
                 doors: list[Point], barriers: list[Barrier]) -> bool:
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


def simplify_polygon(polygon: Polygon):
    # Diese Funktion sollte nicht mehr benutzt werden!
    # Stattdessen sollte die Funktion simplify_polygon aus der Klasse Polygon verwendet werden.
    """
    Removes every point that lies on the edge between two other points.
    """
    index = 0
    index_prev = len(polygon.points) - 1
    index_next = 1
    while index_next < len(polygon.points):
        point = polygon.points[index]
        print(polygon.points[index])
        point_prev = polygon.points[index_prev]
        point_next = polygon.points[index_next]
        if point_is_on_edge(point, Edge(point_prev, point_next)):
            del polygon.points[index]
            if index == 0:
                index_prev -= 1
        else:
            index_prev = index
            index += 1
            index_next += 1


def way_intersects_with_way(way: list[tuple[float, float]],
                            ways: list[dict[str, Union[list[tuple[float, float]], str]]]) -> bool:
    # TODO: Was genau macht diese Funktion?
    # Warum ist der zweite Parameter "wayS" und was macht das Union dort?

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
