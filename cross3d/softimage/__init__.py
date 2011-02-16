##
#	\namespace	blur3d.api.softimage
#
#	\remarks	Defines the classes that will be used for the Softimage implementation of the blur3d abstraction layer
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

def init():
	# make sure we can import softimage
	import PySoftimage
	
	# import softimage classes