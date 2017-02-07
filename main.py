"""
STEREOSCOPIC ANATOMY GAME

Originally started as a senior design project for the 2014-2015 academic year.
Senior design team members:
 Alex Dawson-Elli, Kenny Lamarka, Kevin Alexandre, Jascha Wilcox , Nate Burell

Development was continued in fall 2015 by:
 Jascha Wilcox, Erik Messier
"""

# Built-In 
import json

# Custom modules
import config
import anatomyTrainer
import menu
import demoGlasses

def main():
	"""
	Run this function with no parameters to begin the anatomy puzzle game.
	"""
	
	try:
		# open Tkinter menu to set init config parameters
		configurations = menu.modalityGUI()		
		
		# read configuration parameters from json file
		with open('.\\dataset\\configurations\\configurations.json', 'rb') as f:
			
			# open json file
			configurations = json.load(f)
			
			# assign config attributes from json keywords
			config.dispMode = int(configurations['dispMode'])
			config.pointerMode = int(configurations['pointerMode'])
			proceedFromConfigGUI = configurations['proceed']
			
			# close json file
			f.close()
			
		if proceedFromConfigGUI:
			
			# start puzzle game
			anatomyTrainer.start()
			anatomyTrainer.startGame(anatomyTrainer.init.games.tutorialGame.InterfaceTutorial, [])
			
		#		# EVAN: added Gabe's code (very hackily!)
		import demoGlasses
		experimentObject = demoGlasses.Experiment()
		
		# EVAN: add tracking of wiimote via PhaseSpace system
		wiiNode3D = viz.addGroup() # Create empty node3D
		wiimoteRigid = experimentObject.config.mocap.returnPointerToRigid('wii') # Get access to phasespace wiimote tracker / rigid body
		wiiNode3D = viz.addGroup() # Create empty node3D
		
		# EVAN: link wiimote pose to pointer object
		wiimoteRigid.link_pose(anatomyTrainer.model.pointer) # link wiimote position to pointer
		
	except:
		raise
	
	



if __name__ == '__main__':
	main()