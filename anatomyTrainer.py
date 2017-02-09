"""
Primary file from which the Anatomy Trainer game is run.
"""

# Vizard modules
import viz
import vizact, vizshape, viztask

# Custom modules
import model
import menu
import init
import config

def start(wiiSphere):
	"""
	Run everything necessary for game startup
	"""
	
	# Physics
	viz.phys.enable()

	### Initialize pointer tool
	# define pointer object as Polygon File Format (.ply) file
	model.pointer = viz.addChild('.\\dataset\\Hand\\handPoint_reduced.ply', parent=wiiSphere, flags=viz.ROTATE_Y_UP)
	model.pointer.visible(viz.OFF)
	pointer = model.pointer
	pointer.setScale(0.012, 0.012, 0.012)
	# EVAN: question: why set initial position there?
	pointer.setEuler(0, -115, 0)
	pointer.disable([viz.PHYSICS, viz.DYNAMICS])
	
	### Initialize environment this will load the coliseum and sky
	sky = viz.addChild('gallery.osgb')
	sky.setPosition([0, 0, -5])
	sky.collideMesh()
	sky.disable(viz.DYNAMICS)

	# Lighting
	lights = []
	[lights.append(viz.addLight()) for _ in range(2)]
	lights[0].setEuler(90, 40, 0)
	lights[0].intensity(0.5)
	lights[1].setEuler(270, 40, 0)
	lights[1].intensity(0.3)
	
	# Initialize pointer controls
	#	- config.pointerMode is an int read in from json file
	#	- pointer is the .ply file
	#	- sky is the environment (gallery.osgb)
	config.pointerMode = 2
	device = init.pointerInput(2, model.pointer, sky)

	# EVAN: I commented out both the display and menu code
	# - it's not necessary if we are directly launching the tutorial game
	
	### Initialize display
#	model.display = init.DisplayInstance(config.dispMode, config.camMode, device, pointer)
#	## Launch menu system
#	model.menu = menu.MenuController()
	
	### Override escape key to toggle menu
	viz.setOption('viz.default_key.quit','0')

	# EVAN: might comment out part that resets pointer
	# Stuff to run on program termination
	vizact.onexit(endGame)
	
def startGame(game, dataset):
	if model.gameController:
		return
	model.gameController = game(dataset)

def restartGame(game, dataset):
	if not model.gameController:
		return
	model.gameController.end()
	model.gameController = None
	startGame(game, dataset)

def endGame():
	if not model.gameController:
		return
	model.gameController.end()
	model.gameController = None
	print model.gameController

