##
#	\namespace	cross3d.abstract.abstractscenecache
#
#	\remarks	The AbstractSceneCache class provides an interface to editing data caches in a Scene environment for any DCC application
#	
#	\author		eric
#	\author		Blur Studio
#	\date		09/08/10
#

from Py3dsMax import mxs
from cross3d.abstract.abstractscenecache import AbstractSceneCache

class StudiomaxSceneCache( AbstractSceneCache ):
	def _nativeControllers( self ):
		"""
			\remarks	implements the AbstractSceneCache._nativeControllers method to collect a list of the native controllers that are currently applied to this cache instance
			\return		<list> [ <variant> nativeController, .. ]
		"""
		# store the maxsript variables we're going to use
		get_propcontrol = mxs.getPropertyController
		
		# return the playback from controller
		output = []
		for propname in self.propertyNames():
			control = get_propcontrol(self._nativePointer,propname)
			if ( control ):
				output.append(control)
		return output
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def filename( self ):
		"""
			\remarks	implements the AbstractSceneCache.filename method to return the filename that this cache is pulling from
			\return		<str> filename
		"""
		return self._nativePointer.filename
			
	def isEnabled( self ):
		"""
			\remarks	implements the AbstractSceneCache.isEnabled method to return wether or not this cache is enabled in the scene
			\return		<bool> enabled
		"""
		return self._nativePointer.enabled
		
	def setEnabled( self, state ):
		"""
			\remarks	implements the AbstractSceneCache.setEnabled method to mark whether or not this cache is enabled in the scene
			\param		state		<bool>
			\return		<bool> success
		"""
		self._nativePointer.enabled = state
		return True
	
	def setFilename( self, filename ):
		"""
			\remarks	implements the AbstractSceneCache.setFilename method to set the filename for this cache data to the inputed filename
			\param		filename	<str>
			\return		<bool> success
		"""
		self._nativePointer.filename = filename
		return True
	
# register the symbol
import cross3d
cross3d.registerSymbol( 'SceneCache', StudiomaxSceneCache )
