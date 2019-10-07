import sys  # i.e. the system
import time  # to sleep and wait
from threading import Thread  # for thrading
import Tkinter as tk
from HamsterAPI.comm_ble import RobotComm  # Hamster!

'''
This is probably one of the simplest program, but one of the most useful, as it's just a bare-bones
software to run the hamsters.
'''
gMaxRobotNum = 2
gRobotList = []
robot = 0


def move(l, r, t):
    robot.set_wheel(0, l)
    robot.set_wheel(1, r)
    time.sleep(t)
    robot.set_wheel(0, 0)
    robot.set_wheel(0, 0)


def count():
    for i in range(10):
        print str(i)
        time.sleep(1)


def main(argv=None):
    # instantiate COMM object
    while True:
        if len(gRobotList) > 0:
            for r in gRobotList:
                r.set_musical_note(45)
                time.sleep(2)
    robot = gRobotList[0]
    robot1 = gRobotList[1]
    for r in gRobotList:
        r.set_musical_note(45)
        time.sleep(2)
    f = open('Start.txt', 'r')
    notes = []
    for line in f:
        line = line.strip()
        notes.append(line.split(" "))
    for note in notes:
        robot.set_musical_note(int(note[0]) + 39)
        time.sleep(0.3 * float(note[1]))
        robot.set_musical_note(0)
        time.sleep(0.2 * float(note[1]))
    robot.set_topology(10)
    time.sleep(0.5)
    # main part of test
    # t1 = Thread(target = count)
    # t1.start()
    # t2 = Thread(target = count)
    # t2.start()
    # t3 = Thread(target = count)
    # t3.start()
    # ending
    comm.stop()
    comm.join()
    print("terminated!")


# Terminate the program when exit.
global gRobotList
global robot
comm = RobotComm(gMaxRobotNum)
comm.start()
print("Bluetooth,Start!")
gRobotList = comm.robotList
t = Thread(target=main)
t.start()
frame = tk.Tk()
frame.mainloop()
