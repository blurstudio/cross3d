##
#	\namespace	blur3d.api.abstract.abstractscenecache
#
#	\remarks	The AbstractSceneCache class provides an interface to editing data caches in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from blur3d.api import SceneWrapper

class AbstractSceneCache( SceneWrapper ):
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def disable( self ):
		"""
			\remarks	convenience method for disabling this cache in the scene
			\sa			setEnabled
			\return		<bool> success
		"""
		return self.setEnabled(False)
	
	def controllers( self ):
		"""
			\remarks	return a list of the controllers that are currently on this cache instance
			\return		<list> [ <blur3d.api.SceneAnimationController> controller, .. ]
		"""
		from blur3d.api import SceneAnimationController
		return [ SceneAnimationController( self._scene, nativeControl ) for nativeControl in self._nativeControllers() ]
	
	def enable( self ):
		"""
			\remarks	convenience method for enabling this cache in the scene
			\sa			setEnabled
			\return		<bool> success
		"""
		return self.setEnabled(True)
	
	def filename( self ):
		"""
			\remarks	[abstract] return the filename that this cache is pulling from
			\return		<str> filename
		"""
		from blurdev import debug
				
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError

		return ''
			
	def isEnabled( self ):
		"""
			\remarks	[abstract] return wether or not this cache is enabled in the scene
			\return		<bool> enabled
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError

		return False
		
	def setEnabled( self, state ):
		"""
			\remarks	[abstract] mark whether or not this cache is enabled in the scene
			\param		state		<bool>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError

		return False
	
	def setFilename( self, filename ):
		"""
			\remarks	[abstract] set the filename for this cache data to the inputed filename
			\param		filename	<str>
			\return		<bool> success
		"""
		from blurdev import debug
				
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError

		return False
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneCache', AbstractSceneCache, ifNotFound = True )
