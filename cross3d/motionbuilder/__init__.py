##
#	\namespace	cross3d.motionbuilder
#
#	\remarks	The cross3d.motionbuilder package contains the necessary classes to control Motion Builder.
#	
#	\author		douglas
#	\author		Blur Studio
#	\date		06/21/12
#

import external

def init():

	# Making sure we can import the layer.
	import pyfbsdk as mob
	
	# Importing the layer's classes.
	import motionbuilderapplication
	import motionbuilderscene
	import collection
