##
#   :namespace  cross3d.maya
#
#   :remarks    The cross3d.maya package contains the necessary classes to control Maya.
#   
#   :author     mikeh
#   :author     Blur Studio
#   :date       09/10/14
#

import external

def init():

	# Making sure we can import the layer.
	import maya.cmds
	
	# Importing the layer's classes.
	import mayaexceptionrouter
	import mayauserprops
	import mayaapplication
	import mayascene
	import mayascenewrapper
	import mayasceneobject
	import mayagroup
	import mayascenemodel
	import mayascenecamera
	import mayasceneviewport
	import mayascenematerial
	import collection
