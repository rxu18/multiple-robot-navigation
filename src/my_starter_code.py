import sys  # i.e. the system
import time  # to sleep and wait
import threading  # for thrading
import Tkinter as tk  # GUI
from HamsterAPI.comm_usb import RobotComm  # Hamster!

'''
I feel like I wasted all of yesterday understanding how the GUI works. But at least we 
ave a starter code written all by me! We just draw a rectangle with eyes' color based
on some rgb value, and bind a few keys with the format I did below.

Now, grey(d) accepts a value from 0 to 99 and returns a shade of grey from #000000 to #ffffff
(256 shades of grey!) and the rgb conversions is pretty self-explanatory.
'''
MAX_R = 1


def move(l, r):
    if (len(gRobotList) > 0):
        for robot in gRobotList:
            robot.set_wheel(0, l)
            robot.set_wheel(1, r)


def rightTurn():
    move(50, -50)
    time.sleep(0.549)
    move(0, 0)


def grey(d):
    tup = (int(2.56 * d), int(2.56 * d), int(2.56 * d))
    return rgb(tup)


def rgb(tup):
    s = "#"
    for i in range(3):
        s += hex(tup[i])[2:4]
    return s


class Controller(object):
    # Initializer
    def __init__(self):
        self.behavior = 'Pause'
        self.quit = False
        self.done = False
        t = threading.Thread(target=self.controller)
        t.daemon = True
        t.start()
        self.controller_thread = t
        return

    # Determines which method gets implemented
    def controller(self):
        while not self.quit:
            if (self.behavior == "Pause"):
                self.pause()  # Done!
            elif (self.behavior == "Display"):
                self.display()
            else:
                print("Wait... What program is this?")
        print("And we're done!")
        return

    def setB(self, phrase="Pause"):
        self.behavior = phrase

    # Main part of the program

    def pause(self):
        if len(gRobotList) > 0:
            for robot in gRobotList:
                robot.set_wheel(0, 0)
                robot.set_wheel(1, 0)
                robot.set_musical_note(0)
        time.sleep(0.1)
        return

    def display(self):
        global canvas
        global ll
        global lr
        if len(gRobotList) > 0:
            canvas.create_rectangle(120, 200, 180, 260, fill='#aaa')
            # create a line segment for drawing the left proximilty sensor
            # create a line segment for drawing the right proxijity sensor
            robot = gRobotList[0]
            l = robot.get_proximity(0)
            r = robot.get_proximity(1)
            if (l >= 10):
                canvas.coords(ll, (133, 200, 133, 200 + (l - 100)))
            else:
                canvas.coords(ll, (0, 0, 0, 0))
            if (r >= 10):
                canvas.coords(lr, (167, 200, 167, 200 + (r - 100)))
            else:
                canvas.coords(lr, (0, 0, 0, 0))
            #print ("l = %d, r = %d" % (l, r));
            fl = robot.get_floor(0)
            fr = robot.get_floor(1)
            #print ("fl = %d, fr = %d" % (fl, fr));
            canvas.create_rectangle(125, 205, 140, 210, fill=grey(fl))
            canvas.create_rectangle(160, 205, 175, 210, fill=grey(fr))

        time.sleep(0.1)

# GUI


class GUI(object):
    def __init__(self, root, behaviors):
        self.root = root
        self.behaviors = behaviors
        self.initUI()

    # Buttons!
    def initUI(self):
        global canvas
        global ll
        global lr
        frame = self.root
        frame.geometry('300x400')
        mycanvas = tk.Canvas(frame, bg="green", width=300, height=300)
        mycanvas.pack()
        canvas = mycanvas
        self.behaviors.setB("Display")

        ll = canvas.create_line(0, 0, 0, 0, fill="red")
        lr = canvas.create_line(0, 0, 0, 0, fill="red")
        bP = tk.Button(frame, text="Pause")
        bP.pack(side='left')
        bP.bind('<Button-1>', lambda x: self.behaviors.setB("Pause"))

        bE = tk.Button(frame, text="Exit")
        bE.pack(side='left')
        bE.bind('<Button-1>', self.stopProg)

        mycanvas.bind_all("<w>", lambda x: move(30, 30))
        mycanvas.bind_all("<a>", lambda x: move(-30, 30))
        mycanvas.bind_all("<s>", lambda x: move(-30, -30))
        mycanvas.bind_all("<d>", lambda x: move(30, -30))
        mycanvas.bind_all("<KeyRelease>", lambda x: move(0, 0))
        mycanvas.bind_all("<r>", lambda x: rightTurn())

    def stopProg(self, event=None):
        self.behaviors.quit = True
        self.behaviors.done = True
        for robot in gRobotList:
            robot.reset()
        self.behaviors.controller_thread.join()
        self.root.quit()
        return


# main, where we run the code.
gMaxRobotNum = 1
gRobotList = []


def main(argv=None):
    # instantiate COMM object
    global gRobotList
    comm = RobotComm(gMaxRobotNum)
    comm.start()
    print("Bluetooth,Start!")
    gRobotList = comm.robotList
    frame = tk.Tk()
    GUI(frame, Controller())
    frame.mainloop()
    comm.stop()
    comm.join()
    print("terminated!")


main()