import sys
import viz
import vizconnect

viz.res.addPath('resources')
sys.path.append('utils')

from mocapInterface import phasespaceInterface	
from configobj import ConfigObj
from configobj import flatten_errors
from validate import Validator
import platform
import os.path
import virtualPlane
import vizact


class Configuration():
	
	def __init__(self, expCfgName = ""):
		"""
		Opens and interprets both the system config (as defined by the <platform>.cfg file) and the experiment config
		(as defined by the file in expCfgName). Both configurations MUST conform the specs given in sysCfgSpec.ini and
		expCfgSpec.ini respectively. It also initializes the system as specified in the sysCfg.
		"""
		self.eyeTracker = []
		
		self.writables = list()
		if expCfgName:
			self.__createExpCfg(expCfgName)
		else:
			self.expCfg = None
			
		self.__createSysCfg()
		
		for pathName in self.sysCfg['set_path']:
			viz.res.addPath(pathName)
			
		# seems to be where the startup command is invoked
		self.vizconnect = vizconnect.go( './vizConnect/' + self.sysCfg['vizconfigFileName'])
		self.__postVizConnectSetup()
		
		
	def __postVizConnectSetup(self):
		
		''' 
		This is where one can run any system-specifiRRRc code that vizconnect can't handle
		'''

		dispDict = vizconnect.getRawDisplayDict()
				
		if self.sysCfg['use_phasespace']:
			
			from mocapInterface import phasespaceInterface	
			self.mocap = phasespaceInterface(self.sysCfg);
			self.mocap.start_thread()
			
			self.use_phasespace = True
			
		else:
			self.use_phasespace = False

		if( self.sysCfg['use_wiimote']):
			# Create wiimote holder
			self.wiimote = 0
			self.__connectWiiMote()

		if self.sysCfg['use_hmd'] and self.sysCfg['hmd']['type'] == 'DK2':
			self.__setupOculusMon()
		
		if self.sysCfg['use_eyetracking']:
			self.use_eyetracking = True
			self.__connectSMIDK2()
		else:
			self.use_eyetracking = False
			
		if self.sysCfg['use_DVR'] == 1:
			self.use_DVR = True
		else:
			self.use_DVR = False
		
		if self.sysCfg['use_virtualPlane']:
			
			self.use_VirtualPlane = True
			
			isAFloor = self.sysCfg['virtualPlane']['isAFloor']
			planeName = self.sysCfg['virtualPlane']['planeName']
			planeCornerFile = self.sysCfg['virtualPlane']['planeCornerFile']
			
			self.virtualPlane = virtualPlane.virtualPlane(self,planeName,isAFloor,planeCornerFile)
			
		self.writer = None #Will get initialized later when the system starts
		self.writables = list()
		
		self.__setWinPriority()
		viz.setMultiSample(self.sysCfg['antiAliasPasses'])
		viz.MainWindow.clip(0.01 ,200)
		
		viz.vsync(1)
		viz.setOption("viz.glfinish", 1)
		viz.setOption("viz.dwm_composition", 0)
		
	def __createExpCfg(self, expCfgName):

		"""

		Parses and validates a config obj
		Variables read in are stored in configObj
		
		"""
		
		print "Loading experiment config file: " + expCfgName
		
		# This is where the parser is called.
		expCfg = ConfigObj(expCfgName, configspec='expCfgSpec.ini', raise_errors = True, file_error = True)

		validator = Validator()
		expCfgOK = expCfg.validate(validator)
		if expCfgOK == True:
			print "Experiment config file parsed correctly"
		else:
			print 'Experiment config file validation failed!'
			res = expCfg.validate(validator, preserve_errors=True)
			for entry in flatten_errors(expCfg, res):
			# each entry is a tuple
				section_list, key, error = entry
				if key is not None:
					section_list.append(key)
				else:
					section_list.append('[missing section]')
				section_string = ', '.join(section_list)
				if error == False:
					error = 'Missing value or section.'
				print section_string, ' = ', error
			sys.exit(1)
		if expCfg.has_key('_LOAD_'):
			for ld in expCfg['_LOAD_']['loadList']:
				print 'Loading: ' + ld + ' as ' + expCfg['_LOAD_'][ld]['cfgFile']
				curCfg = ConfigObj(expCfg['_LOAD_'][ld]['cfgFile'], configspec = expCfg['_LOAD_'][ld]['cfgSpec'], raise_errors = True, file_error = True)
				validator = Validator()
				expCfgOK = curCfg.validate(validator)
				if expCfgOK == True:
					print "Experiment config file parsed correctly"
				else:
					print 'Experiment config file validation failed!'
					res = curCfg.validate(validator, preserve_errors=True)
					for entry in flatten_errors(curCfg, res):
					# each entry is a tuple
						section_list, key, error = entry
						if key is not None:
							section_list.append(key)
						else:
							section_list.append('[missing section]')
						section_string = ', '.join(section_list)
						if error == False:
							error = 'Missing value or section.'
						print section_string, ' = ', error
					sys.exit(1)
				expCfg.merge(curCfg)
		
		self.expCfg = expCfg

	
	def __setWinPriority(self,pid=None,priority=1):
		
		""" Set The Priority of a Windows Process.  Priority is a value between 0-5 where
			2 is normal priority.  Default sets the priority of the current
			python process but can take any valid process ID. """
			
		import win32api,win32process,win32con
		
		priorityclasses = [win32process.IDLE_PRIORITY_CLASS,
						   win32process.BELOW_NORMAL_PRIORITY_CLASS,
						   win32process.NORMAL_PRIORITY_CLASS,
						   win32process.ABOVE_NORMAL_PRIORITY_CLASS,
						   win32process.HIGH_PRIORITY_CLASS,
						   win32process.REALTIME_PRIORITY_CLASS]
		if pid == None:
			pid = win32api.GetCurrentProcessId()
		
		handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, True, pid)
		win32process.SetPriorityClass(handle, priorityclasses[priority])
		
	def __createSysCfg(self):
		"""
		Set up the system config section (sysCfg)
		"""
		
		# Get machine name
		sysCfgName = platform.node()+".cfg"
		
		if not(os.path.isfile(sysCfgName)):
			sysCfgName = "defaultSys.cfg"
			
		print "Loading system config file: " + sysCfgName
		
		# Parse system config file
		sysCfg = ConfigObj(sysCfgName, configspec='sysCfgSpec.ini', raise_errors = True)
		
		validator = Validator()
		sysCfgOK = sysCfg.validate(validator)
		
		if sysCfgOK == True:
			print "System config file parsed correctly"
		else:
			print 'System config file validation failed!'
			res = sysCfg.validate(validator, preserve_errors=True)
			for entry in flatten_errors(sysCfg, res):
			# each entry is a tuple
				section_list, key, error = entry
				if key is not None:
					section_list.append(key)
				else:
					section_list.append('[missing section]')
				section_string = ', '.join(section_list)
				if error == False:
					error = 'Missing value or section.'
				print section_string, ' = ', error
			sys.exit(1)
		self.sysCfg = sysCfg
	
		
	def __setupOculusMon(self):
		"""
		Setup for the oculus rift dk2
		Relies upon a cluster enabling a single client on the local machine
		THe client enables a mirrored desktop view of what's displays inside the oculus DK2
		Note that this does some juggling of monitor numbers for you.
		"""
		
		#viz.window.setFullscreenMonitor(self.sysCfg['displays'])
		
		#hmd = oculus.Rift(renderMode=oculus.RENDER_CLIENT)

		displayList = self.sysCfg['displays'];
		
		if len(displayList) < 2:
			print 'Display list is <1.  Need two displays.'
		else:
			print 'Using display number' + str(displayList[0]) + ' for oculus display.'
			print 'Using display number' + str(displayList[1]) + ' for mirrored display.'
		
		### Set the rift and exp displays
		
		riftMon = []
		expMon = displayList[1]
		
		with viz.cluster.MaskedContext(viz.MASTER):
			
			# Set monitor to the oculus rift
			monList = viz.window.getMonitorList()
			
			for mon in monList:
				if mon.name == 'Rift DK2':
					riftMon = mon.id
			
			viz.window.setFullscreen(riftMon)

		with viz.cluster.MaskedContext(viz.CLIENT1):
			
			count = 1
			while( riftMon == expMon ):
				expMon = count
				
			viz.window.setFullscreenMonitor(expMon)
			viz.window.setFullscreen(1)

	def __connectWiiMote(self):
		
		wii = viz.add('wiimote.dle')#Add wiimote extension
		
		# Replace old wiimote
		if( self.wiimote ):
			print 'Wiimote removed.'
			self.wiimote.remove()
			
		self.wiimote = wii.addWiimote()# Connect to first available wiimote
		
		vizact.onexit(self.wiimote.remove) # Make sure it is disconnected on quit
		self.wiimote.led = wii.LED_1 | wii.LED_2 #Turn on leds to show connection
		
		def buttonPress(wiimote):
			"""
			This function serves to call the grab() method from 
			the tutorialGame when the wiimote trigger is pulled.

			Parameters
			----------
			wiimote : Vizard extension sensor

			Returns
			-------
			None
			"""
			
			# return integer code corresponding with button ID
			buttonState = wiimote.getButtonState()
			
			if buttonState == 32: # corresponds to B (the trigger)
				print("Button Pressed")
				
				# call the grab() from tutorialGame when trigger is pulled
				anatomyTrainer.model.gameController.grab()
				
			else:
				pass
		
		def buttonRelease(wiimote):
			"""
			This function serves to call the release() method from 
			the tutorialGame when the wiimote trigger is pulled.

			Parameters
			----------
			wiimote : Vizard extension sensor

			Returns
			-------
			None
			"""
			
			# return integer code corresponding with button ID
			buttonState = wiimote.getButtonState()
			
			if buttonState == 0: # corresponds to B (the trigger)
				print("Button Released")
				
				# call the release() from tutorialGame when trigger is pulled
				anatomyTrainer.model.gameController.release()
			
			else:
				pass

		# run buttonPress() when B is held
		vizact.onsensordown(self.wiimote, wii.BUTTON_B, buttonPress, self.wiimote)
		# run corresponding release() function when trigger is released 
		vizact.onsensorup(self.wiimote, wii.BUTTON_B, buttonRelease, self.wiimote)
	
	def __connectSMIDK2(self):
		
		if self.sysCfg['sim_trackerData']:
			self.eyeTracker = smi_beta.iViewHMD(simulate=True)
		else:
			self.eyeTracker = smi_beta.iViewHMD()


