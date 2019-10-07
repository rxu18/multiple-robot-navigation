'''
   =======================================================================
   Written By Richard Xu with help from Drs. David Zhu and Qin Chen.

   Last updated: May 28th, 2016
   ========================================================================
'''

'''
This program creates five different behaviors for the hamster: Square, Shy, Dance, Follow and Sing.
The code is written at a time when I had limited Python exposure. In fact, this may be the first
Python program I ever wrote.

Sing is the one I am the most proud of: it reads a file and makes the robot sing. Square makes the
robot travel in a small square Shy makes the robot travel in a straight line until it encounters an
object, at which moment it shies away Follow makes the robot follow whatever is in front of it, like
an ant Dance makes the robot move all over the place.
'''
import sys
import time  # sleep
import Tkinter as tk
import threading
from ../../HamsterAPI.comm_ble import RobotComm
#from HamsterAPI.comm_usb import RobotComm

gMaxRobotNum = 8
gRobotList = []

class ThreadedBehaviors(object):
    def __init__(self):
        self.behavior='Shy'
        self.gQuit = False
        t = threading.Thread(target=self.behaviors)
        t.daemon = True
        t.start()
        self.behavior_handle = t

    def behaviors(self):
        while not self.gQuit:
            if self.behavior == 'Square':
                self.square()
            elif self.behavior == 'Shy':
                self.shy()
            elif self.behavior == 'Dance':
                self.dance()
            elif self.behavior == 'Follow':
                self.follow()
            elif self.behavior == 'Sing':
                self.sing()       
            else:
                print 'waiting for robot...'
        print "exiting behaviors loop"

    def square(self):
        if (len(gRobotList) > 0):
            for robot in gRobotList:
                robot.set_wheel(0,50)
                robot.set_wheel(1,-50)
                time.sleep(0.515)
                robot.set_wheel(0,50)
                robot.set_wheel(1,50)
                time.sleep(1)
        time.sleep(0.1)
        return

    def shy(self):       
        if (len(gRobotList) > 0):
            for robot in gRobotList:
                prox_l = robot.get_proximity(0)
                prox_r = robot.get_proximity(1)
                if (prox_l > 40 or prox_r > 40):
                    robot.set_wheel(0,20-prox_l)
                    robot.set_wheel(1,20-prox_r)
                    robot.set_musical_note((prox_l+prox_r)/2)  
                    time.sleep(0.1)
                else:
                    robot.set_wheel(0,0)
                    robot.set_wheel(1,0)
                    robot.set_musical_note(0)
                    time.sleep(0.1)
        time.sleep(0.1)                   
        
    def follow(self):
        if (len(gRobotList) > 0):
            for robot in gRobotList:
                prox_l = robot.get_proximity(0)
                prox_r = robot.get_proximity(1)
                if (prox_l < 10 or prox_r < 10):
                    robot.set_wheel(0,0)
                    robot.set_wheel(1,0)
                    robot.set_musical_note(0)
                elif (prox_l < 60 or prox_r < 60):
                    robot.set_wheel(0,100 - prox_l * 2)
                    robot.set_wheel(1,100 - prox_r * 2)
                    robot.set_musical_note((prox_l+prox_r)/2)  
                    #print("Don't run away from me!")
                    time.sleep(0.1)
                else:
                    robot.set_wheel(0,0)
                    robot.set_wheel(1,0)
                    robot.set_musical_note(0)
                    #print("Still following )")
                    time.sleep(0.1)
        time.sleep(0.5)
        return
        
    def dance(self):
        if (len(gRobotList) > 0):
            for robot in gRobotList:
                prox = robot.get_proximity(0)
                if (prox < 60):
                    robot.set_wheel(0,50)
                    robot.set_wheel(1,50)
                    #print("Going forward")
                    time.sleep(0.05)
                else:
                    robot.set_wheel(0,-50)
                    robot.set_wheel(1,-50)
                    #print("Going backward")
                    time.sleep(0.05)
        time.sleep(0.1)
        return

    def sing(self):
        tempo = 148
        if (len(gRobotList) > 0):
            for robot in gRobotList:
                robot.reset()

        file_name = raw_input("Input file name:")
        f = open('Output.txt','r')
        notes = []
        for line in f:
            line = line.strip()
            notes.append(line.split(" "))
        #print(str(notes))
        if (len(gRobotList) > 0):
            for robot in gRobotList:
                for note in notes:
                    robot.set_musical_note(int(note[0]))
                    time.sleep(0.6 * 60 / tempo * float(note[1]))
                    robot.set_musical_note(0)
                    time.sleep(0.4 * 60 / tempo * float(note[1]))

        time.sleep(0.01)
        return

    def Square(self, event=None):
        self.behavior = "Square"

    def Shy(self, event=None):
        self.behavior = "Shy"

    def Follow(self, event=None):
        self.behavior = "Follow"

    def Dance(self, event=None):
        self.behavior = "Dance"

    def Sing(self, event=None):
        self.behavior = 'Sing'
        

class GUI(object):
    def __init__(self, root, behaviors):
        self.root = root
        self.behaviors = behaviors
        self.initUI()

    def initUI(self):
        frame = self.root
        canvas = tk.Canvas(frame, bg="white", width=300, height=300)
        canvas.pack(expand=1, fill='both')
        canvas.create_rectangle(175, 175, 125, 125, fill="green")
  
        button0 = tk.Button(frame,text="Square")
        button0.pack(side='left')
        button0.bind('<Button-1>', self.behaviors.Square)

        button1 = tk.Button(frame,text="Shy")
        button1.pack(side='left')
        button1.bind('<Button-1>', self.behaviors.Shy)

        button2 = tk.Button(frame,text="Follow")
        button2.pack(side='left')
        button2.bind('<Button-1>', self.behaviors.Follow)

        button3 = tk.Button(frame,text="Dance")
        button3.pack(side='left')
        button3.bind('<Button-1>', self.behaviors.Dance)

        button4 = tk.Button(frame,text="Sing")
        button4.pack(side='left')
        button4.bind('<Button-1>', self.behaviors.Sing)

        button5 = tk.Button(frame,text="Exit")
        button5.pack(side='left')
        button5.bind('<Button-1>', self.stopProg)

    def stopProg(self, event=None):
        self.behaviors.gQuit = True
        for robot in gRobotList:
            robot.reset()
        time.sleep(0.5)
        self.behaviors.behavior_handle.join()
        self.root.quit()
        return

def main(argv=None):
    global gRobotList

    comm = RobotComm(gMaxRobotNum)
    comm.start()
    print 'Bluetooth starts'  
    gRobotList = comm.robotList

    behaviors = ThreadedBehaviors()
    
    frame = tk.Tk()
    # GUI(frame, behaviors)
    frame.mainloop()
    time.sleep(5)
    comm.stop()
    comm.join()

    print("terminated!")

if __name__ == "__main__":
    sys.exit(main())