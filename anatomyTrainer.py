# Anatomy Trainer copy as of 7/7/17 #

""" 
Renamed this file the name of the original so I don't need to change the names everywhere!
Note that this is currently the most recent file
"""

"""
Primary file from which the Anatomy Trainer game is run.
"""

# Vizard modules
import viz
import vizact, vizshape, viztask
import vizinfo

# Custom modules
import model
import menu
import init_splitscreen_6_28
import config

def start():
	"""
	Run everything necessary for game startup
	"""
	# Physics
	viz.phys.enable()

	### Initialize pointer tool
	
	model.pointer = viz.addChild('.\\dataset\\Hand\\pin.obj') # Added parent thing here
	pointer = model.pointer
	
	pointer.setScale(0.0012, 0.0012, 0.0012)
	pointer.setPosition([-.4,.4,.7], viz.REL_LOCAL) # Alison: Place pointer in position where it is viz-able (ha puns) to the viewer	
	
	pointer.setEuler(0, -115, 0)
	pointer.disable([viz.PHYSICS, viz.DYNAMICS])
	
	
#	### Alpha slice plane setup
#	viz.startLayer(viz.POINTS)
#	viz.vertex(0,0,0)
#	planeVert = viz.endLayer(parent = pointer)
#	planeVert.dynamic()
#	
#	# Setup normal vector for alpha slicing plane calculation
#	planeVert.setNormal(0,[0,1,0])
#	model.planeVert = planeVert
#	slicePlane = vizshape.addPlane(size = [20, 20, 20], parent = pointer, cullFace = False)
#	slicePlane.alpha(0.20)
#	slicePlane.color(viz.ORANGE)
	
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
	device = init_splitscreen_6_28.pointerInput(config.pointerMode, pointer, sky)
	### Initialize display
	model.display = init_splitscreen_6_28.DisplayInstance(config.dispMode,config.camMode,device,pointer)
	
	### Launch menu system
	model.menu = menu.MenuController()
	
	### Display Instructions
		
	INSTRUCTIONS = """ 
Use W/A/S/D and E/X to control the pointer's position
Use arrow keys to move the camera left/right and to tilt the camera up/down
Use T/G to control zoom
Use +/- to toggle ortho views
Use ,/./; to control the pointer's orientation
Press SPACEBAR to grab object
Press F1 to exit pannel (NOTE: This also removes the ESC function to exit. Press F1 again to turn pannels back on) 
(Ctrl key toggles the complete puzzle in FREE PLAY mode)
"""
	infoPanel = vizinfo.InfoPanel(INSTRUCTIONS)
#	infoPanel.setPanelVisible(viz.TOGGLE)
	
	### Override escape key to toggle menu
	viz.setOption('viz.default_key.quit','0')
	
#	# Record moviefilms
#	viz.setOption('viz.AVIRecorder.maxWidth', '1280')
#	viz.setOption('viz.AVIRecorder.maxHeight', '720')
#	vizact.onkeydown(viz.KEY_F11, viz.window.startRecording, 'D:\\recording.avi')
#	vizact.onkeydown(viz.KEY_F12, viz.window.stopRecording)
	
	# Stuff to run on program termination
	vizact.onexit(endGame)
	
def startGame(game, dataset):
	print game
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

