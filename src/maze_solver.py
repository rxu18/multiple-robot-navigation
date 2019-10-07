import sys # i.e. the system
import time # to sleep and wait
import threading # for thrading
import Tkinter as tk # GUI
from HamsterAPI.comm_usb import RobotComm # Hamster!
wait = 0.549;

'''
A maze solver that does not always work! I'll make one with SLAM some day. In fact, I had the idea of a SLAMon Day 3/4, which Robin can confirm and also
seen by the fact that I made a "Advanced Mazefinding Project" on day 4. That turns out to be a lot more difficult than anything I've done, so I haven't
finished it yet.
For this code, it checks when it comes close to a wall whether or not to make a left, right or u-turn, with right>left>uturn
Also, a comment about semicolons: I know they aren't necessary, but I write mostly Java/C++ code, and they all use semicolons. Now it's like a habit for
me. They won't cause any trouble as long as the line isn't supposed to end with a colon. I do drop semicolons after a while to match the python style, and
now I sometimes forget them when writing Java/C++ code :P Well, at least those languages have a compiler, so it'll catch these stupid mistakes.
'''
def turnR(robot):
    global wait;
    robot.set_wheel(0,50);
    robot.set_wheel(1,-50);
    time.sleep(wait);
    robot.set_wheel(0,0);
    robot.set_wheel(1,0);
    time.sleep(0.5);

class Controller(object):
    #Initializer
    def __init__(self):
        self.behavior = 'Pause';
        self.quit = False;
        self.done = False;
        t = threading.Thread(target = self.controller);
        t.daemon = True;
        t.start();
        self.controller_thread = t;
        return;

    #Determines which method gets implemented
    def controller(self):
        while not self.quit:
            if (self.behavior == "Debug"):
                self.debug();
            elif (self.behavior == "Maze"):
                self.maze();
            elif (self.behavior == "Pause"):
                self.pause();       #Done!
            else:
                print("Wait... What program is this?");
        print("And we're done!");
        return;

    def setB(self, phrase = "Pause"):
        self.behavior = phrase;

    #Main part of the program

    def debug(self):
        if len(gRobotList) > 0:
            for robot in gRobotList:
                print("Left sensor: %d, Right Sensor: %d" % (robot.get_proximity(0), robot.get_proximity(1)));
                time.sleep(1);

    def maze(self):
        if len(gRobotList) > 0:
            for robot in gRobotList:
                if robot.get_proximity(0) < 70:
                    #Nothing in front. Keep driving!
                    robot.set_wheel(0, 30);
                    robot.set_wheel(1, 30);
                else:
                    #Oh no! A wall! What do we do?
                    wall = [False] * 3;
                    for i in range(3):
                        turnR(robot);
                        print("Proximity for %d is %d" % (i, robot.get_proximity(0)));
                        if (robot.get_proximity(0) >= 50):
                            wall[i] = True;
                            print("wall[%d] is true!" % (i));
                    print(str(wall));
                    if not wall[0]:
                        print("Making a right turn");
                        turnR(robot);
                        turnR(robot);
                    elif not wall[2]:
                        print("Making a left turn");
                    elif not wall[1]:
                        print("Making a U-turn");
                        for i in range(3):
                            turnR(robot);
                    else:
                        print("I'm trapped! Heeelp me!");
        time.sleep(0.01);

    def pause(self):
        if len(gRobotList) > 0:
            for robot in gRobotList:
                robot.set_wheel(0,0);
                robot.set_wheel(1,0);
                robot.set_musical_note(0);
        time.sleep(0.1);
        return

#GUI
class GUI(object):
    def __init__(self, root, behaviors):
        self.root = root;
        self.behaviors = behaviors;
        self.initUI();

    #Buttons!
    def initUI(self):
        frame = self.root;
        frame.geometry('300x200');
        bD = tk.Button(frame, text = "Debug");
        bD.pack(side = 'left');
        bD.bind('<Button-1>', lambda x : self.behaviors.setB("Debug"));

        bM = tk.Button(frame, text = "Maze");
        bM.pack(side = 'left');
        bM.bind('<Button-1>', lambda x : self.behaviors.setB("Maze"));

        bP = tk.Button(frame, text = "Pause");
        bP.pack(side = 'left');
        bP.bind('<Button-1>', lambda x : self.behaviors.setB("Pause"));

        bE = tk.Button(frame,text="Exit");
        bE.pack(side='left');
        bE.bind('<Button-1>', self.stopProg);

    def stopProg(self, event=None):
        self.behaviors.quit = True;
        self.behaviors.done = True;
        for robot in gRobotList:
            robot.reset();
        self.behaviors.controller_thread.join();
        self.root.quit();
        return

# main, where we run the code.
gMaxRobotNum = 1;
gRobotList = [];
def main(argv=None):
    # instantiate COMM object
    global gRobotList;
    comm = RobotComm(gMaxRobotNum);
    comm.start();
    print("Bluetooth,Start!");
    gRobotList = comm.robotList;
    behaviors = Controller();
    frame = tk.Tk();
    GUI(frame, behaviors);
    frame.mainloop();
    comm.stop();
    comm.join();
    print("terminated!");

#Terminate the program when exit.
if __name__ == "__main__":
    sys.exit(main());