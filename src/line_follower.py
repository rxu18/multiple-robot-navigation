import sys # i.e. the system
import time # to sleep and wait
import threading # for thrading
import Tkinter as tk # GUI
from HamsterAPI.comm_usb import RobotComm
'''
First, notice the use of lambda method instead of many method with the similar function. This is to save space as the previous versions
have many functions that do similar stuff. Surprisingly, we can not just do args = "Bang" or something to make it work according to 
Tkinter documentation. Oh well...

Let me explain what a PID controller is: it is a close-looped control system to correct errors. It works best for things like air conditioners,
but it's still good for hamster line following.
PID stands for Proportion-Integral-Derivative. In short, f(t) = a*e(t) + b*integral_0^t e(x) dx + c*d/dx d(x), where e(t) is the error at time t, and
f is how much it's tring to correct by. Often a P-controller is enough. Let me explain intuitively how this works:
Proportion: when there's a big error, we obviously want to correct it more.
Integral: if it hasn't been fixed by a while, that means the problem is bigger than expected. We better try harder!
Derivative: If suddenly the error spikes, another factor might have been introduced that causes the error, so we try hard to balance it.
a, b, c are constants, and there are really no good ways to find them other than trial-and-error.

'''
interval = 20
error = [0] * (interval / 2)
#If dif>0, it'll be turning left, and vice versa.
def setWithDif(robot, dif):
        if (dif != 0):
            robot.set_wheel(0, 20-dif)
            robot.set_wheel(1, 20+dif)
        else:
            robot.set_wheel(0, 30)
            robot.set_wheel(1, 30)
class Controller(object):
    #Initializer
    def __init__(self):
        self.behavior = 'Pause'
        self.quit = False
        self.done = False
        t = threading.Thread(target = self.controller)
        t.daemon = True
        t.start()
        self.controller_thread = t
        return

    #Determines which method gets implemented
    def controller(self):
        while not self.quit:
            if (self.behavior == "Bang"):
                self.bang()        #Done!
            elif (self.behavior == "3Pos"):
                self.threePos()    #Done!
            elif (self.behavior == "P-C"):
                self.pControl()    #Basics there.
            elif (self.behavior == "PID"):
                self.pid()         #Basics there.
            elif (self.behavior == "Pause"):
                self.pause()       #Done!
            else:
                print("Wait... What program is this?")
        print("And we're done!")
        return

    def setB(self, phrase = "Pause"):
        self.behavior = phrase

    #Main part of the program

    def pause(self):
        if len(gRobotList) > 0:
            for robot in gRobotList:
                robot.set_wheel(0,0)
                robot.set_wheel(1,0)
                robot.set_musical_note(0)
        time.sleep(0.1)
        return       
    
    #Binary movement, where it either turns left or turns right.
    def bang(self):
        if len(gRobotList) > 0:
            for robot in gRobotList:
                floor_l = robot.get_floor(0)
                floor_r = robot.get_floor(1)
                #print('l = %d, r = %d' % (floor_l, floor_r))
                if floor_r > floor_l:
                    setWithDif(robot, 10)
                    #print("Turning Left!")
                else:
                    setWithDif(robot, -10)
                    #print("Turning Right!")
                time.sleep(0.2)
        return

    #Trinary movement, i.e. left/right turn plus doing nothing.
    def threePos(self):
        if len(gRobotList) > 0:
            for robot in gRobotList:
                l = robot.get_floor(0)
                r = robot.get_floor(1)
                #print("l = %d, r = %d", %(l, r))
                dif = r - l
                if dif > 60:
                    setWithDif(robot, 10)
                    #print("Turning Left!")
                elif dif < -60:
                    setWithDif(robot, -10)
                    #print("Turning Right!")
                else:
                    setWithDif(robot, 0)
                    #print("Not turning.")  
                time.sleep(0.2)
        return

    # P-control system with left sensor.
    def pControl(self):
        global interval
        if len(gRobotList) > 0:
            for robot in gRobotList:
                f = robot.get_floor(0)
                #print("Left floor reading: %d" % (f))
                #if (f >= 80 or f <= 20): #When it's in black or white
                setWithDif(robot, int(1.3 * (f - 50)))
                #else:
                #    setWithDif(robot, 0)
                time.sleep(1.0 / interval)
        return
    
    # P-Control system with both sensors. It cannot work with sharp turns, however.
    def pControl2(self):
        if len(gRobotList) > 0:
            for robot in gRobotList:
                l = robot.get_floor(0)
                r = robot.get_floor(1)
                d = r-l
                #print("l = %d, r = %d d = %d" % (l, r, d))
                if (d > 50 or d < -50): #When it's in black or white
                    setWithDif(robot, d)
                    #print("Turning!")
                else:
                    setWithDif(robot, 0)
                time.sleep(1.0 / interval)
        return

    # PID system.
    def pid(self):
        global interval
        global error
        if len(gRobotList) > 0:
            for robot in gRobotList:
                l = robot.get_floor(0)
                r = robot.get_floor(1)
                d = r-l
                s = 0
                for n in error:
                    s += n
                print("l = %d, r = %d, s = %d" % (l, r, s))
                error.append(d)
                error.pop(0)
                change = max(min(int(d + 0.05 * s), 79),-79)
                setWithDif(robot, change)
                print(error)
                time.sleep(1.0 / interval)
        return

#GUI
class GUI(object):
    def __init__(self, root, behaviors):
        self.root = root
        self.behaviors = behaviors
        self.initUI()

    #Buttons!
    def initUI(self):
        frame = self.root
        frame.geometry('350x200')
  
        bBang = tk.Button(frame,text="Bang")
        bBang.pack(side='left')
        bBang.bind('<Button-1>', lambda x: self.behaviors.setB("Bang"))

        b3 = tk.Button(frame,text="3Pos")
        b3.pack(side='left')
        b3.bind('<Button-1>', lambda x: self.behaviors.setB("3Pos"))

        bPC = tk.Button(frame, text="P-C")
        bPC.pack(side = 'left')
        bPC.bind('<Button-1>', lambda x: self.behaviors.setB("P-C"))
        
        bPID = tk.Button(frame, text = "PID")
        bPID.pack(side = 'left')
        bPID.bind('<Button-1>', lambda x: self.behaviors.setB("PID"))

        bP = tk.Button(frame, text = "Pause")
        bP.pack(side = 'left')
        bP.bind('<Button-1>', lambda x: self.behaviors.setB("Pause"))

        bE = tk.Button(frame,text="Exit")
        bE.pack(side='left')
        bE.bind('<Button-1>', self.stopProg)

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
    behaviors = Controller()
    frame = tk.Tk()
    GUI(frame, behaviors)
    frame.mainloop()
    comm.stop()
    comm.join()
    print("terminated!")

#Terminate the program when exit.
if __name__ == "__main__":
    sys.exit(main())