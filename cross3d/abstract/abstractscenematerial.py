##
#	\namespace	blur3d.api.abstract.abstractscenematerial
#
#	\remarks	The AbstractSceneMaterial class provides an interface to editing materials in a Scene environment for any DCC application
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		09/08/10
#

from blurdev import debug

class AbstractSceneMaterial:
	def __eq__( self, other ):
		"""
			\remarks	compares this instance to another object
			\param		other	<variant>
			\return		<bool> equal
		"""
		if ( isinstance( other, AbstractSceneMaterial ) ):
			return other._nativePointer == self._nativePointer
		return False
		
	def __init__( self, scene, nativeMaterial ):
		"""
			\remarks	initialize the abstract scene material
		"""
		self._scene				= scene
		self._nativePointer		= nativeMaterial
	
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
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def edit( self ):
		"""
			\remarks	[abstract] allow the user to edit the material
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
		
	def hasProperty( self, key ):
		"""
			\remarks	[abstract] check to see if the inputed property name exists for this material
			\sa			property, setProperty
			\param		key		<str>
			\return		<bool> found
		"""
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def materialName( self ):
		"""
			\remarks	[abstract] return the name of this material instance
			\sa			setMaterialName
			\return		<str> name
		"""
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return ''
	
	def materialId( self ):
		"""
			\remarks	[abstract] return the unique id for this material instance
			\sa			setMaterialId
			\return		<int> id
		"""
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return 0
	
	def nativePointer( self ):
		"""
			\remarks	return the pointer to the native material instance
			\return		<variant> nativeMaterial
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
			\remarks	define a way to record this material to xml
			\param		xml		<blurdev.XML.XMLElement>
			\return		<bool> success
		"""
		if ( not xml ):
			return False
		
		xml.setAttribute( 'name', 	self.materialName() )
		xml.setAttribute( 'id', 	self.materialId() )
		return True
	
	def scene( self ):
		"""
			\remarks	return the scene instance that this material is linked to
			\return		<blur3d.api.Scene>
		"""
		return self._scene
	
	def setMaterialName( self, materialName ):
		"""
			\remarks	[abstract] set the name of this material instance
			\sa			materialName
			\param		materialName	<str>
			\return		<bool> success
		"""
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def setMaterialId( self, materialId ):
		"""
			\remarks	[abstract] set the unique id for this material instance
			\sa			materialId
			\param		materialId <int>
			\return		<bool> success
		"""
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
	
	@staticmethod
	def fromXml( scene, xml ):
		"""
			\remarks	create a new material from the inputed xml data
			\param		xml		<blurdev.XML.XMLElement>
			\return		
		"""
		if ( not xml ):
			return None
		mname 	= xml.attribute( 'name' )
		mid		= int(xml.attribute( 'id', 0 ))
		return scene.findMaterial( mname, mid )
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneMaterial', AbstractSceneMaterial, ifNotFound = True )