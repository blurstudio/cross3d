##
#	\namespace	cross3d.studiomax.studiomaxsceneanimationkey
#
#	\remarks	The StudiomaxSceneAnimationKey class defines a base class for managing animation curves within a 3d scene
#
#	\author		eric
#	\author		Blur Studio
#	\date		03/15/10
#

from Py3dsMax import mxs
from cross3d.constants import TangentType
from cross3d.abstract.abstractsceneanimationkey import AbstractSceneAnimationKey

class StudiomaxSceneAnimationKey( AbstractSceneAnimationKey ):

	# TODO: Use these. But that has to be done between projects, since currently the tangent type is used to write retime curves on disk.
	_abstractToNativeTangentTypes = { TangentType.Automatic: mxs.pyhelper.namify('auto'),
									  TangentType.Bezier: mxs.pyhelper.namify('custom'),
									  TangentType.Linear: mxs.pyhelper.namify('linear'),
									  TangentType.Stepped: mxs.pyhelper.namify('step')
	}

	# Some of the Max specific tangent types will be converted to bezier.
	_nativeToAbstractTangentTypes = { 'auto': TangentType.Automatic,
									  'custom': TangentType.Bezier,
									  'linear': TangentType.Linear,
									  'step': TangentType.Stepped,
									  'slow': TangentType.Bezier,
									  'fast': TangentType.Bezier,
									  'smooth': TangentType.Automatic
	}

	#--------------------------------------------------------------------------------
	#								private methods
	#--------------------------------------------------------------------------------
	def _nativeValue( self ):
		"""
			\remarks	implements the AbstractSceneAnimationKey._nativeValue method to return the value for this key
			\return		<variant> value
		"""
		return self._nativePointer.value
	
	def _setNativeValue( self, nativeValue ):
		"""
			\remarks	implements the AbstractSceneAnimationKey._setNativeValue method to set the native value of this key to the inputed value
			\param		nativeValue		<variant>
			\return		<bool> success
		"""
		self._nativePointer.value = nativeValue
		return True
	
	def _setNativeProperty( self, key, nativeValue ):
		"""
			\remarks	overloads the AbstractSceneAnimationKey._setNativeProperty method to catch some properties that need to be converted to names
			\param		key				<str>
			\param		nativeValue		<variant>
			\return 	<bool> success
		"""
		if ( key in ('inTangentType','outTangentType') ):
			nativeValue = mxs.pyhelper.namify(nativeValue)
			
		return AbstractSceneAnimationKey._setNativeProperty( self, key, nativeValue )
	
	#--------------------------------------------------------------------------------
	#								public methods
	#--------------------------------------------------------------------------------
	def propertyNames( self ):
		"""
			\remarks	overloading the AbstractSceneAnimationKey.propertyNames method to remove 'value' and 'time' from the properties since these
						should be accessed via the time/setTime and value/setValue methods
			\return		<list> [ <str> propname, .. ]
		"""
		names = AbstractSceneAnimationKey.propertyNames( self )
		if ( 'time' in names ):
			names.remove('time')
		if ( 'value' in names ):
			names.remove('value')
		return names
		
	def setTime( self, time ):
		"""
			\remarks	implements the AbstractSceneAnimationKey.setTime method to set the value of this key to the inputed value
			\param		time	<float>
			\return		<bool> success
		"""
		self._nativePointer.time = time
		return True
	
	def time( self ):
		"""
			\remarks	implements the AbstractSceneAnimationKey.time method to return the time frame of this key
			\return		<float> value
		"""
		return float(self._nativePointer.time)
	
# register the symbol
import cross3d
cross3d.registerSymbol( 'SceneAnimationKey', StudiomaxSceneAnimationKey )