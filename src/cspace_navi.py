'''
NAME: Richard Xu
LANG: Python
TASK: C-Space
'''
'''
This is one of the more complex projects I worked on. Therefore, the documentation will be split into parts.
Also, why is .in file considered as executable here? I don't even know...
'''


# ed = Euclidean Distance




import Queue
import Tkinter as tk
import time
import math
from threading import Thread
from HamsterAPI.comm_usb import RobotComm
def ed(x1, y1, x2, y2):
    return math.sqrt(math.pow(x1-x2, 2) + math.pow(y1-y2, 2))


'''
A* is similar to Dijkstra, in that we are always choosing the closest node for now, but we also have a projected cost based on how close
the node is from the destination. The cost will always be optimistic. Therefore, instead of going for nodes that are closest but going another
way, it would go for nodes that are at a good place in going to the goal. Also, once it's at the goal, it would remove any nodes that have a projected
cost higher than the current lowest cost to the goal, since the projection is optimistic.
'''
# A simple implementation of A-Star. Going from 0, aiming for 1.


def pathfind(vertices, edges):
    d = [float('inf')] * len(vertices)
    d[0] = 0
    visited = [False] * len(vertices)
    parent = [None] * len(vertices)
    numVisited = 0
    while (numVisited < len(vertices)):
        next = -1
        for i in range(len(vertices)):
            if not visited[i] and (next == -1 or d[i] < d[next]):
                next = i
        visited[next] = True
        for vertex in edges[next]:
            projectedCost = d[next] + \
                ed(vertices[next][0], vertices[next][1], vertices[vertex][0], vertices[vertex][1]) + \
                ed(vertices[vertex][0], vertices[vertex]
                   [1], vertices[1][0], vertices[1][1])
            if (projectedCost < d[vertex]):
                d[vertex] = projectedCost
                parent[vertex] = next
                if vertex == 1:
                    # We remove all vertices whose distance is further.
                    for i in range(len(vertices)):
                        if not visited[i] and d[i] > d[vertex]:
                            visited[i] = True
                            # print "Removing node %d because the projected distance is too far." % i
        numVisited += 1
    path = [1, ]
    lastNode = 1
    while (parent[lastNode] != None):
        lastNode = parent[lastNode]
        path.append(lastNode)
    return path


def draw(canvas, x, y, a, hamster, lEye, rEye):
    l = 20 * math.sqrt(2)
    vtx = []
    s = a + (3.1415/4)
    for i in range(4):
        vtx.append((x + l * math.sin(s), y + l * math.cos(s)))
        s += 3.1415 / 2
    canvas.coords(hamster, (vtx[0][0], vtx[0][1], vtx[1][0],
                            vtx[1][1], vtx[2][0], vtx[2][1], vtx[3][0], vtx[3][1]))
    canvas.coords(lEye, ((4*vtx[0][0]+vtx[2][0]) / 5 + 2, (4*vtx[0][1]+vtx[2][1]) /
                         5 + 2, (4*vtx[0][0]+vtx[2][0])/5 - 2, (4*vtx[0][1]+vtx[2][1])/5 - 2))
    canvas.coords(rEye, ((vtx[3][0]+4*vtx[1][0]) / 5 + 2, (vtx[3][1]+4*vtx[1][1]) /
                         5 + 2, (vtx[3][0]+4*vtx[1][0])/5 - 2, (vtx[3][1]+4*vtx[1][1])/5 - 2))


def drawRobot(canvas, segments, start):
    hamster = canvas.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, fill="white")
    lEye = canvas.create_oval(0, 0, 0, 0, fill="black")
    rEye = canvas.create_oval(0, 0, 0, 0, fill="black")
    (x, y, a) = (start[0], start[1], 0)
    for seg in segments:
        while (a - seg[1] > 0.2 or a - seg[1] < -0.2):
            a = (a + 0.1) % 6.28
            draw(canvas, x, y, a, hamster, lEye, rEye)
            time.sleep(0.05)
        a = seg[1]
        d = 0
        while d < seg[0]:
            d += 2
            x += 2 * math.cos(a)
            y -= 2 * math.sin(a)
            draw(canvas, x, y, a, hamster, lEye, rEye)
            time.sleep(0.05)
        x += (d - seg[0]) * math.cos(a)
        y -= (d - seg[0]) * math.sin(a)
# Main


