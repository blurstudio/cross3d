##
#	\namespace	blur3d.api.abstract.abstractsceneanimationcontroller
#
#	\remarks	The AbstractSceneAnimationController class provides an interface to editing controllers in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from Py3dsMax 												import mxs
from blur3d.api.abstract.abstractsceneanimationcontroller	import AbstractSceneAnimationController
#from blur3d.api.abstract.abstractsceneanimationkey import AbstractSceneAnimationKey

class StudiomaxSceneAnimationController( AbstractSceneAnimationController ):
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _createNativeKeyAt( self, time ):
		"""
			\remarks	implements the AbstractSceneAnimationController._nativeKeys method to create a new key at the inputed time
			\param		time		<float>
			\return		<Py3dsMax.mxs.Key> nativeKey || None
		"""
		return mxs.addNewKey( self._nativePointer, time )
	
	def _nativeKeys( self ):
		"""
			\remarks	implements the AbstractSceneAnimationController._nativeKeys method to collect a list of the current keys
						for this controller instance
			\return		<list> [ <Py3dsMax.mxs.Key> nativeKey, .. ]
		"""
		return self._nativePointer.keys
		
	@classmethod
	def _createNewNative( cls, scene, controllerType ):
		"""
			\remarks	implements the AbstractSceneAnimationController._createNewNative method to create a new native controller in the scene of the inputed controller type
			\param		scene				<blur3d.api.Scene>
			\param		controllerType		<blur3d.constants.ControllerType>
			\return		<blur3d.api.SceneAnimationController> || None
		"""
		from blur3d.constants import ControllerType
		if ( controllerType == ControllerType.Bezier_Float ):
			return mxs.Bezier_Float()
		return None
	
	def _setNativeKeyAt(self, time, nativeKey):
		"""
			\remarks	set the key at the inputed time to the given native key
			\param		time		<float>
			\param		nativeKey	<variant>
			\return		<bool> success
		"""
		key = self.keyAt(time)
		if nativeKey == None:
			# remove the key if it exists
			if key:
				index = mxs.getKeyIndex(self._nativePointer, time)
				# index is 1 based, zero indecates that the key was not found.
				if index != 0:
					return mxs.deleteKey(self._nativePointer, index)
		elif not key:
			# Create the key so we can set the value
			key = self._createNativeKeyAt(time)
			if not key:
				return False
		return key.setValue(nativeKey)
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def controllerType( self ):
		"""
			\remarks	implements AbstractSceneAnimationController.controllerType method to return the controller type for this instance
			\return		<blur3d.constants.ControllerType>
		"""
		from blur3d.constants import ControllerType
		cls = mxs.classof(self._nativePointer)
		
		# return a float controller
		if ( cls == mxs.Bezier_Float ):
			return ControllerType.Bezier_Float
		
		return 0
		
	def name( self ):
		"""
			\remarks	implements AbstractSceneWrapper.name to return the name of this animation controller instance
			\sa			setName
			\return		<str> name
		"""
		return '.'.join( mxs.exprForMaxObject( self._nativePointer ).split( '.' )[1:] )
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneAnimationController', StudiomaxSceneAnimationController )