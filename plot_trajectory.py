import matplotlib.pyplot as plt
from csv import reader
from dateutil import parser
from matplotlib import animation
import math
import numpy as np
import argparse
import os
import shutil

# Setup commandline argument(s) structures
ap = argparse.ArgumentParser(description='TODO')
ap.add_argument("--datalog", "-d", type=str, metavar='FILE', default='datalog-Fri_Jun__1_19-20-07_2018-0.txt', help="Name of video file to parse")
ap.add_argument("--trajectory", "-t", type=str, metavar='FILE', default='loaded_trajectory.otraj', help="Name of output file containing information about parsed video")
# Store parsed arguments into array of variables
args = vars(ap.parse_args())

# Extract stored arguments array into individual variables for later usage in script
_traj = args["trajectory"]
_datalog = args["datalog"]

cwd = os.getcwd()
print cwd

# # Change current directory to the specified home directory of the video of interest
# os.chdir(home)
# # Create the directories used to store the extracted data, if they haven't already been made
# if not os.path.exists("frames"):
# 	os.mkdir('frames')
# if not os.path.exists("data"):
# 	os.mkdir('data')

trajRoot = os.path.dirname(_traj)
trajFileName = os.path.splitext(os.path.basename(_traj))
logRoot = os.path.dirname(_datalog)
logFileName = os.path.splitext(os.path.basename(_datalog))

if trajFileName[1] != '.csv':
	newTrajPath = str(cwd) + "/" + str(trajFileName[0]) + ".csv"
	shutil.copy2(_traj, newTrajPath)
	# print "New Path",newTrajPath

if logFileName[1] != '.csv':
	newLogPath = str(cwd) + "/" + str(logFileName[0]) + ".csv"
	shutil.copy2(_datalog, newLogPath)
	# print "New Path",newLogPath

logInputs = np.genfromtxt(newLogPath, delimiter=',',skip_header=2)
trajInputs = np.genfromtxt(newTrajPath, delimiter=' ', skip_header=1)
# print logInputs.shape
# print trajInputs.shape

fig = plt.figure()
line = fig.add_subplot(2,1,1)
err = fig.add_subplot(2,1,2)

time = 		logInputs[:,1]
x = 		logInputs[:,10]
y = 		logInputs[:,11]
yaw = 		logInputs[:,32]
actx = 		logInputs[:,14]
acty = 		logInputs[:,15]
actyaw = 	logInputs[:,32]
errx = 		logInputs[:,7]
erry =		logInputs[:,8]
errAbs = 	logInputs[:,9]
lat = 		logInputs[:,22]
lon = 		logInputs[:,23]

refTrajx = trajInputs[:,0]
refTrajy = trajInputs[:,1]

line.clear()
line.plot(y, x,color='r',label='GPS Trajectory')
line.plot(acty,actx,color='b',label='MHE Trajectory')
line.plot(refTrajy,refTrajx,color='g',label='Reference Trajectory')
line.legend(loc="best")
line.set_title('Position')
line.set_xlabel('X (m)')
line.set_ylabel('Y (m)')
line.axis('equal')
line.autoscale()

err.clear()
err.plot(range(len(errAbs)), errAbs,'b',label='Trajectory Error')
err.legend(loc="best")
err.set_title('Absolute Error')
err.set_xlabel('Time (s)')
err.set_ylabel('Error')
err.autoscale()

plt.show()
