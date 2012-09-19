##
#	\namespace	blur3d.api.abstract.abstractsceneanimationkey
#
#	\remarks	The AbstractSceneAnimationKey class defines a base class for managing animation curves within a 3d scene
#
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

from blur3d import abstractmethod
from blur3d.api import SceneWrapper
from blur3d import api


class AbstractSceneAnimationKey(SceneWrapper):
	#--------------------------------------------------------------------------------
	#								private methods
	#--------------------------------------------------------------------------------
	@abstractmethod
	def _nativeValue(self):
		"""
			\remarks	return the value 
			\return		<variant> value
		"""
		return 0

	@abstractmethod
	def _setNativeValue(self, nativeValue):
		"""
			\remarks	set the native value of this key to the inputed value
			\param		nativeValue		<variant>
			\return		<bool> success
		"""
		return False

	#--------------------------------------------------------------------------------
	#								public methods
	#--------------------------------------------------------------------------------
	@abstractmethod
	def setTime(self, time):
		"""Set the time value for this key.  *time* should be a float.  
		Returns True if successful, False otherwise.
		
		"""
		return False

	def setValue(self, value):
		"""Set the value of this key to the inputed value.  Returns True
		if successful, False otherwise.
		
		"""
		return self._setNativeValue(self._scene._toNativeValue(value))

	@abstractmethod
	def time(self):
		"""Return the time frame of this key

		"""
		return 0.0

	def value(self):
		"""Return the value of this key

		"""
		return self._scene._fromNativeValue(self._nativeValue())


# register the symbol
api.registerSymbol('SceneAnimationKey', AbstractSceneAnimationKey, ifNotFound=True)
