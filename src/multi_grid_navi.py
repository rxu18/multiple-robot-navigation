'''
    @author: Richard Xu
    @task: Multiple Robot Grid Navigation
    This is a program to control multiple robots across a grid space so that they don't collide
    with obstacles and other robots. The program is exponential time with the number of robots.
    This means any navigation across large space with >4 robots, or small space with >6 robots will
    be impractical. However, this code is written for a robot navigation competition, where there
    are <=4 robots on stage to coordinate at once, so this is okay.

    The robots are controlled with a bluetooth API, which was given to me. The navigation algorithm
    and the code written are all my own.

    The easiest way to run this is to run `echo demo.txt | python2 multi_grid_navi.py`
    
    I have removed logging messages so that the code can fit in the desired length. Pardon the use of
    global variables. I understand this is not styllistically elegant, but this is hard to adjust now
    given the large number of moving parts in the script.
'''

import sys
import time
import Queue
import Tkinter as tk
from threading import Thread
from HamsterAPI.comm_ble import RobotComm

'''
    Robot drive section - This will make them move based on the instructions.
    To accomplish this for multiple robot, we first wait for the robots to load using a
    time.sleep(). Then, for each move, we create a thread for each robot to guide it to
    its new direction. Each robot will move to its next location based on the instructions,
    and wait for others to finish indicated with the t.join() statement.
    The set_musical_note instructions help indicate that the robot has not fallen offline.
'''

def move(robot, l, r, t):
    robot.set_wheel(0, l)
    robot.set_wheel(1, r)
    time.sleep(t)
    robot.set_wheel(0, 0)
    robot.set_wheel(1, 0)

def right(robot):
    move(robot, 60, 0, 0.8)

def left(robot):
    move(robot, 0, 60, 0.85)

def uturn(robot):
    move(robot, 30, -30, 1.7)

def forward(robot):
    move(robot, 30, 30, 1)

def wait(robot):
    robot.set_musical_note(45)
    time.sleep(0.5)
    robot.set_musical_note(0)

'''
    This function implements a PID controller. Given the color of the floor, which is low
    when the robot is on the path and high when the robot is going off course, we adjust
    the robot's position so it follows the defined path.
'''
def adjust_path(robot):
    l = robot.get_floor(0)
    r = robot.get_floor(1)
    d = r - l
    change = max(min(int(0.2 * d), 69), -69)
    robot.set_wheel(0, 30 - change)
    robot.set_wheel(1, 30 + change)
    time.sleep(1.0 / 20)

def drive_one_instruction(instruction, robot, robot_num, step_num):
    if instruction == 'F':
        forward(robot)
    elif instruction == 'L':
        left(robot)
    elif instruction == 'R':
        right(robot)
    elif instruction == 'U':
        uturn(robot)
    else:
        wait(robot)
        update(robot_num, step_num + 1)
        return
    while not (robot.get_floor(0) < 30 and robot.get_floor(1) < 30):
        adjust_path(robot)
    robot.set_wheel(0, 0)
    robot.set_wheel(1, 0)
    update(robot_num, step_num + 1)
    wait(robot)

num_robot = 0
def drive(instructions):
    comm = RobotComm(num_robot)
    comm.start()
    robot_list = comm.robotList
    while len(robot_list) < num_robot:
        print("Waiting for robots")
        time.sleep(1)
    print("Robots on board. Start driving.")
    time.sleep(3)
    index = 0
    while index < len(instructions[0]):
        print("step #%d" % (index + 1))
        threads = []
        for i in range(num_robot):
            ti = Thread(name="Moving robot %d" % (i + 1), target=drive_one_instruction,
                       args=(instructions[i][index], robot_list[i], i, index))
            ti.start()
            threads.append(ti)
        for ti in threads:
            ti.join()
        index += 1
        time.sleep(1)

'''
    GUI section. Draws the vertices on the screen with color. The colors are chosen to provide
    an interesting contrast between the different robots while making sure the informations are
    readable.
'''

def rgb(c):
    return '#%02x%02x%02x' % (c[0], c[1], c[2])

frame = tk.Tk()
frame.wm_title("Multi-Robot Navigation")
COLORS = ((240, 255, 240), (255, 245, 238), (255, 160, 132), (50, 205, 50),
          (238, 221, 130), (147, 112, 219), (255, 255, 255))
NODE_DIST = 60
NODE_SIZE = 20

def draw_node(canvas, node, n_color):
    x = node[1][0]
    y = node[1][1]
    dist = NODE_DIST
    size = NODE_SIZE
    canvas.create_oval(x * dist - size, y * dist - size,
                       x * dist + size, y * dist + size, fill=n_color)
    canvas.create_text(x * dist, y * dist, fill="black", text=node[0])

def draw_background(canvas, node, n_color):
    x = node[1][0]
    y = node[1][1]
    dist = NODE_DIST
    size = NODE_SIZE + 5
    bg = canvas.create_oval(x * dist - size, y * dist - size,
                            x * dist + size, y * dist + size, fill=n_color)
    canvas.tag_lower(bg)

