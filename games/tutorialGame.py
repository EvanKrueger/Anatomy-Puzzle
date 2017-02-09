# Builtin
import csv
import time, datetime
import random

# Vizard
import viz
import vizact
import vizinfo, vizdlg
import vizproximity
import viztask
import vizshape
import vizmat

import csv
import time
import datetime
import random

#custom
import init
import menu
import config
import model
import menu
import puzzleGame

class InterfaceTutorial(object):
	"""
	This game mode is intended to instruct novice users in the use of the SpaceMouse
	interface hardware. The mechanics of this tutorial are heavily inspired by the
	'teapot trainer' tutorial that ships with the SpaceMouse device.
	"""
	def __init__(self, dataset):
		
		self.trial = model.trial
		self.moveFunc = self.transform()
		
		self.snapFlag = False
		self.proxList = []
		self.gloveLink = None
		self.snapTransitionTime = 0.3
		self.animateOutline = 1.25
		self.tasks = viztask.Scheduler
		self.recordData = TutorialData()
		
		
		sf = 0.2
#		model.pointer.setEuler(0,0,0)
		model.pointer.setPosition(0,0,0)
		self.gloveStart = model.pointer.getPosition()
		self.iterations = 0
		self.origPosVec = config.SMPositionScale
		self.origOrienVec = config.SMEulerScale
		
		
		#creating tutorial objects
		self.dog = viz.addChild('.\\dataset\\dog\\dog.obj')
#		self.dog.setCenter(0,1,0)
		self.dogStart = self.dog.getPosition()
		self.dog.setScale([sf,sf,sf])
		self.startColor = model.pointer.getColor()
		
		#creating dog outline
		self.dogOutline = viz.addChild('.\\dataset\\dog\\dog.obj')
		self.dogOutline.setScale([sf,sf,sf])
		self.dogOutline.alpha(0.8)
		self.dogOutline.color(0,5,0)
		self.dogOutline.texture(None)

		#creating proximity manager
		self.manager = vizproximity.Manager()
		
		'''creating dog grab and snap sensors around sphere palced in the center of the dog'''
		self.dogCenter = vizshape.addSphere(0.1*sf, pos = (self.dogStart))
		self.outlineCenter = vizshape.addSphere(0.1*sf, pos = (self.dogStart))
		
		'''			EVAN LOOK HERE			'''
		''' SETTING PROXIMITY SENSORS ABOVE DOG ORIGIN SO AS TO ENCOMPASS DOG'''
		self.dogCenter.setPosition([[x,y+0.5,z] for x,y,z in [self.dog.getPosition()]][0])
		self.outlineCenter.setPosition([[x,y+0.5,z] for x,y,z in [self.dog.getPosition()]][0])

		self.centerStart = self.dogCenter.getPosition()
		self.dogGrab = viz.link(self.dogCenter, self.dog)
		self.outlineGrab = viz.link(self.outlineCenter, self.dogOutline)

		self.dogCenter.color(5,0,0)
		self.outlineCenter.color(0,5,0)
		self.dogCenter.visible(viz.ON)
		self.outlineCenter.visible(viz.ON)
		
		self.dogSnapSensor = vizproximity.Sensor(vizproximity.Sphere(0.7*sf, center = [0,0,0]), source = self.dogCenter)
		self.manager.addSensor(self.dogSnapSensor)
		self.dogGrabSensor = vizproximity.Sensor(vizproximity.Sphere(1.7*sf, center = [0,0.25,0]), source = self.dogCenter)
		self.manager.addSensor(self.dogGrabSensor)
		
		'''creating glove target and a dog target. the dog target is a sphere placed at the center of the dog outline'''
		self.gloveTarget = vizproximity.Target(model.pointer)
		self.manager.addTarget(self.gloveTarget)
		self.dogTargetMold = vizshape.addSphere(0.2,parent = self.dogOutline, pos = (self.dogStart))
		self.dogTargetMold.setPosition([0,0,0])
		self.dogTargetMold.visible(viz.OFF)
		self.dogTarget = vizproximity.Target(self.dogTargetMold)
		self.manager.addTarget(self.dogTarget)
		
		#manager proximity events
		self.manager.onEnter(self.dogGrabSensor, self.EnterProximity)
		self.manager.onExit(self.dogGrabSensor, self.ExitProximity)
		self.manager.onEnter(self.dogSnapSensor, self.snapCheckEnter)
		self.manager.onExit(self.dogSnapSensor, self.snapCheckExit)
		
		#reset command
		self.keybindings = []
		self.keybindings.append(vizact.onkeydown('l', self.resetGlove))
		self.keybindings.append(vizact.onkeydown('p', self.debugger))
		
		#task schedule
		self.interface = viztask.schedule(self.interfaceTasks())
		self.gameMechanics = viztask.schedule(self.mechanics())
	
	def resetPos(self):
		self.outlineCenter.setEuler(0,0,0)
		self.outlineCenter.setPosition(0,0.5,0)
		self.dogCenter.setEuler(0,0,0)
		self.dogCenter.setPosition(0,0.5,0)
	# EVAN
	def transform(self):
		trialNum = self.trial
		# seed the pseudo-random number generator with trial number
		# (ensures each participant gets same "random" sequence for
		# each trial number)
		random.seed(trialNum)
		
		# create dictionaries once per trial
		movements = {
				'x2' : [0.5, 0.5, 0.0],
				'x3' : [1.0, 0.5, 0.0],
				'x4' : [-0.5, 0.5, 0.0],
				'x5' : [-1.0, 0.5, 0.0],
				
				'y1' : [0.0, 0.0, 0.0],
				'y2' : [0.0, 0.25, 0.0],
				'y4' : [0.0, 0.75, 0.0],
				'y5' : [0.0, 1.0, 0.0],
				
				'z2' : [0.0, 0.5, 0.5],
				'z3' : [0.0, 0.5, 1.0],
				'z4' : [0.0, 0.5, -0.5],
				'z5' : [0.0, 0.5, -1.0],
				}
