##
#	\namespace	cross3d.studiomax
#
#	\remarks	The cross3d.studiomax package contains the necessary classes to control 3D Studio Max.
#	
#	\author		eric
#	\author		Blur Studio
#	\date		03/15/10
#

import os
from cross3d.enum import Enum, EnumGroup

import external

# Define some constants that are needed internally for Studiomax
class _StudiomaxAppData(Enum): pass
class StudiomaxAppData(EnumGroup):
	AltMtlIndex = _StudiomaxAppData(1108)
	AltPropIndex = _StudiomaxAppData(1110)

def init():
	
	# Making sure we can import the layer.
	from Py3dsMax import mxs
	path = os.path.join(os.path.split(unicode(__file__))[0], 'maxscript', 'helpers.ms')
	mxs.filein(path)
	
	# Importing the layer's classes.
	import studiomaxuserprops
	import studiomaxapplication
	import studiomaxscene
	import studiomaxscenewrapper
	import studiomaxsceneobject	
	import studiomaxscenelayer
	import studiomaxgroup	
	import studiomaxscenelayergroup	
	import studiomaxscenematerial	
	import studiomaxscenepropset
	import studiomaxscenemap
	import studiomaxsceneatmospheric
	import studiomaxscenefx
	import studiomaxscenerenderer
	import studiomaxscenemodel
	import studiomaxscenecamera
	import studiomaxsceneanimationcontroller
	import studiomaxsceneanimationkey
	import studiomaxscenecache
	import studiomaxsceneviewport
	import mixer
	import collection
