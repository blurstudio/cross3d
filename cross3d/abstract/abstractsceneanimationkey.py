##
#	\namespace	blur3d.api.abstract.abstractsceneanimationkey
#
#	\remarks	The AbstractSceneAnimationKey class defines a base class for managing animation curves within a 3d scene
#
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

from blur3d.api import SceneWrapper

class AbstractSceneAnimationKey( SceneWrapper ):
	#--------------------------------------------------------------------------------
	#								private methods
	#--------------------------------------------------------------------------------
	def _nativeValue( self ):
		"""
			\remarks	[abstract] return the value 
			\return		<variant> value
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return 0
	
	def _setNativeValue( self, nativeValue ):
		"""
			\remarks	[abstract] set the native value of this key to the inputed value
			\param		nativeValue		<variant>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	#--------------------------------------------------------------------------------
	#								public methods
	#--------------------------------------------------------------------------------
	def setTime( self, time ):
		"""
			\remarks	[abstract] set the value of this key to the inputed value
			\param		time	<float>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def setValue( self, value ):
		"""
			\remarks	set the value of this key to the inputed value
			\param		value	<variant>
			\return		<bool> success
		"""
		return self._setNativeValue( self._scene._toNativeValue( value ) )
		
	def time( self ):
		"""
			\remarks	[abstract] return the time frame of this key
			\return		<float> value
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return 0.0
		
	def value( self ):
		"""
			\remarks	return the value of this key
			\return		<variant> value
		"""
		return self._scene._fromNativeValue( self._nativeValue() )
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneAnimationKey', AbstractSceneAnimationKey, ifNotFound = True )