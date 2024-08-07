# File: galton.py
# Author: Eve Andersson (eve@eveandersson.com)
# Date: August 2024
#
# This program implements the logic for the Galton Board design found at:
# https://www.bricklink.com/v3/studio/design.page?idModel=576118
#
# To run this program:
# (1) Download the LEGO Spike Prime app onto your computer.
# (2) Open a new project in Python mode.
# (3) Copy-paste in this code.
# (4) Connect a Spike Prime hub.
# (5) Run it! By default, this is set to run in simulation mode.
#
# More details:
# 
# This program can be run in simulation mode or connected to a physical Galton Board. In either case, a Spike Prime hub must be connected in order for it to run.
# 
# In simulation mode, you can specify the number of levels of your Galton Board you plan to implement, the number of balls you plan to use, and a probability
# from 0.0 to 1.0. This will run multiple simulations of the number of balls that will land in each bin, giving you an idea of how tall you need to make each bin.
#
# To use with a real Galton Board, you can modify constants if your design is different than the sample design.  This sample code implements a design with 2 hubs
# and 10 motors, 5 connected to each hub. If you also implement a 2 hub design, but with a different number or order of motors, just edit the constants
# TOP_MOTOR_ORDER and BOT_MOTOR_ORDER. If you want to make a larger Galton Board, you can add additional hubs and associated constants. Before loading code onto
# each of your hubs, update the constant MODE to give each hub the version that works with its motor configuration.

from spike import PrimeHub, LightMatrix, Button, StatusLight, ForceSensor, MotionSensor, Speaker, ColorSensor, App, DistanceSensor, Motor, MotorPair
from spike.control import wait_for_seconds, wait_until, Timer
from math import *
import random

MODE = "sim" # Can be "sim" (to run simulation), "top" (for top hub code), "reg" (for all other hubs). Even if it's a simulation, a hub needs to be connected for this to run.
P = 0.1
N = 10 # number of levels
B = 50 # number of balls for physical machine; controls the number of loops motors are run
B_SIM = 100 # number of balls for simulation
MOTOR_SPEED = 10
MOTOR_OPENING_DEGREES = 30
TOP_MOTOR_ORDER = ["C", "E", "B", "D", "F"]
BOT_MOTOR_ORDER = ["A", "C", "E", "B", "D"]

def bern():
    if random.uniform(0,1) < P:
        return 1
    return 0

def run_one_simulation():
    balls_in_bins = {}
    for bin in range(N + 1):
        # initialize each bin with zero balls
        balls_in_bins[bin] = 0

    # for each ball, determine which bin it lands in
    for ball in range(B_SIM):
        landing_bin = 0
        for level in range(N):
            landing_bin += bern() # increment the landing bin each time the ball is sent to the right on the given level
        balls_in_bins[landing_bin] += 1

    return(balls_in_bins)

if (MODE == "sim"):
    # run some simulations, print useful stats (builder will want to know how full [to avoid overflow] or empty [to not be sad-looking] their bins could be)
    n_sim = 10 # you can make this higher, but you'll have to be patient while it runs on a Spike Prime hub

    balls_in_bins_trials = {}
    for bin in range(N + 1):
        # initialize each bin with an empty list of trials
        balls_in_bins_trials[bin] = []

    for _ in range(n_sim):
        balls_in_bins = run_one_simulation()
        for bin in range(N + 1):
            balls_in_bins_trials[bin].append(balls_in_bins[bin])
    
    print("Number of balls in each bin, based on ", n_sim, " simulations:")

    for bin in range(N + 1):
        mean = sum(balls_in_bins_trials[bin])/len(balls_in_bins_trials[bin])
        maxval = max(balls_in_bins_trials[bin])
        minval = min(balls_in_bins_trials[bin])
        pos = "            " # f-string padding doesn't seem to work on this device, so this is a workaround for alignment
        if bin == 0:
            pos = "     Left "
        elif bin == N:
            pos = "   Right "
        print (pos, "Bin ", bin, ": Average:", round(mean, 1), ", Max:", maxval, ", Min:", minval)

else:
    hub = PrimeHub()
    hub.light_matrix.show_image('HEART') # so you'll know it's running

    if MODE == "top":
        motor_order = TOP_MOTOR_ORDER
        parity_start = 1
    else:
        motor_order = BOT_MOTOR_ORDER
        parity_start = 0

    initial_positions = {}
    for motor_id in motor_order:
        motor = Motor(motor_id)
        initial_positions[motor_id] = motor.get_position()

    print(initial_positions)

    if MODE == "top":
        # ball pump
        motor = Motor('A')
        motor.run_for_rotations(1)
    else:
        # allows you to manually synchonize timing with top hub
        hub.left_button.wait_until_pressed()

    ball_count = 0
    while ball_count < B:
        ball_count += 1
        row_count = 0
        for motor_id in motor_order:
            right = bern()
            row_count += 1
            parity = (parity_start + row_count)%2
            motor = Motor(motor_id)
            # to move the beam to the right, the motor has to go right on even rows and left on odd rows
            if ((right and not parity)) or (not right and parity):
                motor_pos = (initial_positions[motor_id] + MOTOR_OPENING_DEGREES)%360
            else:
                motor_pos = (initial_positions[motor_id] - MOTOR_OPENING_DEGREES)%360
            motor.run_to_position(motor_pos, direction="shortest path", speed=MOTOR_SPEED)

        wait_for_seconds(5)

        for motor_id in motor_order:
            motor = Motor(motor_id)
            motor.run_to_position(initial_positions[motor_id], direction="shortest path", speed=MOTOR_SPEED)

