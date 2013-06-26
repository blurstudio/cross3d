##
#	\namespace	blur3d.studiomax
#
#	\remarks	The blur3d.studiomax package contains the necessary classes to control 3D Studio Max.
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

from blurdev.enum import enum
from blurdev import relativePath

StudiomaxAppData = enum( AltMtlIndex = 1108, AltPropIndex = 1110 )

def init():
	
	# Making sure we can import the layer.
	from Py3dsMax import mxs
	mxs.filein(relativePath(__file__, 'maxscript/helpers.ms'))
	
	# Importing the layer's classes.
	import studiomaxuserprops
	import studiomaxapplication
	import studiomaxscene
	import studiomaxscenewrapper
	import studiomaxsceneobject
	import studiomaxscenemodel	
	import studiomaxscenelayer	
	import studiomaxscenelayergroup	
	import studiomaxscenematerial	
	import studiomaxscenepropset
	import studiomaxscenemap
	import studiomaxsceneatmospheric
	import studiomaxscenefx
	import studiomaxscenerenderer
	import studiomaxscenecamera
	import studiomaxsceneanimationcontroller
	import studiomaxsceneanimationkey
	import studiomaxscenecache
	import studiomaxscenesubmitter
	import studiomaxsceneviewport