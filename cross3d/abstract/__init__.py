##
#	\namespace	blur3d.scenes
#
#	\remarks	The blur3d.scenes package creates an abstract wrapper from a 3d system
#				to use when dealing with scenes
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

def init():
	"""
		\remarks	initializes the original abstract classes, registering them to the api module when necessary
	"""
	import abstractscene
	import abstractsceneobject
	import abstractsceneobjectgroup
	import abstractscenelayer
	import abstractscenelayergroup
	import abstractscenematerial
	import abstractscenemap