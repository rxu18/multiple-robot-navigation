import sys  # i.e. the system
import time  # to sleep and wait
from threading import Thread  # for thrading
import Tkinter as tk  # GUI
import Queue  # Queues!
from HamsterAPI.comm_usb import RobotComm  # Hamster!

'''
This time it's automated maze-solving! The basic idea of thread is simple - just running
another function at the same time. You can see that I went fairly creative with the name
choices. Now this maze-solving algorithm is actually quite terrible: It just always try to
turn right. Simple, Stupid, but somewhat effective.

'''
FREQ = 0.1
MAX_ROBOT = 1
quit = False
robots = []
robot = None
pq = Queue.Queue()
wq = Queue.Queue()


def move(l, r):
    global robot
    robot.set_wheel(0, l)
    robot.set_wheel(1, r)

# Colors!


def grey(d):
    tup = (int(2.56 * d), int(2.56 * d), int(2.56 * d))
    return rgb(tup)


def rgb(tup):
    s = "#"
    for i in range(3):
        s += hex(tup[i])[2:4]
    return s


def watch():
    global robot
    global pq
    global wq
    global quit
    while not quit:
        l = robot.get_proximity(0)
        r = robot.get_proximity(1)
        fl = robot.get_floor(0)
        fr = robot.get_floor(1)
        data = (l, r, fl, fr)
        pq.put(data)
        # Determines whether it's safe right now. If either sensor reads less than 40, tell it to turn.
        # If l > r, turn left, and vice versa.
        if l > 60 or r > 60:
            if l > r:
                # print("+++++Turning Left! l = %d, r = %d +++++" % (l,r));
                wq.put(1)
            else:
                # print("+++++Turning Right! l = %d, r = %d+++++" % (l,r));
                wq.put(2)
        else:
            # print("++++++Safe++++++");
            wq.put(0)
        if fl < 50 or fr < 50:
            quit = True
            f = open('inputs/Finish.txt', 'r')
            notes = []
            for line in f:
                line = line.strip()
                notes.append(line.split(" "))
            for note in notes:
                robot.set_musical_note(int(note[0]) + 39)
                time.sleep(0.3 * float(note[1]))
                robot.set_musical_note(0)
                time.sleep(0.2 * float(note[1]))
        time.sleep(FREQ)
    return
    # This thread will read sensor data and put sensor data into queues
    # IMPORTANT! This is the only thread that should directly read robot sensors

# Needs access to Canvas, pass from main function


def paint(canvas):
    global robot
    global pq
    global quit
    rect = canvas.create_rectangle(120, 200, 180, 260, fill='#aaa')
    # The first "l" means laser-eyes!
    ll = canvas.create_line(0, 0, 0, 0, fill="red")
    lr = canvas.create_line(0, 0, 0, 0, fill="red")
    # Floor rectangles
    fl = canvas.create_rectangle(125, 205, 140, 210, fill="white")
    fr = canvas.create_rectangle(160, 205, 175, 210, fill="white")
    while not quit:
        if not pq.empty():
            # print("Receiving Data!");
            data = pq.get()
            l = data[0]
            r = data[1]
            if (l >= 10):
                canvas.coords(ll, (133, 200, 133, 200 + (l - 100)))
            else:
                canvas.coords(ll, (0, 0, 0, 0))
            if (r >= 10):
                canvas.coords(lr, (167, 200, 167, 200 + (r - 100)))
            else:
                canvas.coords(lr, (0, 0, 0, 0))
            #print ("l = %d, r = %d" % (l, r));
            fl = data[2]
            fr = data[3]
            #print ("fl = %d, fr = %d" % (fl, fr));
            canvas.create_rectangle(125, 205, 140, 210, fill=grey(fl))
            canvas.create_rectangle(160, 205, 175, 210, fill=grey(fr))
            time.sleep(FREQ * 0.9)
    return
    # This thread will read information from the queue and update the gui accordingly, and also handle events
    # such as reaching the border


def walk():
    global robot
    global quit
    while not quit:
        if not wq.empty():
            mov = wq.get()
            if mov == 0:
                move(30, 30)
            else:
                move(50, -50)
            time.sleep(FREQ * 0.9)
    move(0, 0)
    return
    # This thread will read information from the queue and update robot movement accordingly


def main():
    global robots
    global robot
    global quit
    comm = RobotComm(MAX_ROBOT)
    comm.start()
    print("Bluetooth,Start!")
    robots = comm.robotList
    robot = robots[0]
    frame = tk.Tk()
    mycanvas = tk.Canvas(frame, bg="white", width=300, height=300)
    mycanvas.pack()
    watchman = Thread(name="Watchman", target=watch)
    watchman.start()
    painter = Thread(name="Painter", target=paint, args=(mycanvas,))
    painter.start()
    walker = Thread(name="Walker", target=walk)
    walker.start()

    frame.mainloop()

    # Cleaning up
    quit = True
    robot.reset()

    comm.stop()


main()