def main():
    global root
    r = 20 * math.sqrt(2)
    # Read the rectangles. Using a file so that I don't have to type it over and over.
    f = open("C-space.in", "r")
    world = f.readline().strip().split(" ")
    for i in range(4):
        world[i] = int(world[i])
    n = int(f.readline())
    obs = []
    for i in range(n):
        obs.append(f.readline().strip().split(" "))
        for j in range(4):
            obs[i][j] = int(obs[i][j]) - world[j % 2]
    w = world[2] - world[0]
    h = world[3] - world[1]
    start_node = f.readline().strip().split(" ")
    end_node = f.readline().strip().split(" ")
    for i in range(2):
        start_node[i] = int(start_node[i]) - world[0]
        end_node[i] = int(end_node[i]) - world[1]
    # Turn obstacles into C-obstacles
    cobs = []
    for o in obs:
        cobs.append([max(o[0] - r, 0), max(o[1] - r, 0),
                     min(o[2] + r, w), min(o[3] + r, h)])

    '''
		Here we're using a recursive algorithm to accomplish our goal. We start off with the entire grid as a cell, and as we add in new
		obstacles, we cut it into smaller and smaller pieces with vertical lines going up and down.
		Each of the conditions below check for whether or not there will be a new life cell on the four sides of the obstacle.
	'''
    # Life cell creation
    # Naming scheme: cobs[i] = [x_min, y_min, x_max, y_max]. The same applies to lc's
    lc = [[0, 0, world[2] - world[0], world[3] - world[1]]]
    for co in cobs:
        newLc = []
        for cell in lc:
            # If the obstacles is to the left, right, down, or up of the cell
            if cell[0] > co[2] or cell[2] < co[0] or cell[1] > co[3] or cell[3] < co[1]:
                newLc.append(cell)
                continue
            # The two shapes must intersect now.
            # There is a cell to the left of the obstacle
            if cell[0] < co[0]:
                newLc.append([cell[0], cell[1], co[0], cell[3]])
            # To the Right!
            if cell[2] > co[2]:
                newLc.append([co[2], cell[1], cell[2], cell[3]])
            # To the bottom!
            if cell[1] < co[1]:
                newLc.append([max(cell[0], co[0]), cell[1],
                              min(co[2], cell[2]), co[1]])
            # To the top!
            if cell[3] > co[3]:
                newLc.append([max(cell[0], co[0]), co[3],
                              min(co[2], cell[2]), cell[3]])
        lc = newLc

    # Remove fake cells
    index = 0
    while index < len(lc):
        if abs(lc[index][0] - lc[index][2]) < 0.01:
            lc.pop(index)
        else:
            index += 1

    '''
		We connect the live-cells based on their x-coordinates and y-coordinates. Now, the live-cells will not be the vertices - the midpoints of the side they
		intersect on will be.
	'''
    # Connecting the dots
    nodes = []
    nodesInLC = [[] for i in range(len(lc))]
    # Add the start and end nodes
    nodes.append(start_node)
    nodes.append(end_node)
    for i in range(len(lc)):
        for j in range(2):
            if (lc[i][0] <= nodes[j][0] and lc[i][2] > nodes[j][0] and lc[i][1] <= nodes[j][1] and lc[i][3] > nodes[j][1]):
                nodesInLC[i].append(j)
    # Add the other nodes
    for i in range(len(lc)):
        for j in range(len(lc)):
            if i != j:
                if lc[i][0] == lc[j][2] and lc[i][3] > lc[j][1] and lc[i][1] < lc[j][3]:
                    nodes.append(
                        (lc[i][0], (max(lc[i][1], lc[j][1]) + min(lc[i][3], lc[j][3])) / 2))
                    nodesInLC[i].append(len(nodes) - 1)
                    nodesInLC[j].append(len(nodes) - 1)
                elif lc[i][1] == lc[j][3] and lc[i][2] > lc[j][0] and lc[i][0] < lc[j][2]:
                    nodes.append(
                        (max(lc[i][0], lc[j][0]) + min(lc[i][2], lc[j][2]))/2, lc[i][1])
                    nodesInLC[i].append(len(nodes) - 1)
                    nodesInLC[j].append(len(nodes) - 1)

    '''
		A simple way of generating the graph.
	'''
    # Generate the graph
    edges = [[] for i in range(len(nodes))]
    for i in range(len(nodes)):
        for nodeInLC in nodesInLC:
            if i in nodeInLC:
                for node in nodeInLC:
                    if node != i:
                        edges[i].append(node)
    path = pathfind(nodes, edges)

    # GUI stuff
    canvas = tk.Canvas(root, bg="white", width=w, height=h)
    canvas.pack()
    for co in cobs:
        canvas.create_rectangle(co[0], co[1], co[2],
                                co[3], width=0, fill="grey")
    for o in obs:
        canvas.create_rectangle(o[0], o[1], o[2], o[3], fill="black")
    for i in range(len(lc)):
        cell = lc[i]
        canvas.create_rectangle(
            cell[0], cell[1], cell[2], cell[3], fill="green")
        # time.sleep(1)
    for i in range(len(nodes)):
        node = nodes[i]
        canvas.create_oval(node[0] - 5, node[1] - 5,
                           node[0] + 5, node[1] + 5, fill="blue")
        canvas.create_text(node[0], node[1] - 10, text=str(i), fill="white")
    for i in range(len(nodes)):
        for j in edges[i]:
            canvas.create_line(nodes[i][0], nodes[i][1],
                               nodes[j][0], nodes[j][1])
    canvas.create_oval(nodes[0][0] - 5, nodes[0][1] - 5,
                       nodes[0][0] + 5, nodes[0][1] + 5, fill="red")
    segments = []
    for i in range(len(path) - 1):
        canvas.create_oval(nodes[path[i]][0] - 5, nodes[path[i]][1] - 5,
                           nodes[path[i]][0] + 5, nodes[path[i]][1] + 5, fill="red")
        canvas.create_line(nodes[path[i]][0], nodes[path[i]][1],
                           nodes[path[i+1]][0], nodes[path[i+1]][1], fill="red")
        segments.insert(0, (nodes[path[i+1]][0], nodes[path[i+1]]
                            [1], nodes[path[i]][0], nodes[path[i]][1]))
    # print segments
    psegments = []  # p for polar
    for sg in segments:
        l = ed(sg[0], sg[1], sg[2], sg[3])
        theta = math.atan((sg[1]-sg[3])/(sg[2]-sg[0]))
        if (sg[2] - sg[0]) < 0:
            theta += 3.1416
        psegments.append((l, theta))
    # print str(psegments)
    drawRobot(canvas, psegments, start_node)
    root.quit()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("C-Space Navigation")
    t = Thread(target=main)
    t.deamon = True
    t.start()
    root.mainloop()
