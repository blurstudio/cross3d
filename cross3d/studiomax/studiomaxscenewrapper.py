##
#	\namespace	blur3d.api.abstract.abstractscenewrapper
#
#	\remarks	The AbstractSceneWrapper class defines the base class for all other scene wrapper instances.  This creates a basic wrapper
#				class for mapping native object instances from a DCC application to the blur3d structure
#
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

from Py3dsMax									import mxs
from blur3d.api.abstract.abstractscenewrapper 	import AbstractSceneWrapper

class StudiomaxSceneWrapper( AbstractSceneWrapper ):
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _nativeCopy( self ):
		"""
			\remarks	implements the AbstractSceneWrapper._copy method to return a copy of the instance of this wrapper
			\return		<variant> nativePointer
		"""
		return mxs.copy(self._nativePointer)
	
	def _nativeController( self, name ):
		# return the controller for a property on this object
		if ( name in self.propertyNames() ):
			return mxs.getPropertyController( self._nativePointer, name )
		return None
	
	def _nativeProperty( self, key, default = None ):
		"""
			\remarks	implements the AbstractSceneWrapper._nativeProperty method to return the value of the property defined by the inputed key
			\sa			hasProperty, setProperty, _nativeProperty, AbstractScene._fromNativeValue
			\param		key			<str>
			\param		default		<variant>	(auto-converted from the application's native value)
			\return		<variant>
		"""
		return mxs.getProperty( self._nativePointer, key )
	
	def _setNativeProperty( self, key, nativeValue ):
		"""
			\remarks	implements the AbstractSceneWrapper._setNativeProperty method to set the value of the property defined by the inputed key
			\sa			hasProperty, property, setProperty, AbstractScene._toNativeValue
			\param		key		<str>
			\param		value	<variant>	(pre-converted to the application's native value)
			\retrun		<bool> success
		"""
		mxs.setProperty( self._nativePointer, key, nativeValue )
		return True
	
	def _setNativeController( self, name, nativeController ):
		# check for the property controller
		name = name.replace( '.controller', '' )
		
		# set the name
		splt = name.split( '.' )
		propname = splt[-1]
		if ( propname in self.propertyNames() ):
			mxs.setPropertyController( self._nativePointer, propname, nativeController )
			return True
		
		return False
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def hasProperty( self, key ):
		"""
			\remarks	implements the AbstractSceneWrapper.hasProperty method to check to see if the inputed property name exists for this controller
			\sa			property, setProperty
			\param		key		<str>
			\return		<bool> found
		"""
		key = str(key)
		return mxs.isProperty( self._nativePointer, key ) or mxs.hasProperty( self._nativePointer, key )
	
	
	def propertyNames( self ):
		"""
			\remarks	implements the AbstractSceneWrapper.propertyNames method to return a list of the properties that this object
						can access
			\return		<list> [ <str> propname, .. ]
		"""
		return [ str(propname) for propname in mxs.getPropNames( self._nativePointer ) ]
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneWrapper', StudiomaxSceneWrapper )