import sys

from point import Point
from shape import Shape
from blessings import Terminal
import os
from bresenham import bresenham
import numpy as np
import time
import math
from itertools import permutations

height = 0
width = 0
num_shapes = 0
shapes = []
left_margin = 10
top_margin = 2
my_map = []
routing = []
point_stop = []
dx = [0, 1, -1, 0]
dy = [1, 0, 0, -1]


def read_input_file(input_file_name, start_point, end_point, h, w, n_shapes, shapes_array):
    input_file = open(input_file_name, "r")

    # Read the size of map
    line1 = input_file.readline().rstrip("\n").split(",")
    w = int(line1[0])
    h = int(line1[1])

    # Read the start point and end point
    line2 = input_file.readline().rstrip("\n").split(",")
    start_point.x = int(line2[0])
    start_point.y = int(line2[1])
    end_point.x = int(line2[2])
    end_point.y = int(line2[3])

    i = 4
    while i < len(line2):
        x = int(line2[i])
        y = int(line2[i+1])
        i = i + 2
        point_stop.append(Point(x, y))

    # Read the shapes count
    n_shapes = int(input_file.readline())

    # Read all lines and define the shapes
    tokens = input_file.readlines()
    shapes_array = []

    for line in tokens:
        coors = line.split(",")
        points = []

        for idx in range(0, len(coors) - 1, 2):
            p = Point(0, 0)
            p.x = int(coors[idx])
            p.y = int(coors[idx + 1])
            points.append(p)

        # Create a shape and append to us array
        shape = Shape(points)
        shapes_array.append(shape)

    return start_point, end_point, h, w, n_shapes, shapes_array


def draw_map(t):
    for i in range(height + 1):
        row = []
        for j in range(width + 1):
            with t.location(left_margin + j, top_margin + i):
                print(" ", end='')
            row.append(0)

        my_map.append(row)


def draw_border(t):
    for i in range(height + 1):
        for j in range(width + 1):
            if i == 0 or i == height:
                with t.location(left_margin + j, top_margin + i):
                    print(u'\u2550', end='')
            elif j == 0 or j == width:
                with t.location(left_margin + j, top_margin + i):
                    print(u'\u2551', end='')

    with t.location(left_margin, top_margin):
        print(u'\u2554', end='')
    with t.location(left_margin + width, top_margin + height):
        print(u'\u255d', end='')
    with t.location(left_margin, top_margin + height):
        print(u'\u255a', end='')
    with t.location(left_margin + width, top_margin):
        print(u'\u2557', end='')


def draw_shapes(t):
    for i in range(num_shapes):
        for j in range(len(shapes[i].points) - 1):
            draw_route(t, shapes[i].points[j], shapes[i].points[j + 1], height)
        draw_route(t, shapes[i].points[len(shapes[i].points) - 1], shapes[i].points[0], height)


def draw_route(t, a, b, h):
    points_list = bresenham(a.x, a.y, b.x, b.y)

    for point in points_list:
        with t.location(left_margin + point[0], top_margin + h - point[1]):
            print(t.yellow(u'\u2588'), end='')
        my_map[point[1]][point[0]] = 1


def draw_start_end_points(t):
    with t.location(left_margin + start.x, top_margin + height - start.y):
        print(t.bold_red_on_bright_green("S"), end='')
        my_map[start.y][start.x] = "2"
    with t.location(left_margin + end.x, top_margin + height - end.y):
        print(t.bold_red_on_bright_green("G"), end='')
        my_map[end.y][end.x] = "3"


def draw_stop_points(t):
    for point in point_stop:
        with t.location(left_margin + point.x, top_margin + height - point.y):
            print(t.bold_red_on_bright_blue("P"), end='')
            my_map[point.y][point.x] = "4"


def draw_routing(t):
    for i in range(1, len(routing) - 1):
        time.sleep(0.05)
        point = routing[i]
        with t.location(left_margin + point.x, top_margin + height - point.y):
            print('+')


def dfs_recursive(flag, x, y):
    flag[y][x] = 1
    routing.append(Point(x, y))

    if x == end.x and y == end.y:
        return True

    for i in range(4):
        xx = x + dx[i]
        yy = y + dy[i]
        # return false if out the bound
        if xx < 1 or yy < 1 or xx > width - 1 or yy > height - 1:
            continue
        # return false if checked or crash the shape
        if flag[yy][xx] == 1 or my_map[yy][xx] == 1:
            continue

        if dfs_recursive(flag, xx, yy):
            return True

    # flag[y][x] = 0
    del routing[-1]
    return False


def dfs():
    flag = np.zeros((height + 1, width + 1))
    return dfs_recursive(flag, start.x, start.y)


def distance(x1, y1, x2, y2):
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)


def manhattan(x1, y1, x2, y2):
    return abs(x1 - x2) + abs(y1 - y2)


class Heuristic:
    def __init__(self, index, heuristic):
        self.index = index
        self.heuristic = heuristic

    def __lt__(self, other):
        return self.heuristic < other.heuristic


def greedy_recursive(flag, x, y):
    flag[y][x] = 1
    routing.append(Point(x, y))

    if x == end.x and y == end.y:
        return True

    heu = []
    for i in range(4):
        heu.append(Heuristic(i, -1))
        xx = x + dx[i]
        yy = y + dy[i]
        # return false if out the bound
        if xx < 1 or yy < 1 or xx > width - 1 or yy > height - 1:
            continue
        # return false if checked or crash the shape
        if flag[yy][xx] == 1 or my_map[yy][xx] == 1:
            continue
        heu[i].heuristic = manhattan(xx, yy, end.x, end.y)

    heu = [x for x in heu if x.heuristic != -1]
    heu.sort()

    while len(heu) != 0:
        xx = x + dx[heu[0].index]
        yy = y + dy[heu[0].index]
        if greedy_recursive(flag, xx, yy):
            return True
        heu.pop(0)

    # flag[y][x] = 0
    del routing[-1]
    return False


