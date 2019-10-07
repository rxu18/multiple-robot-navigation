'''
NAME: Richard Xu, Scott Bass
LANG: Python
TASK: Trash Cleaner
'''

'''
Using finite state machine to push the trash out. FSM is explained in more detail in Auto_Escape.
For the trash cleaner, there are four states: Forward, Left align, Right align, and Pushing.

'n' = nothing in front, 'l' = left side closer, 'r' = right side closer, 'e' = same distance, 'b' = black line
When it sees an obstacle during the Forward State,it would adjust by turning left/right to align with
the obstacle. Once it finishes aligning, indicated by an 'e', it would push it with a p-control to make sure it does
not lose the obstacle. When it reaches a black line, it would turn back at 60-120 degree from the black line, indicated
by uturn. It would beep if it's pushing an obstacle and get out.
'''
import time  # sleep
import threading
import Queue
import random
from HamsterAPI.comm_usb import RobotComm

robot = None

class StateMachine(object):
	def __init__(self, name, event_queue):
		self.name = name 	# machine name
		self.states = [] 
			# list of tuples, [(state name, event, transition, next_state), ...]

		self.start_state = None
		self.end_states = []
		self.q = event_queue

	def set_start_state(self, state_name):
		self.start_state = state_name

	def add_end_state(self, state_name):
		self.end_states.append(state_name)

	def add_state(self, state, event, transition, next_state):
		self.states.append((state, event, transition, next_state))
			# append to list
	
	# you must set start state before calling run()
	def run(self):
		current_state = self.start_state
		while True:
			if(self.q.empty()):
				continue
			event = self.q.get()
			for c in self.states:
				if c[0] == current_state and c[1] == event:
					current_state = c[3] 	# next state
					c[2]()
					time.sleep(0.05)
					break	# get out of for-loop

def move(l, r):
	global robot
	if (l > 100):
		 l = 100;
	if (r > 100):
		r = 100;
	robot.set_wheel(0, l)
	robot.set_wheel(1, r)

def move_forward():
	move(50, 50)
#1.75 - 180 degree
def uturn():
	move(30, -30);
	while (robot.get_floor(0) < 50 or robot.get_floor(1) < 50):
		time.sleep(0.01);
	time.sleep(random.randint(60, 120) * 0.009722);
	move(50, 50);
def uturn_beep():
	global robot
	move(0,0);
	robot.set_musical_note(88)
	time.sleep(0.5)
	robot.set_musical_note(0)
	uturn()

def turn_left():
	move(-30, 30)

def turn_right():
	move(30, -30);

def move_pid():
	l = robot.get_proximity(0);
	r = robot.get_proximity(1);
	print ("l = %d, r = %d" % (l, r));
	#if (l < 5):
	#	l = 90;
	#if (r < 5):
	#	r = 90;
	d = l - r;
	move(int(30 - 0.8 * d), int(30 + 0.8 * d));
def event_producer(q_handle):
	global robot
	while True:
		l = robot.get_proximity(0)
		r = robot.get_proximity(1)
		if robot.get_floor(0) < 50 or robot.get_floor(1) < 50:
			q_handle.put('b')
			time.sleep(3)
		elif (l < 60 and r < 60):
			q_handle.put('n')
		elif l - r < -10:
			q_handle.put('r')
		elif l - r > 10:
			q_handle.put('l')
		else:
			q_handle.put('e')
		time.sleep(0.1)
	return

def main():
	MAX_ROBOT = 8
	global robot

	# thread to scan and connect to robot
	comm = RobotComm(MAX_ROBOT)
	comm.start()
	print 'Bluetooth starts'
	robot = comm.robotList[0]

	q = Queue.Queue()
	t = threading.Thread(name='User', target=event_producer, args=(q,))
	t.start()
	sm = StateMachine('Trash Cleaning', q)
	# Populate FSM with ticket machine information in this format:
	# ('state name', 'event', 'action/callback', 'next state')
	sm.add_state('F', 'n', move_forward, 'F')
	sm.add_state('F', 'e', move_forward, 'P')
	sm.add_state('F', 'b', uturn, 'F')
	sm.add_state('F', 'l', turn_left, 'L')
	sm.add_state('F', 'r', turn_right, 'R')
	sm.add_state('L', 'n', move_forward, 'F')
	sm.add_state('L', 'e', move_forward, 'P')
	sm.add_state('L', 'b', uturn, 'F')
	sm.add_state('L', 'l', turn_left, 'L')
	sm.add_state('L', 'r', move_forward, 'P')
	sm.add_state('R', 'n', move_forward, 'F')
	sm.add_state('R', 'e', move_forward, 'P')
	sm.add_state('R', 'b', uturn, 'F')
	sm.add_state('R', 'l', move_forward, 'P')
	sm.add_state('R', 'r', turn_right, 'R')
	sm.add_state('P', 'n', move_pid, 'P')
	sm.add_state('P', 'e', move_pid, 'P')
	sm.add_state('P', 'b', uturn_beep, 'F')
	sm.add_state('P', 'l', move_pid, 'P')
	sm.add_state('P', 'r', move_pid, 'P')

	sm.set_start_state('F')

	# Create an instance of FSM
	t2 = threading.Thread(name='FSM', target=sm.run)
	t2.start()

if __name__== "__main__":
	main()

