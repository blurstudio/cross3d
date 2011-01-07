##
#	\namespace	blur3d.classes.abstract.abstractscenemap
#
#	\remarks	The AbstractSceneMap class provides an interface to editing maps in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

class AbstractSceneMap:
	def __eq__( self, other ):
		"""
			\remarks	compares this instance to another object
			\param		other	<variant>
			\return		<bool> equal
		"""
		if ( isinstance( other, AbstractSceneMap ) ):
			return other._nativePointer == self._nativePointer
		return False
		
	def __init__( self, scene, nativeMap ):
		"""
			\remarks	initialize the abstract scene map
		"""
		self._scene				= scene
		self._nativePointer		= nativeMap
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _nativeProperty( self, key, default = None ):
		"""
			\remarks	[abstract] return the value of the property defined by the inputed key
			\sa			hasProperty, setProperty, _nativeProperty, AbstractScene._fromNativeValue
			\param		key			<str>
			\param		default		<variant>	(auto-converted from the application's native value)
			\return		<variant>
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return default
	
	def _setNativeProperty( self, key, nativeValue ):
		"""
			\remarks	[abstract] set the value of the property defined by the inputed key
			\sa			hasProperty, property, setProperty, AbstractScene._toNativeValue
			\param		key		<str>
			\param		value	<variant>	(pre-converted to the application's native value)
			\retrun		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def edit( self ):
		"""
			\remarks	[abstract] allow the user to edit the map
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
		
	def hasProperty( self, key ):
		"""
			\remarks	[abstract] check to see if the inputed property name exists for this map
			\sa			property, setProperty
			\param		key		<str>
			\return		<bool> found
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def mapName( self ):
		"""
			\remarks	[abstract] return the name of this map instance
			\sa			setMapName
			\return		<str> name
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return ''
	
	def mapId( self ):
		"""
			\remarks	[abstract] return the unique id for this map instance
			\sa			setMapId
			\return		<int> id
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return 0
	
	def nativePointer( self ):
		"""
			\remarks	return the pointer to the native map instance
			\return		<variant> nativeMap
		"""
		return self._nativePointer
	
	def property( self, key, default = None ):
		"""
			\remarks	return the value of the property defined by the inputed key
			\sa			hasProperty, setProperty, _nativeProperty
			\param		key			<str>
			\param		default		<variant>		the default value to return if the property is not found
			\return		<variant>
		"""
		return self._scene._fromNativeValue( self._nativeProperty( key, default ) )
	
	def scene( self ):
		"""
			\remarks	return the scene instance that this map is linked to
			\return		<blur3d.classes.Scene>
		"""
		return self._scene
	
	def setMapName( self, mapName ):
		"""
			\remarks	[abstract] set the name of this map instance
			\sa			mapName
			\param		mapName	<str>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def setMapId( self, mapId ):
		"""
			\remarks	[abstract] set the unique id for this map instance
			\sa			mapId
			\param		mapId <int>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
		
	def setProperty( self, key, value ):
		"""
			\remarks	set the value of the property defined by the inputed key
			\sa			hasProperty, property, _setNativeProperty
			\param		key		<str>
			\param		value	<variant>
			\retrun		<bool> success
		"""
		return self._setNativeProperty( key, self._scene._toNativeValue( value ) )
	
# register the symbol
from blur3d import classes
classes.registerSymbol( 'SceneMap', AbstractSceneMap, ifNotFound = True )