def draw_edge(canvas, node1, node2, e_color):
    x1 = node1[1][0]
    y1 = node1[1][1]
    x2 = node2[1][0]
    y2 = node2[1][1]
    dist = NODE_DIST
    edge = canvas.create_line(x1 * dist, y1 * dist,
                              x2 * dist, y2 * dist, fill=e_color)
    canvas.tag_lower(edge)

def draw_edge_special(canvas, node1, node2):
    x1 = int(node1[0]) + 1
    y1 = int(node1[1]) + 1
    x2 = int(node2[0]) + 1
    y2 = int(node2[1]) + 1
    dist = NODE_DIST
    canvas.create_line(x1 * dist, y1 * dist, x2 * dist, y2 * dist, fill="forest green")

'''
    This function implements a gradient of color as we move along the path.
'''
def update(robot_num, step_num):
    global path, COLORS, terminals
    color = rgb((int(COLORS[robot_num][0] * (len(path) - step_num) / len(path)),
                 int(COLORS[robot_num][1] * (len(path) - step_num) / len(path)),
                 int(COLORS[robot_num][2] * (len(path) - step_num) / len(path))))
    x = int(path[step_num][robot_num][0]) + 1
    y = int(path[step_num][robot_num][1]) + 1
    dist = NODE_DIST
    size = NODE_SIZE
    terminals[robot_num].create_oval(x * dist - size, y * dist - size,
                                     x * dist + size, y * dist + size, fill=color)
    terminals[robot_num].create_text(x * dist, y * dist,
                                     fill="black", text=path[step_num][robot_num])

'''
    Main algorithm section. Below is an explanation of how the algorithm works.
    
    Let r = number of robots, l = length of the grid, w = width of the grid.
    We create a graph G=(V,E), where the vertices are all possible tuples (x_1, y_1, x_2, y_2,
    ..., x_r, y_r) of robot locations. Generate V recursively. Vertices u,v are connected if
    each robot in u can move to a location in v with one step. In one step, a robot can move
    #1. (x_i+1, y_i) -- east
    #2. (x_i-1, y_i) -- west
    #3. (x_i, y_i+1) -- north
    #4. (x_i, y_i-1) -- south
    #5. (x_i, y_i)   -- wait
    as long as the new location will not contain a robot or an obstacle, and there is no head-on
    collision. To account for head-on collision, check if the new location is occupied by another robot
    and if that robot will move to (x_i, y_i) in the next turn.

    We perform BFS on this graph of n-tuples. The graph is referred to as "mdgraph" in the program.
    For each move, we finally decide how much each robot needs to turn by to get to the new location.
    The instruction set is L = left turn, U = U turn, R = right turn, F = continue straight, S = stop.

    This uses O((lw)^r) space and time. Since r <= 4 in the competition, this is efficient enough for
    l*w ~ 100, which describes all possible maps we are tested with.
'''
def dir_change(prev, next):
    return (next - prev + 4) % 4

def path_to_instruction(path, j):
    global start_dir
    direction = start_dir[j]
    instructions = []
    ins_list = "FLUR"
    for i in range(len(path) - 1):
        new_dir = None
        if int(path[i + 1][j][0]) - int(path[i][j][0]) == 1:  # East
            new_dir = 0
        elif int(path[i + 1][j][1]) - int(path[i][j][1]) == -1:  # North
            new_dir = 1
        elif int(path[i + 1][j][0]) - int(path[i][j][0]) == -1:  # West
            new_dir = 2
        elif int(path[i + 1][j][1]) - int(path[i][j][1]) == 1:  # South
            new_dir = 3
        else:
            instructions.append('S')
        if new_dir:
            instructions.append(ins_list[dir_change(direction, new_dir)])

    return instructions

path = None
def to_instruction(paths):
    global path
    path = paths
    print("Path: \n" + str(paths))
    global terminals
    for i in range(len(terminals)):
        for j in range(len(paths) - 1):
            draw_edge_special(terminals[i], paths[j][i], paths[j+1][i])
    instructions = []
    for i in range(num_robot):
        instructions.append(path_to_instruction(paths, i))
    return instructions

def st(i, j):
    return str(i) + str(j)

def generateEdges(locations, original, graph):
    global obstacles, l, w
    if len(locations) < len(original):
        i = len(locations)
        x_i = int(original[i][0])
        y_i = int(original[i][1])
        pos_loc = [st(x_i, y_i)]
        if x_i < l - 1:
            pos_loc.append(st(x_i + 1, y_i))
        if x_i > 0:
            pos_loc.append(st(x_i - 1, y_i))
        if y_i < w - 1:
            pos_loc.append(st(x_i, y_i + 1))
        if y_i > 0:
            pos_loc.append(st(x_i, y_i - 1))
        for newLoc in pos_loc:
            if not (newLoc in locations or newLoc in obstacles):
                headOn = False
                if newLoc in original:
                    j = original.index(newLoc)
                    if j < i and original[i] == locations[j]:
                        headOn = True
                if not headOn:
                    locations.append(newLoc)
                    generateEdges(locations, original, graph)
                    del locations[-1]
    else:
        graph[original].append(tuple(locations))

