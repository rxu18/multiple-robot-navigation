'''
/* =======================================================================
   (c) 2015, Kre8 Technology, Inc.

   Written By Richard Xu and Drs. David Zhu, Qin Chen

   Last updated: May 28th, 2016

   PROPRIETARY and CONFIDENTIAL
   ========================================================================*/
'''

'''
As the first assignment, I am not yet familiar with the hamster enough to do whatever I want with it. Therefore, I didn't write most of the code.
Looking back, a lot of the starter code can be compressed down, which you'll start to see in future version.

I'll explain how HamsterAPI.comm works, in case you come from Praticle Physics! BTW email qin_chen99@yahoo.com if you want to buy a hamster.
There are two versions for HamsterAPI.comm: comm_ble and comm_usb. comm_usb needs a dongle, while comm_ble needs a special bluetooth service, but
most computers in the recent couple of years have it. There might be other stuff in there, but since it's compiled we cannot see it (unless you use
a decompiler... But I heard it's actually mostly just sending technical serial number stuff between the robot) just do from HamsterAPI.comm_(usb/ble)
import RobotComm.
Then, you do comm = RobotComm(MAX_ROBOT), where comm and MAX_ROBOT are variable names. MAX_ROBOT tell the computer when to stop getting more robots
to connect. Then, you call comm.start(), and it'll start trying to connect robots. For example, if MAX_ROBOT = 2, it will try to connect 2 robots to
the program and then stop trying. The robots will be stored in comm.robotList(), which would contain a list of the robots, each with methods as documented
in RobotAPI.
Some tricky things though: Each dongle can only connect to one hamster, and multiple dongles really don't work well. i.e. don't use dongle for >1 robot.
However, the RobotComm for comm_ble will only start working when you have a Tkinter root on mainloop(), which also halts the program until the window is
closed. Therefore, it's suggested that you do most of the work in another Thread when working with comm_ble

Oh yes. The robots can also sing. How do they do that? Let me explain.
open(name of file, 'r') generates a file reader. Doing "for line in f" takes each of the lines of the file and loop through them in a for each loop. Now,
the lines will contain a newline character in the end, which is removed with the strip() command.
Then, we use split(' ') to tokenize the line. Each line will contain the note, with 1 = Middle C, and the duration of the notes in beats. Then, we just make
the hamsters play!
'''
import sys
import time  # sleep
import Tkinter as tk
from threading import Thread
from HamsterAPI.comm_ble import RobotComm
#from HamsterAPI.comm_usb import 

tempo = 200
def main():
	robots = comm.robotList
	while len(robots) < 1:
		robots = comm.robotList
		print "Waiting..."
		time.sleep(1)
	print "We're ready!"
	f = open('Song.txt','r');
	notes = [];
	for line in f:
		line = line.strip();
		notes.append(line.split(" "));
	print(str(notes));
	robot = robots[0]
	for note in notes:
		robot.set_musical_note(int(note[0]) + 39);
		time.sleep(0.6 * 60 / tempo * float(note[1]));
		robot.set_musical_note(0);
		time.sleep(0.4 * 60 / tempo * float(note[1]));

	time.sleep(0.01);

comm = RobotComm(1)
comm.start()
t = Thread(target = main)
t.deamon = True
t.start()
root = tk.Tk()
root.mainloop()