#		movements = {
#				'x1' : [0.0, 0.5, 0.0],
#				'x2' : [0.5, 0.5, 0.0],
#				'x3' : [1.0, 0.5, 0.0],
#				'x4' : [-0.5, 0.5, 0.0],
#				'x5' : [-1.0, 0.5, 0.0],
#				
#				'y1' : [0.0, 0.0, 0.0],
#				'y2' : [0.0, 0.25, 0.0],
#				'y3' : [0.0, 0.50, 0.0],
#				'y4' : [0.0, 0.75, 0.0],
#				'y5' : [0.0, 1.0, 0.0],
#				
#				'z1' : [0.0, 0.5, 0.0],
#				'z2' : [0.0, 0.5, 0.5],
#				'z3' : [0.0, 0.5, 1.0],
#				'z4' : [0.0, 0.5, -0.5],
#				'z5' : [0.0, 0.5, -1.0],
#				}
		orientations = {
				'x1' : [-90, 0, 0],
				'x2' : [-45, 0, 0],
				'x4' : [45, 0, 0],
				'x5' : [90, 0, 0],
				
				'y1' : [0, -90, 0],
				'y2' : [0, -45, 0],
				'y4' : [0, 45, 0],
				'y5' : [0, 90, 0],
				
				'z1' : [0, 0, -90],
				'z2' : [0, 0, -45],
				'z4' : [0, 0, 45],
				'z5' : [0, 0, 90],
		}
#		orientations = {
#				'x1' : [-90, 0, 0],
#				'x2' : [-45, 0, 0],
#				'x3' : [0, 0, 0],
#				'x4' : [45, 0, 0],
#				'x5' : [90, 0, 0],
#				
#				'y1' : [0, -90, 0],
#				'y2' : [0, -45, 0],
#				'y3' : [0, 0, 0],
#				'y4' : [0, 45, 0],
#				'y5' : [0, 90, 0],
#				
#				'z1' : [0, 0, -90],
#				'z2' : [0, 0, -45],
#				'z3' : [0, 0, 0],
#				'z4' : [0, 0, 45],
#				'z5' : [0, 0, 90],
#				}
		
		def randomTransform():
			if trialNum == 1:
				positions = movements.pop(random.choice(movements.keys()))
				angles = [0, 0, 0]
			elif trialNum == 2:
				positions = [0.0, 0.5, 0.0]
				angles = orientations.pop(random.choice(orientations.keys()))
