##
#	\namespace	blur3d.scenes
#
#	\remarks	The blur3d.scenes package creates an abstract wrapper from a 3d system
#				to use when dealing with scenes
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

def init():
	# make sure we can import softimage
	from PySoftimage import xsi
	
	# import softimage classes
	#import softimageuserprops
	import softimagescene
	import softimagescenewrapper
	import softimagesceneobjectmetadata # not in abstract
	import softimagesceneobject
	import softimagescenemodel
	import softimagescenecamera
	import softimagesceneviewport # not in abstract
	import softimagescenerenderpass