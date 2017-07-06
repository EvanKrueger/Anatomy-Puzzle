# test

"""
This script demonstrates how the vizcave module works in Vizard.

Use the WASD keys to move the avatar within the cave.
This simulates the head tracker assigned to vicave.setTracker()

Use the mouse + arrow keys to move the entire cave through the environment.
This simulates how the vizcave.CaveView object affects the final viewpoint.

Press the 1-4 keys to change which cave wall is represented by the right half
of the window.
"""
import viz
import vizact
import vizcam
import vizcave
import vizshape

viz.setMultiSample(8)
viz.fov(60)
viz.go(viz.FULLSCREEN)

import vizinfo
infoWindow = viz.addWindow(pos=(0,1), size=(1,1), clearMask=0, order=10)
infoWindow.visible(False,viz.WORLD)
vizinfo.InfoPanel(window=infoWindow)

# Setup main window
viz.MainWindow.setSize([0.5,1])

# Setup cave window
caveView = viz.addView()

# Setup pivot navigation for main window
cam = vizcam.PivotNavigate(distance=10,center=(0,2,0))
cam.rotateUp(25)

# Create avatar to simulate person standing in cave
avatar = viz.addAvatar('vcc_male2.cfg')
avatar.state(1)

# Use keyboard to simulate avatar movement
avatar_tracker = vizcam.addKeyboard6DOF(turnScale=2.0)
viz.link(avatar_tracker,avatar)

# Head tracker
head_tracker = viz.link(avatar,viz.NullLinkable,srcFlag=viz.ABS_PARENT)
head_tracker.preTrans([0,1.69,0.12])

# Create cave view
cave_origin = vizcave.CaveView(head_tracker,view=caveView)
cave_origin.renderOnlyToWindows([viz.MainWindow])

# Use keyboard mouse to simulate origin tracker
origin_tracker = vizcam.addFlyNavigate()
origin_tracker.setPosition([0,0.1,0])
viz.link(origin_tracker, cave_origin)