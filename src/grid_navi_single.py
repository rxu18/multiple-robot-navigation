'''
NAME: Richard, Max, Qin
LANG: Python
TASK: Grid Navigation
'''
'''
I based my final project off of this program. Since I explained the final project in detail, I'll explain this in less detail.

Input section: If you look at the final project, this should seem similar to you. However, instead of having the robot move from any position to another, we just
implemented it so that the robot moves from top-left to bottom-right.

Robot-Drive section: This is also similar to that in the final project, except we don't use threads. The move functions are designed for my robot, Halbert, so you
might want to change it a little. The robot goes to the next intersection, turns based on the instructions, and moves to the next interseciton with a line following.

toInstruction and BFS: For BFS, just read it online. It wouldn't be difficult, especially since the graph is stored as an adjacency list. For toInstruction, it's 
almost exactly the same as that in final project.
'''

import sys
import pdb
import Queue
import time
import Tkinter as tk
from threading import Thread
from HamsterAPI.comm_usb import RobotComm # Hamster!
instruct = None
robot = None
interval = 20


def move(l, r, t):
    robot.set_wheel(0, l)
    robot.set_wheel(1, r)
    time.sleep(t)
    robot.set_wheel(0, 0)
    robot.set_wheel(1, 0)


def right():
    move(60, 0, 0.9)


def left():
    move(0, 60, 0.9)


def uturn():
    move(30, -30, 1.8)


def forward():
    robot.set_wheel(0, 30)
    robot.set_wheel(1, 30)
    time.sleep(1)


def pid():
    global interval
    l = robot.get_floor(0)
    r = robot.get_floor(1)
    d = r-l
    #print("l = %d, r = %d, d = %d" % (l, r, d));
    change = max(min(int(0.2 * d), 79), -79)
    robot.set_wheel(0, 30 - change)
    robot.set_wheel(1, 30 + change)
    time.sleep(1.0 / interval)
    return


def robotDrive():
    global instruct
    global robot
    MAX_ROBOT = 1
    comm = RobotComm(MAX_ROBOT)
    comm.start()
    print("Bluetooth,Start!")
    robot = comm.robotList[0]
    index = 0
    while index < len(instruct) + 1:
        if robot.get_floor(0) < 30 and robot.get_floor(1) < 30:
            print "Reaching an intersection!"
            if index == len(instruct):
                break
            if instruct[index] == 'F':
                forward()
            elif instruct[index] == 'L':
                left()
            elif instruct[index] == 'R':
                right()
            else:
                uturn()
            index += 1
        else:
            pid()
    robot.set_wheel(0, 60)
    robot.set_wheel(1, -60)
    f = open('Finish.txt', 'r')
    notes = []
    for line in f:
        line = line.strip()
        notes.append(line.split(" "))
    for note in notes:
        robot.set_musical_note(int(note[0]) + 39)
        time.sleep(0.3 * float(note[1]))
        robot.set_musical_note(0)
        time.sleep(0.2 * float(note[1]))
    robot.set_wheel(0, 0)
    robot.set_wheel(1, 0)
    return


