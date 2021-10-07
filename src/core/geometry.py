import math
from typing import Union


def centroid(points: list[tuple[float, float]]) -> tuple[float, float]:
    """
    Finds the centroid of a polygon.

    TODO: maybe replace with more accurate function
    """
    x, y = zip(*points)
    return sum(x) / len(x), sum(y) / (len(y))


def in_interval(point1: tuple[float, float], point2: tuple[float, float], point3: tuple[float, float]) -> bool:
    """
    Checks whether point3 is between point1 and point2.
    Should only be used for collinear points.
    """
    x1 = point1[0]
    y1 = point1[1]
    x2 = point2[0]
    y2 = point2[1]
    x3 = point3[0]
    y3 = point3[1]
    if almost_same_point((x1, y1), (x2, y2)) \
            or almost_same_point((x1, y1), (x3, y3)) \
            or almost_same_point((x2, y2), (x3, y3)):
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


def distance(point1: tuple[float, float], point2: tuple[float, float]) -> float:
    """
    Calculates the distance between two 2-dimensional points.
    """
    x1 = point1[0]
    y1 = point1[1]
    x2 = point2[0]
    y2 = point2[1]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def get_line(point1: tuple[float, float], point2: tuple[float, float]) -> Union[tuple[float, float],
                                                                                tuple[None, float]]:
    """
    Finds the values of the linear equation (y = mx + n) for 2 given points.
    """
    x1 = point1[0]
    y1 = point1[1]
    x2 = point2[0]
    y2 = point2[1]
    if almost_same(x1, x2):  # Bei Senkrechten für b stattdessen den gemeinsamen x-Wert speichern
        return None, x1
    m = (y1 - y2) / (x1 - x2)
    n = y1 - m * x1
    return m, n


def intersection(m1: float, m2: float, n1: float, n2: float) -> Union[None, tuple[float, float]]:
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
    return x2, y2


# the points in the polygon must be in order!
#           |
# ----------+-----------
#           |   x  <-- this point has only positive coordinates!
#           |

# ---> Gauß's area formula https://en.wikipedia.org/wiki/Shoelace_formula
def anti_clockwise(polygon: list[tuple[float, float]]) -> bool:
    """
    Checks if a polygon (list of points) is given in an anticlockwise order.
    """
    result = 0
    x, y = zip(*polygon)
    length = len(polygon)
    index = length - 1
    index_next = 0
    while index_next < length:
        result += (y[index] + y[index_next]) * (x[index] - x[index_next])
        index = index_next
        index_next += 1
    return result < 0


def point_inside_polygon(point: tuple[float, float], polygon: list[tuple[float, float]]) -> bool:
    """
    Checks if a point is inside a polygon (list of points).

    The point is also outside the polygon if it is on the line segment between two adjacent points of the polygon.
    """
    if point in polygon:
        return False
    count = 0
    for polygon_point1, polygon_point2 in zip(polygon, polygon[1:] + polygon[:1]):
        if point_is_on_edge(point, [polygon_point1, polygon_point2]):
            return False
        if polygon_point1[0] >= point[0] or polygon_point2[0] >= point[0]:
            if almost_same(point[1], polygon_point1[1]):
                if polygon_point1[1] < polygon_point2[1]:
                    count += 1
            if almost_same(point[1], polygon_point2[1]):
                if polygon_point1[1] > polygon_point2[1]:
                    count += 1
            else:
                m, b = get_line(polygon_point1, polygon_point2)
                # intersection with a horizontal line through the point
                intersection_point = intersection(m, 0, b, point[1])
                if intersection_point:
                    if intersection_point[0] > point[0]:
                        if in_interval(polygon_point1, polygon_point2, intersection_point):
                            count = count + 1

    if count % 2 == 1:
        return True
    return False


def point_is_on_edge(point: tuple[float, float], edge: list[tuple[float, float]]) -> bool:
    """
    Checks whether a point is on an edge.
    """
    if almost_same_point(point, edge[0]) or almost_same_point(point, edge[1]):
        return True
    m, b = get_line(edge[0], edge[1])
    m_orthogonal, b_orthogonal = get_orthogonal_line(m, point)
    intersection_point = intersection(m, m_orthogonal, b, b_orthogonal)
    if almost_same_point(point, intersection_point):
        return True
    return False


