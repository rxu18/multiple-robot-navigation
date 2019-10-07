'''
A quick attempt to get multiple robots. Took a bit of work, but we found that the Tkinter
frame is the most important part :)
'''
from HamsterAPI.comm_ble import RobotComm
import Tkinter as tk
import threading
import time

comm = RobotComm(2)
comm.start()

def main():
	global comm
	while True:
		print 'while'
		if len(comm.robotList) > 1:
			comm.robotList[0].set_wheel(0,30)
			comm.robotList[1].set_wheel(0,30)
			print 'yo'
		time.sleep(2)
t = threading.Thread(target = main)
t.daemon  = True
t.start()
while True:
	pass
# frame = tk.Tk()
# frame.mainloop()