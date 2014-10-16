##
#   :namespace  blur3d.api.maya
#
#   :remarks    The blur3d.api.maya package contains the necessary classes to control Maya.
#   
#   :author     mikeh@blur.com
#   :author     Blur Studio
#   :date       09/10/14
#

import external

def init():

	# Making sure we can import the layer.
	import maya.cmds
	
	# Importing the layer's classes.
	import mayauserprops
	import mayaapplication
	import mayascene
	import mayascenewrapper
	import mayasceneobject
	import mayagroup
	import mayascenemodel
	import mayascenecamera
	import mayasceneviewport