#				angles = orientations.pop(sorted(orientations.keys())[0])
			elif trialNum == 3:
				positions = movements.pop(random.choice(movements.keys()))
				angles = orientations.pop(random.choice(orientations.keys()))
			return positions, angles
				
		return randomTransform


	def load(self, dataset):
		'''Accept dataset, but do nothing with it'''
		pass

	def debugger(self):
		"""
		Activates debuggin' tools
		"""
		self.manager.setDebug(viz.TOGGLE)
		if self.dogCenter.getVisible() == viz.ON:
			self.dogCenter.visible(viz.OFF)
			self.outlineCenter.visible(viz.OFF)
			self.dogTargetMold.visible(viz.OFF)
		else:
			self.dogCenter.visible(viz.ON)
			self.outlineCenter.visible(viz.ON)
			self.dogTargetMold.visible(viz.ON)
			
	def interfaceTasks(self):
		"""
		Grab and Release task. viztask was used to make grab and release dependent on the occurence of one another.
		In order for a release there must have been a grab and vice versa.
		"""

		while True:
			yield viztask.waitKeyDown(' ')
			self.grab()
			yield viztask.waitKeyUp(' ')
			self.release()

	def end(self):
		"""
		CLEANUP TUTORIAL
		"""
		print 'ending'
		viztask.Task.kill(self.interface)
		viztask.Task.kill(self.gameMechanics)
		self.manager.clearSensors()
		self.manager.clearTargets()
		self.manager.remove()
		self.dog.remove()
		self.dogOutline.remove()
		self.dogCenter.remove()
		self.outlineCenter.remove()
		self.dogTargetMold.remove()
		self.iterations = 0
		# EVAN: no wonder I can never find the pointer
		model.pointer.setParent(model.display.camcenter)
		model.pointer.setPosition([0,1,0])
		self.proxList = []
		self.gloveLink = None
		self.recordData.close()
		for bind in self.keybindings:
			bind.remove()
			
	def mechanics(self):
		"""tutorial mechanics: moves the dog outline around the environment and waits for the dog to be snapped to it
		before preforming the next action."""
		
		#Move back to start position and angle
#		self.resetPos()
#		movePos = vizact.moveTo((0,0.5,0), time = self.animateOutline)
#		moveAng = vizact.spinTo((0,0,0), time = self.animateOutline)
#		transition = vizact.parallel(movePos, moveAng)
#		self.outlineCenter.addAction(transition)
		
#		#EVAN LOOK HERE: SETS POSITIONS OF DOGS
#		randomPos = [1*(random.random()-0.5),abs(1*(random.random()-0.5)),2*(random.random()-0.5)]
#		randomEuler = [random.randint(-90,90),random.randint(-90,90),random.randint(-90,90)]
		randomPos, randomEuler = self.moveFunc()
		
		#CHANGE RESULT TO TRIAL TYPE
		self.recordData.event(event = self.trial, result = 'MOVE SOMEWHERE AND SOMETHING', x = randomPos[0], y = randomPos[1], z = randomPos[2])
		self.movePos = vizact.moveTo(randomPos, time = self.animateOutline)
		self.moveAng = vizact.spinTo(euler = randomEuler, time = self.animateOutline, mode = viz.ABS_GLOBAL)
		transition = vizact.parallel(self.movePos, self.moveAng)
		yield viztask.waitTime(1)
		self.outlineCenter.addAction(transition)
		self.iterations = self.iterations+1
		if self.iterations == 12:
			self.recordData.event(event = 'FINISHED', result = 'FINISHED')
			self.end()
	def resetGlove(self):
		#move glove to starting position
		model.pointer.setPosition(self.gloveStart)

	def EnterProximity(self, e):
		"""
		If the target entering the proximity is the gloveTarget, and the gloveTarget is active
		then add the source of the proximity sensor to self.proxList
		
		"""
		"""@args vizproximity.ProximityEvent()"""
		source = e.sensor.getSourceObject()
		target = e.target.getSourceObject()
		targets = e.manager.getActiveTargets()
		print self.iterations
		if target == model.pointer:
			for t in targets:
				if t == self.gloveTarget:
					model.pointer.color(4,1,1)
					self.proxList.append(source)

	def ExitProximity(self, e):
		"""
		If the target leaving the proximity sensor is the gloveTarget, then remove the source of 
		the proximity sensor from self.proxList
		"""
		"""@args vizproximity.ProximityEvent()"""
		
		source = e.sensor.getSourceObject()
		target = e.target.getSourceObject()
		if target == model.pointer:
			model.pointer.color(1,1,1)
			
			self.proxList.remove(source)

	def grab(self):
		"""
		If the glove is not already linked to something, and the glove is within proximity of an object, link the 
		object to the glove
		"""
		print('command invoked correctly')