def generateVertices(soFar, graph):
    global num_robot, obstacles, l, w
    if len(soFar) < num_robot:
        for i in range(l):
            for j in range(w):
                loc = st(i, j)
                if (not loc in soFar) and (not loc in obstacles):
                    soFar.append(loc)
                    generateVertices(soFar, graph)
                    del soFar[-1]
    else:
        vertex = tuple(soFar)
        graph[vertex] = []
        generateEdges([], vertex, graph)

def bfs(start_nodes, graph):
    global end_nodes
    q = Queue.Queue()
    visited = {}
    for vertex in graph:
        visited[vertex] = False
    q.put((start_nodes, [start_nodes]))
    while not q.empty():
        node = q.get()
        if not visited[node[0]]:
            visited[node[0]] = True
            if node[0] == end_nodes:
                return to_instruction(node[1])
            for u in graph[node[0]]:
                if not visited[u]:
                    q.put((u, node[1] + [u]))

'''
    The main control for the program. This has to be a thread because frame.mainloop() and
    this has to run at the same time.
'''
def controller():
    global start_nodes, end_nodes, COLORS, nodes_location, canvas, l, terminals
    # Draw the nodes
    canvas.create_text(l * 35, 10, text="Main terminal")
    for node in nodes_location:
        if node[0] in start_nodes:
            draw_node(canvas, node, rgb(COLORS[start_nodes.index(node[0])]))
        else:
            draw_node(canvas, node, 'RoyalBlue1')
        if node[0] in end_nodes:
            draw_background(canvas, node, rgb(COLORS[end_nodes.index(node[0])]))
        connected_nodes = graph[node[0]]
        if not connected_nodes:
            continue
        for connected_node in connected_nodes:
            for a_node in nodes_location:
                if connected_node == a_node[0]:
                    draw_edge(canvas, node, a_node, 'RoyalBlue1')
    # Generate the terminals
    for i in range(num_robot):
        terminals[i].create_text(l * 35, 10, text="Terminal #%d" % (i+1))
        for node in nodes_location:
            if node[0] == start_nodes[i]:
                draw_node(terminals[i], node, rgb(COLORS[i]))
            else:
                draw_node(terminals[i], node, 'RoyalBlue1')
            if node[0] == end_nodes[i]:
                draw_background(terminals[i], node, rgb(COLORS[i]))
            connected_nodes = graph[node[0]]
            if not connected_nodes:
                continue
            for connected_node in connected_nodes:
                for a_node in nodes_location:
                    if connected_node == a_node[0]:
                        draw_edge(terminals[i], node, a_node, 'RoyalBlue1')
    # Generate multi-dimensional graph
    mdgraph = {}
    print("Generating Vertices of multi-graph. This may take a few minutes.")
    generateVertices([], mdgraph)
    print("Running BFS.")
    instructions = bfs(start_nodes, mdgraph)
    print("Printing Instructions.")
    print(str(instructions))
    time.sleep(1)
    drive(instructions)
    time.sleep(3)
    sys.exit(0)

'''
    The section that reads the input for the entire program. Notice how we are able to set
    default values: since an empty string "" in python has a False boolean value, if the user
    does not input any information it will use the default value.
'''
obstacles = set()
graph = dict()
nodes_location = []
start_nodes = []
end_nodes = []
start_dir = []
terminals = []
l = int(raw_input("Length of board: ") or 4)
w = int(raw_input("Height of board: ") or 4)
canvas = tk.Canvas(frame, bg="snow", width=l * 70, height=w * 70)
canvas.grid(row=0, column=0)
n = int(raw_input("Number of obstacles: ") or 0)
for i in range(n):
    obstacles.add(str(raw_input("Enter coordinates for obstacle #%d: " % (i+1))))
for i in range(l):
    for j in range(w):
        name = str(i) + str(j)
        if name not in obstacles:
            connected = set()
            if i > 0 and st(i - 1, j) not in obstacles:
                connected.add(st(i - 1, j))
            if i < l - 1  and st(i + 1, j) not in obstacles:
                connected.add(st(i + 1, j))
            if j > 0  and st(i, j - 1) not in obstacles:
                connected.add(st(i, j - 1))
            if j < w - 1 and st(i, j + 1) not in obstacles:
                connected.add(st(i, j + 1))
            graph[name] = connected
            nodes_location.append((name, [i + 1, j + 1]))
num_robot = int(raw_input("Number of robots: ") or 0)
for i in range(num_robot):
    terminals.append(tk.Canvas(frame, bg="snow", width=l * 70, height=w * 70))
    terminals[i].grid(row=(i + 1) / 4, column=(i + 1) % 4)
for i in range(num_robot):
    start_nodes.append(raw_input("Start coordinate for robot #%d: " % (i + 1)).strip())
    end_nodes.append(raw_input("End coordinate for robot #%d: " % (i + 1)).strip())
    start_dir.append("ENWS".index(raw_input("Start direction for robot #%d (NESW): " % (i + 1))[0]))
start_nodes = tuple(start_nodes)
end_nodes = tuple(end_nodes)
Thread(target=controller).start()
frame.mainloop()