class GraphDisplay(object):
    def __init__(self, graph, nodes_location, start_node=None, goal_node=None, l=5, w=5):
        self.node_dist = 60
        self.node_size = 20
        self.canvas = None
        self.graph = graph
        self.nodes_location = nodes_location
        self.start_node = start_node
        self.goal_node = goal_node
        self.display_graph(l, w)
        return

    def display_graph(self, l, w):
        frame = tk.Tk()
        self.canvas = tk.Canvas(frame, bg="white", width=l * 80, height=w * 80)
        self.canvas.pack(expand=1, fill='both')
        for node in self.nodes_location:
            if node[0] == self.start_node:
                self.draw_node(node, 'red')
            elif node[0] == self.goal_node:
                self.draw_node(node, 'green')
            else:
                self.draw_node(node, 'blue')
            # get list of names of connected nodes
            connected_nodes = self.graph[node[0]]
            # find location for each connected node and draw edge
            if connected_nodes:
                for connected_node in connected_nodes:
                    # step into node locations
                    for a_node in nodes_location:
                        if connected_node == a_node[0]:
                            self.draw_edge(node, a_node, 'blue')
        t1 = Thread(name='thread1', target=self.bfs)
        t1.start()
        frame.mainloop()
        return

    def draw_node(self, node, n_color):
        node_name = node[0]
        x = node[1][0]
        y = node[1][1]
        dist = self.node_dist
        size = self.node_size
        self.canvas.create_oval(x*dist-size, y*dist-size,
                                x*dist+size, y*dist+size, fill=n_color)
        self.canvas.create_text(x*dist, y*dist, fill="white", text=node[0])
        return

    def draw_edge(self, node1, node2, e_color):
        x1 = node1[1][0]
        y1 = node1[1][1]
        x2 = node2[1][0]
        y2 = node2[1][1]
        dist = self.node_dist
        self.canvas.create_line(x1*dist, y1*dist, x2 *
                                dist, y2*dist, fill=e_color)
        return

    def toInstruction(self, path):
        # Assume that robot starts facing east.
        # 0 = E, 1 = N, 2 = W, 3 = S
        direction = 0
        instructions = []
        # print str(path)
        for i in range(len(path) - 1):
            newDir = None
            if int(path[i+1][0]) - int(path[i][0]) == 1:  # East
                newDir = 0
            elif int(path[i+1][1]) - int(path[i][1]) == -1:  # North
                newDir = 1
            elif int(path[i+1][0]) - int(path[i][0]) == -1:
                newDir = 2
            else:
                newDir = 3
            # print("i = %d, direction = %d, newDir = %d" % (i, direction, newDir))
            change = (newDir - direction + 4) % 4
            if change == 1:
                instructions.append('L')
            elif change == 2:
                instructions.append('U')
            elif change == 3:
                instructions.append('R')
            else:
                instructions.append('F')
            direction = newDir
        return instructions

    def bfs(self):
        global instruct
        # q = Queue.LifoQueue()
        q = Queue.Queue()
        visited = []
        q.put((self.start_node, [self.start_node]))
        while not q.empty():
            node = q.get()
            if not node[0] in visited:
                loc = None
                for i in range(len(nodes_location)):
                    if nodes_location[i][0] == node[0]:
                        loc = nodes_location[i][1]
                        break
                self.draw_node((node[0], loc), 'purple')
                time.sleep(0.1)
                self.draw_node((node[0], loc), 'yellow')
                visited.append(node[0])
                print("Visiting node " + node[0])
                if node[0] == self.goal_node:
                    instruct = self.toInstruction(node[1])
                    print str(instruct)
                    robotDrive()
                    return
                for newNode in self.graph[node[0]]:
                    if not newNode in visited:
                        q.put((newNode, node[1] + [newNode]))


l = int(input("Input length: "))
w = int(input("Input width: "))
n = int(input("Obstacles? "))
obstacles = []
for i in range(n):
    obstacles.append(str(raw_input("Coords? ")))
graph = dict()
nodes_location = []
# print str(obstacles)
for i in range(l):
    for j in range(w):
        name = str(i) + str(j)
        if not name in obstacles:
            connected = set()
            if i > 0 and not (str(i-1) + str(j)) in obstacles:
                connected.add(str(i-1) + str(j))
            if i < l - 1 and not (str(i+1) + str(j)) in obstacles:
                connected.add(str(i+1) + str(j))
            if j > 0 and not (str(i) + str(j - 1)) in obstacles:
                connected.add(str(i) + str(j - 1))
            if j < w - 1 and not (str(i) + str(j + 1)) in obstacles:
                connected.add(str(i) + str(j+1))
            graph[name] = connected
            nodes_location.append((name, [i + 1, j + 1]))

display = GraphDisplay(graph, nodes_location, '00', str(l-1) + str(w-1), l, w)
