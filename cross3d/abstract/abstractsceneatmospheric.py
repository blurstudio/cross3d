##
#	\namespace	blur3d.api.abstract.abstractsceneatmospheric
#
#	\remarks	The AbstractSceneAtmospheric class provides an interface to editing atmosperhics in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

class AbstractSceneAtmospheric:
	def __eq__( self, other ):
		"""
			\remarks	compares this instance to another object
			\param		other	<variant>
			\return		<bool> equal
		"""
		if ( isinstance( other, AbstractSceneAtmospheric ) ):
			return other._nativePointer == self._nativePointer
		return False
		
	def __init__( self, scene, nativeAtmospheric ):
		"""
			\remarks	initialize the abstract scene atmospheric
		"""
		self._scene				= scene
		self._nativePointer		= nativeAtmospheric
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _nativeLayer( self ):
		"""
			\remarks	[abstract] return the layer that this atmospheric is a part of
			\sa			layer
			\return		<variant> nativeLayer || None
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return None
	
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
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
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
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def atmosName( self ):
		"""
			\remarks	[abstract] return the name of this atmospheric instance
			\sa			setAtmosphericName
			\return		<str> name
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return ''
	
	def atmosId( self ):
		"""
			\remarks	[abstract] return the unique id for this atmospheric instance
			\sa			setAtmosphericId
			\return		<int> id
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return 0
	
	def disable( self ):
		"""
			\remarks	disables this atmospheric in the scene
			\sa			enable, isEnabled, setEnabled
			\return		<bool> success
		"""
		return self.setEnabled( False )
	
	def enable( self ):
		"""
			\remarks	enables this atmospheric in the scene
			\sa			disable, isEnabled, setEnabled
			\return		<bool> success
		"""
		return self.setEnabled( True )
		
	def hasProperty( self, key ):
		"""
			\remarks	[abstract] check to see if the inputed property name exists for this atmospheric
			\sa			property, setProperty
			\param		key		<str>
			\return		<bool> found
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def isEnabled( self ):
		"""
			\remarks	[abstract] return whether or not this atmospheric is currently enabled in the scene
			\sa			disable, enable, setEnabled
			\return		<bool> enabled
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def layer( self ):
		"""
			\remarks	return the layer that this atmospheric is a part of
			\return		<blur3d.api.SceneLayer> || None
		"""
		nativeLayer = self._nativeLayer()
		if ( nativeLayer ):
			from blur3d.api import SceneLayer
			return SceneLayer( self._scene, nativeLayer )
		return None
	
	def nativePointer( self ):
		"""
			\remarks	return the pointer to the native atmospheric instance
			\return		<variant> nativeAtmospheric
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
	
	def recordXml( self, xml ):
		"""
			\remarks	record the atmospheric to the inputed xml node
			\param		xml		<blurdev.XML.XMLElement>
			\return		<bool> success
		"""
		if ( not xml ):
			return False
		
		xml.setAttribute( 'name', self.atmosName() )
		xml.setAttribute( 'id',		self.atmosId() )
		return True
	
	def scene( self ):
		"""
			\remarks	return the scene instance that this atmospheric is linked to
			\return		<blur3d.api.Scene>
		"""
		return self._scene
	
	def setAtmosName( self, atmosphericName ):
		"""
			\remarks	[abstract] set the name of this atmospheric instance
			\sa			atmosphericName
			\param		atmosphericName	<str>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def setAtmosId( self, atmosphericId ):
		"""
			\remarks	[abstract] set the unique id for this atmospheric instance
			\sa			atmosphericId
			\param		atmosphericId <int>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
			raise NotImplementedError
		
		return False
	
	def setEnabled( self, state ):
		"""
			\remarks	[abstract] set whether or not this atmospheric is currently enabled in the scene
			\sa			disable, enable, isEnabled
			\param		state		<bool>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.isDebugLevel( debug.DebugLevel.High ) ):
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
	
	@staticmethod
	def fromXml( scene, xml ):
		"""
			\remarks	restore the atmospheric from the inputed xml node
			\param		scene	<blur3d.api.Scene>
			\param		xml		<blurdev.XML.XMLElement>
			\return		<blurdev.api.SceneAtmospheric> || None
		"""
		return scene.findAtmospheric( atmosName = xml.attribute( 'name' ), atmosId = int(xml.attribute('id',0)) )
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneAtmospheric', AbstractSceneAtmospheric, ifNotFound = True )