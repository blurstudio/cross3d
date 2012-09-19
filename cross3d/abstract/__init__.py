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
	Initializes the original abstract classes, registering them to the api 
	module when necessary
	"""
	import abstractuserprops
	import blurtags
	import abstractapplication
	import abstractscene
	import abstractscenewrapper
	import abstractsceneobject
	import abstractsceneobjectgroup
	import abstractscenelayer
	import abstractscenelayergroup
	import abstractscenematerial
	import abstractscenemap
	import abstractsceneatmospheric
	import abstractscenerenderer
	import abstractscenemodel
	import abstractscenecamera
	import abstractscenerenderpass
	import abstractsceneviewport
	import abstractsceneanimationcontroller
	import abstractsceneanimationkey
	import abstractscenecache
	import abstractscenesubmitter
	import abstractalembic
	import abstractwritejob
	import abstractwritejobs
