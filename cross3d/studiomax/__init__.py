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

from blurdev.enum import enum

StudiomaxAppData = enum( AltMtlIndex = 1108, AltPropIndex = 1110 )

def init():
	import studiomaxscene	
	import studiomaxsceneobject	
	import studiomaxscenelayer	
	import studiomaxscenelayergroup	
	import studiomaxscenematerial	
	import studiomaxscenepropset
	import studiomaxscenemap
	import studiomaxsceneatmospheric
	import studiomaxscenerenderer
	import studiomaxscenecamera