class Experiment(viz.EventClass):
	
	"""
	Experiment manages the basic operation of the experiment.
	"""
	
	def __init__(self):
		
		# Event class
		# This makes it possible to register callback functions (e.g. activated by a timer event)
		# within the class (that accept the implied self argument)
		# eg self.callbackFunction(arg1) would receive args (self,arg1)
		# If this were not an eventclass, the self arg would not be passed = badness.
		
		viz.EventClass.__init__(self)
		
		##############################################################
		##############################################################
		## Use config to setup hardware, motion tracking, frustum, eyeTrackingCal.
		##  This draws upon the system config to setup the hardware / HMD
		
		config = Configuration()
		self.config = config
		
		self.eyeSphere = viz.addGroup()
		self.setupShutterGlasses()
		
		vizact.onexit(self.__endExperiment) # Make sure it is disconnected on quit

#		self.environment = self.createEnvironment()
		
	def __endExperiment(self):
		
		self.config.mocap.stop_thread()
	
	def createEnvironment():
		pass
		
	def setupShutterGlasses(self):

		'''
		MOCAP: This is where I create an action that updates the mainview
		with data from my motion capture system
		'''
		
		config = self.config
		print 'Connecting mainview to eyesphere'

		# Flip L/R eye phasing
		viz.MainWindow.setStereoSwap(viz.TOGGLE)
		
		shutterRigid = config.mocap.returnPointerToRigid('shutter') # Here, 
		shutterRigid.link_pose(self.eyeSphere)
				
		self.config.virtualPlane.attachViewToGlasses(self.eyeSphere,shutterRigid)
	

