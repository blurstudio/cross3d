##
#	\namespace	cross3d.studiomax.matlib
#
#	\remarks	This package contains material editing methods for Studiomax
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		01/06/11
#

from Py3dsMax import mxs

def toggleCaches( object, state ):
	"""
		\remarks	enables/disables the caches on the inputed object based on the given state
		\param		object		<Py3dsMax.mxs.Object>
		\param		state		<bool>
		\return		<bool> success
	"""
	from cross3d.studiomax.cachelib import pointcache
	pointcache.toggleCaches( object, state )
	
	from cross3d.studiomax.cachelib import transformcache
	transformcache.toggleCaches( object, state )