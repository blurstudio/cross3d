##
#	\namespace	blur3d.softimage
#
#	\remarks	The blur3d.softimage package contains the necessary classes to control Softimage.
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

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