# create instance of Gabe's Experiment class to begin tracking portion of the code
experimentObject = Experiment()

### Set up Wiimote PhaseSpace Tracking
wiiNode3D = viz.addGroup() # Create empty node3D
wiimoteRigid = experimentObject.config.mocap.returnPointerToRigid('wii') # Get access to phasespace wiimote tracker / rigid body
wiimoteRigid.link_pose(wiiNode3D) #Setup an automatic per-frame update of wiiNode3D using the transf. matrix from wiimoteRigid

### Attach shape to wiimote controller
import vizshape
wiiSphere = vizshape.addBox(size=[0.03,.03,.1])
wiiSphere.visible(viz.OFF)
wiimoteRigid.link_pose(wiiSphere)

### Start Game
# import Erik's anatomyTrainer module to access game code
import anatomyTrainer
anatomyTrainer.model.trial = 2
# game setup, passing wiiSphere to allow model.pointer to see it
anatomyTrainer.start(wiiSphere)
# start tutorial game directly, bypassing menus
anatomyTrainer.startGame(anatomyTrainer.init.games.tutorialGame.InterfaceTutorial, [])

# change pointer scale and rotation to align with wiimote and overall scale
# (slightly unnecessary (and possibly redundant) change to scale, especially if ultimately set to invisible, but whatever)
anatomyTrainer.model.pointer.setScale( [0.012, 0.012, 0.012] )
anatomyTrainer.model.pointer.setEuler( [ 180, 0, 0 ] )

#vizact.onkeydown(viz.KEY_ESCAPE, anatomyTrainer.restartGame(anatomyTrainer.init.games.tutorialGame.InterfaceTutorial))