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