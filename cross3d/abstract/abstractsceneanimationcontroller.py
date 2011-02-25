##
#	\namespace	blur3d.api.abstract.abstractsceneanimationcontroller
#
#	\remarks	The AbstractSceneAnimationController class defines a base class for managing animation curves within a 3d scene
#
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

from blur3d.api import SceneWrapper

class AbstractSceneAnimationController( SceneWrapper ):
	#--------------------------------------------------------------------------------
	#								private methods
	#--------------------------------------------------------------------------------
	def _createNativeKeyAt( self, time ):
		"""
			\remarks	[abstract] creates a new key at the inputed time
			\param		time		<float>
			\return		<variant> nativeKey || None
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
	def _nativeKeys( self ):
		"""
			\remarks	[abstract] return a list of the keys that are defined for this controller
			\return		<list> [ <variant> nativeKey, .. ]
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return []
	
	def _setNativeKeyAt( self, time, nativeKey ):
		"""
			\remarks	[abstract] set the key at the inputed time to the given native key
			\param		time		<float>
			\param		nativeKey	<variant>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
		
	@classmethod
	def _createNewNative( cls, scene, controllerType ):
		"""
			\remarks	[abstract] create a new native controller in the scene of the inputed controller type
			\param		scene				<blur3d.api.Scene>
			\param		controllerType		<blur3d.constants.ControllerType>
			\return		<blur3d.api.SceneAnimationController> || None
		"""
		from blurdev import debug
				
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError

		return None
		
	#--------------------------------------------------------------------------------
	#								public methods
	#--------------------------------------------------------------------------------
	def createKeyAt( self, time ):
		"""
			\remarks	creates a new key at the inputed time
			\param		time	<float>
			\return		<blur3d.api.SceneAnimationKey> || None
		"""
		nativeKey = self._createNativeKeyAt( time )
		if ( nativeKey ):
			from blur3d.api import SceneAnimationKey
			return SceneAnimationKey( self._scene, nativeKey )
		return None
	
	def controllerType( self ):
		"""
			\remarks	[abstract] return the type of controller that this controller is
			\return		<blur3d.constants.ControllerType>
		"""
		from blurdev import debug
				
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError

		return 0
		
	def isKeyedAt( self, time ):
		"""
			\remarks	return whether or not a key exists at the inputed time frame
			\param		time	<float>
			\return		<bool> keyed
		"""
		return self.keyAt(time) != None
	
	def keyAt( self, time ):
		"""
			\remarks	return the key that is found at the inputed time frame
			\param		time	<float>
			\return		<blur3d.api.SceneAnimationKey> || None
		"""
		for key in self.keys():
			if ( key.time() == time ):
				return key
		return None
		
	def keys( self ):
		"""
			\remarks	return a list of SceneAnimationKey's that are defined for this controller
			\return		<list> [ <blur3d.api.SceneAnimationKey> key, .. ]
		"""
		from blur3d.api import SceneAnimationKey
		return [ SceneAnimationKey( self._scene, nativeKey ) for nativeKey in self._nativeKeys() ]
	
	def removeKeyAt( self, time ):
		"""
			\remarks	clears the key at the inputed time
			\param		time		<float>
			\return		<bool> success
		"""
		return self.setKeyAt( time, None )
	
	def setKeyAt( self, time, key ):
		"""
			\remarks	set the key at the inputed time frame to the inputed key
			\param		time		<float>
			\param		key			<blur3d.api.SceneAnimationKey>
			\return		<bool> success
		"""
		nativeKey = None
		if ( key ):
			nativeKey = key.nativePointer()
			
		return self._setNativeKeyAt( time, nativeKey )
	
	@classmethod
	def createNew( cls, scene, controllerType ):
		"""
			\remarks	create a new controller in the scene of the inputed controller type
			\param		scene				<blur3d.api.Scene>
			\param		controllerType		<blur3d.constants.ControllerType>
			\return		<blur3d.api.SceneAnimationController> || None
		"""
		nativeController = cls._createNewNative( scene, controllerType )
		if ( nativeController ):
			from blur3d.api import SceneAnimationController
			return SceneAnimationController( scene, nativeController )
		return None
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneAnimationController', AbstractSceneAnimationController, ifNotFound = True )