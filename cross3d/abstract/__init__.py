##
#	\namespace	cross3d.scenes
#
#	\remarks	The cross3d.scenes package creates an abstract wrapper from a 3d system
#				to use when dealing with scenes
#	
#	\author		eric
#	\author		Blur Studio
#	\date		03/15/10
#

import external

def init():
	"""
	Initializes the original abstract classes, registering them to the api 
	module when necessary
	"""
	import abstractexceptionrouter
	import abstractuserprops
	import abstractundocontext
	import abstractapplication
	import abstractscene
	import abstractscenewrapper
	import abstractsceneobject
	import abstractcontainer
	import abstractscenelayer
	import abstractscenelayergroup
	import abstractgroup
	import abstractscenematerial
	import abstractscenemap
	import abstractsceneatmospheric
	import abstractscenefx
	import abstractscenerenderer
	import abstractscenemodel
	import abstractscenecamera
	import abstractscenerenderpass
	import abstractsceneviewport
	import abstractsceneanimationcontroller
	import abstractsceneanimationkey
	import abstractscenecache
	import abstractscenepropset
	import mixer
	import collection
