##
#	\namespace	blur3d.motionbuilder
#
#	\remarks	The blur3d.motionbuilder package contains the necessary classes to control Motion Builder.
#	
#	\author		douglas@blur.com
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