#		print("Here: ", init.wiimote.getButtonState())
#		
		if self.outlineCenter.getAction() or self.dogCenter.getAction():
			self.recordData.event(event = 'grab', result = 'Did Not Pick Up')
			return
		if not self.gloveLink and len(self.proxList)>0:
			target = self.proxList[0]
			self.gloveLink = viz.grab(model.pointer, target, viz.ABS_GLOBAL)
			self.recordData.event(event = 'grab', result = 'Picked Up')
		else:
			self.recordData.event(event = 'grab', result = 'Did Not Pick Up')
#
	def release(self):
		"""
		Unlink the glove and the object, and if the object is close enough to its target, and is within angular range, then
		the object is snapped to its target.
		"""
		eulerThres = 45
		eulerDiff = vizmat.QuatDiff(self.outlineCenter.getQuat(), self.dogCenter.getQuat())
		if self.snapFlag == True and eulerDiff <= eulerThres and self.gloveLink:
			self.recordData.event(event = 'release', result = 'Snapped!', angOffset = eulerDiff, posOffset = (vizmat.Distance(self.dogCenter.getPosition(), self.outlineCenter.getPosition())))
			self.snap()
		else:
			self.recordData.event()
		if self.gloveLink:
			try:
				self.gloveLink.remove()
			except NameError:
				self.gloveLink.removeItems(viz.grab(model.pointer, target, viz.ABS_GLOBAL))
#
	def snap(self):
		"""
		Moves dog to the pos and euler of its target (dogTarget)
		"""
		movePos = vizact.moveTo(self.outlineCenter.getPosition(), time = self.snapTransitionTime)
		moveAng = vizact.spinTo(euler = self.outlineCenter.getEuler(), time = self.snapTransitionTime)
#		transition = vizact.parallel(movePos, moveAng)
#		self.dogCenter.addAction(transition)		
		viz.playSound(".\\dataset\\snap.wav")
		if not self.dogCenter.getAction() and not self.outlineCenter.getAction(): 
			self.resetPos()
#			movePos = vizact.moveTo((0,0.5,0), time = self.animateOutline)
#			moveAng = vizact.spinTo((0,0,0), time = self.animateOutline)
#			transition = vizact.parallel(movePos, moveAng)
#			self.outlineCenter.addAction(transition)
#			self.dogCenter.addAction(transition)
		viztask.schedule(self.mechanics())
#
	def snapCheckEnter(self, e):
		"""
		If the snap proximity sensor has its desired target within range, then snapFlag is True.
		snapFlag is used in release to determine whether snap will be called or not.
		"""
		
		targets = e.manager.getActiveTargets()
		for t in targets:
			if t == self.dogTarget:
				self.snapFlag = True
#
	def snapCheckExit(self, e):
		"""
		If the dogTarget has left the proximity sensor then snapFlag is False
		"""
		target = e.target.getSourceObject()
		if target == self.dogTargetMold:
			self.snapFlag = False

class TutorialData():
	"""
	Collects data from tutorial
	"""
	def __init__(self):
		"""
		Init data recording structure
		"""
		self.startTime = datetime.datetime.now()
		try:
			self.scoreFile = open('.\\log\\tutorial\\' + self.startTime.strftime('%m%d%Y_%H%M%S') + '.csv', 'wb')
		except IOError:
			print "No directory?"
			raise
		self.csv = csv.writer(self.scoreFile)
		self.header = ['timestamp','event', 'event result','x', 'y', 'z', 'angular offset', 'positional offset']
		self.events = []
		self.csv.writerow(self.header)
		
	def event(self, x = 'n/a', y = 'n/a', z = 'n/a', event = "release", result = 'Did Not Snap', angOffset = 'n/a', posOffset = 'n/a'):
		'''record event'''
		currentEvent = dict(zip(self.header,[time.clock(), event, result, x,y,z,angOffset,posOffset]))
		self.csv.writerow([currentEvent[column] for column in self.header])
		
	def close(self):
		self.scoreFile.close()