def greedy():
    flag = np.zeros((height + 1, width + 1))
    return greedy_recursive(flag, start.x, start.y)


def bfs():
    flag = np.zeros((height + 1, width + 1))
    flag[start.y][start.x] = 1
    tracking = [[Point(-1, -1) for x in range(width + 1)] for y in range(height + 1)]

    queue = [start]
    found = False
    while len(queue) != 0 and not found:
        open_node = queue.pop(0)
        for i in range(4):
            xx = open_node.x + dx[i]
            yy = open_node.y + dy[i]
            # return false if out the bound
            if xx < 1 or yy < 1 or xx > width - 1 or yy > height - 1:
                continue
            # return false if checked or crash the shape
            if flag[yy][xx] == 1 or my_map[yy][xx] == 1:
                continue

            queue.append(Point(xx, yy))
            tracking[yy][xx] = Point(open_node.x, open_node.y)
            flag[yy][xx] = 1
            if xx == end.x and yy == end.y:
                found = True
                break

    if tracking[end.y][end.x] == Point(-1, -1):
        return False

    # routing by using 'tracking'
    temp = end
    while temp != start:
        routing.append(temp)
        temp = tracking[temp.y][temp.x]

    routing.append(start)
    routing.reverse()
    return True


class Node_AS:
    def __init__(self, point, g, h):
        self.point = point
        self.g = g
        self.h = h

    def __lt__(self, other):
        return self.g + self.h < other.g + other.h


def a_star():
    flag = np.zeros((height + 1, width + 1))
    flag[start.y][start.x] = 1
    tracking = [[Point(-1, -1) for x in range(width + 1)] for y in range(height + 1)]

    g = 0
    h = manhattan(start.x, start.y, end.x, end.y)
    queue = [Node_AS(start, g, h)]
    found = False
    while len(queue) != 0 and not found:
        open_node = queue.pop(0)
        for i in range(4):
            xx = open_node.point.x + dx[i]
            yy = open_node.point.y + dy[i]
            # return false if out the bound
            if xx < 1 or yy < 1 or xx > width - 1 or yy > height - 1:
                continue
            # return false if checked or crash the shape
            if flag[yy][xx] == 1 or my_map[yy][xx] == 1:
                continue

            # calculate current cost and heuristic
            g = open_node.g + 1
            h = manhattan(xx, yy, end.x, end.y)
            new_node = Node_AS(Point(xx, yy), g, h)
            queue.append(new_node)
            queue.sort()

            tracking[yy][xx] = Point(open_node.point.x, open_node.point.y)
            flag[yy][xx] = 1

            # return true if open end point
            if xx == end.x and yy == end.y:
                found = True
                break

    if tracking[end.y][end.x] == Point(-1, -1):
        return False

    # routing by using 'tracking'
    temp = end
    while temp != start:
        routing.append(temp)
        temp = tracking[temp.y][temp.x]

    routing.append(start)
    routing.reverse()
    return True


if __name__ == "__main__":
    term = Terminal()
    os.system('cls' if os.name == 'nt' else 'clear')

    start = Point(0, 0)
    end = Point(0, 0)
    start, end, height, width, num_shapes, shapes = read_input_file("input.txt", start, end, height, width, num_shapes,
                                                                    shapes)

    print("Input selection (from 1 to 5): ")
    selection = int(input())

    os.system('cls' if os.name == 'nt' else 'clear')
    draw_map(term)
    draw_border(term)
    draw_shapes(term)
    draw_start_end_points(term)

    if selection == 1:  # algorithm 1
        routing = []
        if dfs():
            draw_routing(term)
        else:
            print("Routing not found!")
    elif selection == 2:  # algorithm 2
        routing = []
        if greedy():
            draw_routing(term)
        else:
            print("Routing not found!")
    elif selection == 3:  # algorithm 3
        routing = []
        if bfs():
            draw_routing(term)
        else:
            print("Routing not found!")
    elif selection == 4:  # algorithm 4
        routing = []
        if a_star():
            draw_routing(term)
        else:
            print("Routing not found!")
    elif selection == 5:  # level 3
        draw_stop_points(term)

        # generate all possible route (brute force)
        perm = list(permutations(range(len(point_stop))))

        min_routing = []
        min_cost = width * height
        save_start = start
        save_end = end
        for i in range(len(perm)):
            big_routing = []

            start = save_start
            end = point_stop[perm[i][0]]
            routing = []
            if not a_star():  # find route from 2 point using a-star
                print("Routing not found!")
                sys.exit()
            big_routing.append(routing)

            length = len(perm[i])
            for j in range(length - 1):
                start = point_stop[perm[i][j]]
                end = point_stop[perm[i][j + 1]]
                routing = []
                if not a_star():  # find route from 2 point using a-star
                    print("Routing not found!")
                    sys.exit()
                big_routing.append(routing)

            start = point_stop[perm[i][length - 1]]
            end = save_end
            routing = []
            if not a_star():  # find route from 2 point using a-star
                print("Routing not found!")
                sys.exit()
            big_routing.append(routing)

            cost = 0  # calculate total cost
            for c in big_routing:
                cost = cost + len(c)

            if cost < min_cost:
                min_cost = cost
                min_routing = big_routing

        for i in min_routing:
            routing = i
            draw_routing(term)
