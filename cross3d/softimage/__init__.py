##
#	\namespace	cross3d.softimage
#
#	\remarks	The cross3d.softimage package contains the necessary classes to control Softimage.
#	
#	\author		douglas
#	\author		Blur Studio
#	\date		03/15/10
#

import external

def init():
	
	# Making sure we can import the layer.
	from PySoftimage import xsi
	
	# Importing the layer's classes.
	import softimageuserprops
	import softimageundocontext
	import softimageapplication
	import softimagescene
	import softimagescenewrapper
	import softimagesceneobject
	import softimagegroup
	import softimagescenemodel
	import softimagescenecamera
	import softimagescenerenderpass
	import softimagesceneviewport
	import collection
