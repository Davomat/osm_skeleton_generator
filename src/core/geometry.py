import math


# finde the centroid of a polygon --> maybe replace with more accurate function
def centroid(points):
    x, y = zip(*points)
    return sum(x) / len(x), sum(y) / (len(y))


# check if point3 is between point1 and point2 --> should be used for  collinear points only
def in_interval(point1, point2, point3):
    x1 = point1[0]
    y1 = point1[1]
    x2 = point2[0]
    y2 = point2[1]
    x3 = point3[0]
    y3 = point3[1]
    if almost_same_point((x1, y1), (x2, y2)) or almost_same_point((x1, y1), (x3, y3)) or almost_same_point((x2, y2), (
            x3, y3)) :
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


# distance between two points
def distance(point1, point2):
    x1 = point1[0]
    y1 = point1[1]
    x2 = point2[0]
    y2 = point2[1]
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


# find linear equation (y = mx + b)
def get_line(point1, point2):
    x1 = point1[0]
    y1 = point1[1]
    x2 = point2[0]
    y2 = point2[1]
    if almost_same(x1, x2):  # Bei Senkrechten für b stattdessen den gemeinsamen x-Wert speichern
        return None, x1
    m = (y1 - y2) / (x1 - x2)
    b = y1 - m * x1
    return m, b


# find the intersection between two lines (if there is one)
def intersection(m1, m2, b1, b2):
    if m1 is None and m2 is None:
        return None # either no intersection or infinite number of intersections

    if m1 is None:
        x2 = b1
        y2 = m2 * x2 + b2

    elif m2 is None:
        x2 = b2
        y2 = m1 * x2 + b1

    elif almost_same(m1, m2):
        return None

    else:
        x2 = (b2 - b1) / (m1 - m2)
        y2 = m1 * x2 + b1
    return (x2, y2)


# the points in the polygon must be in order!
#           |
# ----------+-----------
#           |   x  <-- this point has only positive coordinates!
#           |

# ---> Gauß's area formula https://en.wikipedia.org/wiki/Shoelace_formula
def anti_clockwise(polygon):
    sum = 0
    x,y = zip(*polygon)
    length = len(polygon)
    index = length - 1
    index_next = 0
    while index_next < length:
        sum += (y[index] + y[index_next]) * (x[index] - x[index_next])
        index = index_next
        index_next += 1
    return sum < 0


# point is also outside the polygon if it is on the line segment between two adjacent points of the polygon
def point_inside_polygon(point, polygon):
    if point in polygon:
        return False
    count = 0
    for polygon_point1, polygon_point2 in zip(polygon, polygon[1:] + polygon[:1]):
        if point_is_on_edge(point,[polygon_point1,polygon_point2]):
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
                intersection_point = intersection(m, 0, b,point[1])
                if intersection_point:
                    if intersection_point[0] > point[0]:
                        if in_interval(polygon_point1, polygon_point2, intersection_point):
                            count = count + 1

    if count % 2 == 1:
        return True
    return False


def point_is_on_edge(point, edge):
    if almost_same_point(point, edge[0]) or almost_same_point(point, edge[1]):
        return True
    m, b = get_line(edge[0], edge[1])
    m_orthogonal, b_orthogonal = get_orthogonal_line(m, point)
    intersection_point = intersection(m, m_orthogonal, b, b_orthogonal)
    if almost_same_point(point, intersection_point):
        return True
    return False


def point_inside_room(point, polygon, barriers):
    for barrier in barriers:
        if point in barrier:
            return False
        if point_inside_polygon(point, barrier):
            return False
    return point_inside_polygon(point, polygon)


def almost_same_point(point1, point2):
    if point1 is None or point2 is None:
        return False
    return almost_same(point1[0], point2[0]) and almost_same(point1[1], point2[1])


def almost_same(value1, value2):
    return math.isclose(value1,value2, abs_tol=0.00000001)


def polygon_intersection(way, polygon):
    for i in range(len(way) - 1):
        m_way_segment, b_way_segment = get_line(way[i], way[i + 1], )
        for polygon_point1, polygon_point2 in zip(polygon, polygon[1:] + polygon[:1]):
            if polygon_point1 != polygon_point2:
                m_polygon_segment, b_polygon_segment = get_line(polygon_point1, polygon_point2)
                intersection_point = intersection(m_polygon_segment, m_way_segment, b_polygon_segment, b_way_segment)

                if intersection_point:
                    if in_interval(polygon_point1, polygon_point2, intersection_point) and \
                            in_interval(way[i], way[i + 1], intersection_point):
                        if not almost_same_point(intersection_point, way[i]) and \
                                not almost_same_point(intersection_point, way[i + 1]):
                                return True

    return False


def way_inside_room(way, polygon, barriers):
    for i in range(len(way) - 1):
        centre = centroid([way[i], way[i + 1]])
        if not point_inside_room(centre, polygon, barriers):
            return False
    for barrier in barriers:
        if polygon_intersection(way, barrier):
            return False
    return not polygon_intersection(way, polygon)


# find an orthogonal line going through the point
def get_orthogonal_line(m, point):
    x = point[0]
    y = point[1]
    if m == 0:
        m2 = None
        b2 = x

    elif m is None:
        m2 = 0
        b2 = y

    else:
        m2 = -1 / m
        b2 = y - m2 * x
    return m2, b2


def add_doors_to_polygon(polygon, all_doors):
    doors = []
    index = 0
    index_prev = len(polygon) -1
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
                        point_distance = distance(intersection_point,
                                                  door)
                        if (point_distance < 0.3 and in_interval(polygon[index_prev], polygon[index], intersection_point)) or almost_same_point(intersection_point,polygon[index] or almost_same_point(intersection_point,polygon[index_prev])):
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


# exclude ways that lead into the corners of the room
def way_is_valid(point1, point2, polygon, doors, barriers):
    if way_inside_room([point1, point2], polygon, barriers):
        if point1 in doors and (point2 in doors or point_inside_room(point2, polygon, barriers)):
            return True
        if point_inside_room(point1, polygon, barriers) and (
                point2 in doors or point_inside_room(point2, polygon, barriers)):
            return True
    return False


#remove every point that lies on the edge between two other points
def simplify_polygon(polygon):
    index = 0
    index_prev = len(polygon) -1
    index_next = 1
    while index_next < len(polygon):
        point = polygon[index]
        point_prev = polygon[index_prev]
        point_next = polygon[index_next]
        if point_is_on_edge(point,[point_prev, point_next]):
            del polygon[index]
            if index == 0:
                index_prev -= 1
        else:
            index_prev = index
            index += 1
            index_next += 1


def simplify_room(polygon,barriers):
    simplify_polygon(polygon)
    for barrier in barriers:
        simplify_polygon(barrier)

def way_intersects_with_way(way,ways):
    m,b = get_line(way[0],way[1])
    for way2 in ways:
        i = 0
        while i < len(way2['way']) -1:
            m2,b2 = get_line(way2['way'][i],way2['way'][i+1])
            intersection_point = intersection(m, m2, b, b2)
            if intersection_point:
                if in_interval(way[0], way[1], intersection_point) and in_interval(way2['way'][i], way2['way'][i + 1], intersection_point):
                    return True
            i += 1
    return False
