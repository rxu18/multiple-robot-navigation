'''
/* =======================================================================
	(c) 2015, Kre8 Technology, Inc.

	Starter Code for FSM Applications

	By:				Qin Chen, Richard Xu, Scott Bass
	Last Updated:	6/10/16

	PROPRIETARY and CONFIDENTIAL
=========================================================================*/
'''
'''
Using finite state machine to navigate a maze. To read more about it, just go to wikipedia
or try out the droid_maintainance puzzle. It's basically a clearer way to represent a bunch
of if statements.
For this, we have four states: Forward, Turning Left, Turning Right, Black Line.
Forward means you're moving forward. If one sees an obstacle in the forward state, it would
switch to Left or Right, whichever one it thinks would be faster to get out. e.g. If the left
sensor reads a higher value, i.e. the obstacle's closer on the left side, it would turn right
to avoid it.
Now, on left/right, it would keep turning that direction until it gets out. This is so that it
does not get stuck turning left and right over and over again if the robot is between two obstacles,
like this:
					 \
           _________  \
           |       |   \
           |       |   /
           _________  /
                     /
  A bad drawing of the hamster and obstacle.

@Scott: It was amazing working with you. You're a really good partner.
'''
import time  # sleep
import threading
import Queue
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
                    break  # get out of for-loop
            if(current_state == "B"):
                break


def move(left, right):
    global robot
    robot.set_wheel(0, left)
    robot.set_wheel(1, right)


def move_right():
    move(30, -30)


def move_left():
    move(-30, 30)


def move_forward():
    move(30, 30)


def happy_day():
    global robot
    move(0, 0)
    robot.set_musical_note(30)
    time.sleep(2)


def event_producer(q_handle):
    global robot
    while True:
        l = robot.get_proximity(0)
        r = robot.get_proximity(1)
        if robot.get_floor(0) < 50 or robot.get_floor(1) < 50:
            q_handle.put('b')
            break
        elif (l < 60 and r < 60):
            q_handle.put('n')
        elif l < r:
            q_handle.put('r')
        else:
            q_handle.put('l')
        time.sleep(0.1)
    return


if __name__ == "__main__":
    global robot
    MAX_ROBOT = 1
    comm = RobotComm(MAX_ROBOT)
    comm.start()
    print 'Bluetooth starts'
    robot = comm.robotList[0]
    q = Queue.Queue()
    t = threading.Thread(name='User', target=event_producer, args=(q,))
    t.start()

    # Create an instance of FSM
    sm = StateMachine('Escape', q)

    # Populate FSM with ticket machine information in this format:
    # ('state name', 'event', 'action/callback', 'next state')
    sm.add_state('F', 'n', move_forward, 'F')
    sm.add_state('F', 'r', move_left, 'L')
    sm.add_state('F', 'l', move_right, 'R')
    sm.add_state('F', 'b', happy_day, 'B')
    sm.add_state('L', 'r', move_left, 'L')
    sm.add_state('L', 'l', move_left, 'L')
    sm.add_state('L', 'n', move_forward, 'F')
    sm.add_state('L', 'b', happy_day, 'B')
    sm.add_state('R', 'r', move_right, 'R')
    sm.add_state('R', 'l', move_right, 'R')
    sm.add_state('R', 'n', move_forward, 'F')
    sm.add_state('R', 'b', happy_day, 'B')

    sm.set_start_state('F')  # this must be done before starting machine
    t = threading.Thread(name='FSM', target=sm.run)
    t.start()
