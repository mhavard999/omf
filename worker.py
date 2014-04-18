
'''
Work executes python functions. It can use the local machine or the omf.coop cluster.

One queue, stores tuples (analysisName, requestType). Or maybe have two queues, whatever.

Adding jobs.
	Put (analysisName, 'toRun') on the queue.
	If that analysis is already on the queue, return failed.
	Update the DB to say queued.
Running jobs.
	Every 1(?) second, all nodes check the queue.
	If there's a toRun there, and we're not full, pop one.
	Start the job.
	Update DB to say queued.
Canceling jobs.
	Every 1(?) second, all nodes check the queue.
	If there's a toKill there, and we're running that analysisName, pop one.
	Kill the PID.

Queue limits?

We need to handle two cases:
1. Filesystem case. Just have a dumb fileQueue class that has no limits, etc.?
2. S3 cluster case. Have a cluterQueue class, and also have a daemon.
'''

import os, tempfile, time
from multiprocessing import Value, Lock
from threading import Thread, Timer
import studies, analysis, milToGridlab
import helperfuncs as hlp

JOB_LIMIT = 1

class MultiCounter(object):
	def __init__(self, initval=0):
		self.val = Value('i', initval)
		self.lock = Lock()
	def increment(self):
		with self.lock:
			self.val.value += 1
	def decrement(self):
		with self.lock:
			self.val.value -= 1
	def value(self):
		with self.lock:
			return self.val.value

runningJobCount = MultiCounter(0)

newFeederWireframe = {'links':[],'hiddenLinks':[],'nodes':[],'hiddenNodes':[],'layoutVars':{'theta':'0.8','gravity':'0.01','friction':'0.9','linkStrength':'5','linkDistance':'5','charge':'-5'}}

def milImportBackground(self, owner, feederName, stdString, seqString):
	newFeeder = dict(**newFeederWireframe)
	[newFeeder['tree'], xScale, yScale] = milToGridlab.convert(stdString, seqString)
	newFeeder['layoutVars']['xScale'] = xScale
	newFeeder['layoutVars']['yScale'] = yScale
	with open('./schedules.glm','r') as schedFile:
		newFeeder['attachments'] = {'schedules.glm':schedFile.read()}
	hlp.feederDump(owner, feederName, newFeeder)
	
def milImport(owner, feederName, stdString, seqString):
		# Setup.
		runningJobCount.increment()
		importThread = Thread(target=milImportBackground, args=[owner, feederName, stdString, seqString])
		importThread.start()
		runningJobCount.decrement()