def point_inside_room(point: tuple[float, float], polygon: list[tuple[float, float]],
                      barriers: list[list[tuple[float, float]]]) -> bool:
    """
    Checks whether a point is inside a room (polygon with barriers).
    """
    for barrier in barriers:
        if point in barrier:
            return False
        if point_inside_polygon(point, barrier):
            return False
    return point_inside_polygon(point, polygon)


def almost_same_point(point1: tuple[float, float], point2: tuple[float, float]) -> bool:
    """
    Checks whether 2 points have almost the same coordinates
    """
    if point1 is None or point2 is None:
        return False
    return almost_same(point1[0], point2[0]) and almost_same(point1[1], point2[1])


def almost_same(value1: float, value2: float) -> bool:
    """
    Checks whether 2 values are in the same range within a specific tolerance.
    """
    return math.isclose(value1, value2, abs_tol=0.00000001)


def polygon_intersection(way: list[tuple[float, float]], polygon: list[tuple[float, float]]) -> bool:
    """
    Checks whether a specific way crosses a part of a polygon.
    """
    for i in range(len(way) - 1):
        m_way_segment, n_way_segment = get_line(way[i], way[i + 1], )
        for polygon_point1, polygon_point2 in zip(polygon, polygon[1:] + polygon[:1]):
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


def way_inside_room(way: list[tuple[float, float]], polygon: list[tuple[float, float]],
                    barriers: list[list[tuple[float, float]]]) -> bool:
    """
    Checks whether a way is completely inside a room without intersections.
    """
    for i in range(len(way) - 1):
        centre = centroid([way[i], way[i + 1]])
        if not point_inside_room(centre, polygon, barriers):
            return False
    for barrier in barriers:
        if polygon_intersection(way, barrier):
            return False
    return not polygon_intersection(way, polygon)


def get_orthogonal_line(m: Union[float, None], point: tuple[float, float]) -> Union[tuple[float, float],
                                                                                    tuple[None, float]]:
    """
    Calculates an orthogonal line going through the given point.
    """
    x = point[0]
    y = point[1]
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


def add_doors_to_polygon(polygon: list[tuple[float, float]], all_doors: list[tuple[float, float]]) \
        -> list[tuple[float, float]]:
    """
    Inserts the door points into the polygon.
    """
    doors = []
    index = 0
    index_prev = len(polygon) - 1
    change = True
    while change:
        change = False
        while index < len(polygon):
            added_door = False
            m, b = get_line(polygon[index_prev], polygon[index])
            for door in all_doors:
                if door not in doors:
                    if door in polygon:
                        doors.append(door)
                    else:
                        m2, b2 = get_orthogonal_line(m, door)
                        intersection_point = intersection(m, m2, b, b2)
                        point_distance = distance(intersection_point, door)
                        if (point_distance < 0.3 and
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


def way_is_valid(point1: tuple[float, float], point2: tuple[float, float], polygon: list[tuple[float, float]],
                 doors: list[tuple[float, float]], barriers: list[list[tuple[float, float]]]) -> bool:
    """
    Checks whether a way is inside a room and does not collide .

    Excludes ways that lead into the corners of the room.
    """
    if way_inside_room([point1, point2], polygon, barriers):
        if point1 in doors and (point2 in doors or point_inside_room(point2, polygon, barriers)):
            return True
        if point_inside_room(point1, polygon, barriers) and (
                point2 in doors or point_inside_room(point2, polygon, barriers)):
            return True
    return False


def simplify_polygon(polygon: list[tuple[float, float]]):
    """
    Removes every point that lies on the edge between two other points.
    """
    index = 0
    index_prev = len(polygon) - 1
    index_next = 1
    while index_next < len(polygon):
        point = polygon[index]
        point_prev = polygon[index_prev]
        point_next = polygon[index_next]
        if point_is_on_edge(point, [point_prev, point_next]):
            del polygon[index]
            if index == 0:
                index_prev -= 1
        else:
            index_prev = index
            index += 1
            index_next += 1


def simplify_room(polygon: list[tuple[float, float]], barriers: list[list[tuple[float, float]]]):
    """
    Removes every point that lies on the edge between two other points.
    """
    simplify_polygon(polygon)
    for barrier in barriers:
        simplify_polygon(barrier)


def way_intersects_with_way(way: list[tuple[float, float]],
                            ways: list[dict[str, Union[list[tuple[float, float]], str]]]) -> bool:
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
