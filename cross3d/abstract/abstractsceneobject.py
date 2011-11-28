##
#	\namespace	blur3d.api.abstract.abstractsceneobject
#
#	\remarks	The AbstractSceneObject class provides the base foundation for the 3d Object framework for the blur3d system
#				This class will provide a generic overview structure for all manipulations of 3d objects
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

from blur3d		import abstractmethod
from blur3d.api import SceneWrapper
from blur3d.constants import ObjectType

class AbstractSceneObject( SceneWrapper ):
	iconCache = {}
	_objectType = ObjectType.Generic
	_subClasses = {}
	
	def __init__( self, scene, nativeObject ):
		SceneWrapper.__init__( self, scene, nativeObject )
		
		self._objectType	= self._typeOfNativeObject( nativeObject )

	def __new__( cls, scene, nativeObject ):
		"""
			\remarks	acts as a factory to return the right type of scene object
			\return		<variant> SceneObject
		"""
		#print SceneWrapper.__subclasses__()
		if not cls._subClasses:
			for c in cls._subclasses( cls ):
				if not c._objectType == ObjectType.Generic:
					cls._subClasses[ c._objectType ] = c
		
		nativeType = cls._typeOfNativeObject( nativeObject )
		if nativeType in cls._subClasses:
			c = cls._subClasses[ nativeType ]
			return SceneWrapper.__new__( c )
		return SceneWrapper.__new__( cls )
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
		
	@abstractmethod
	def _findNativeChild( self, name, recursive = False, parent = None ):
		"""
			\remarks	finds the child by the name and returns it
			\sa			findChild
			\param		name		<str>
			\param		recursive	<bool>
			\param		parent		<variant> nativeObject	(used for recursive searches when necessary)
			\return		<variant> nativeObject || None
		"""
		return None
	
	@abstractmethod
	def _nativeCaches( self, cacheType = 0 ):
		"""
			\remarks	return a list of the native caches that are applied to this object
			\param		cacheType	<blur3d.constants.CacheType>	fitler by the inputed cache type
			\return		<list> [ <variant> nativeCache, .. ]
		"""
		return []
		
	@abstractmethod
	def _nativeChildren( self ):
		"""
			\remarks	looks up the native children for this object
			\sa			children
			\return		<list> [ <variant> nativeObject, .. ]
		"""
		return []
	
	@abstractmethod
	def _nativeLayer( self ):
		"""
			\remarks	returns the native application's layer that the object is on
			\sa			layer, setLayer, _setNativeLayer
			\return		<variant> nativeLayer || None
		"""
		return None
	
	@abstractmethod
	def _nativeMaterial( self ):
		"""
			\remarks	returns the native material for this object
			\sa			material, setMaterial, _setNativeMaterial
			\return		<variant> nativeMaterial || None
		"""
		return None
	
	@abstractmethod
	def _nativeModel( self ):
		"""
			\remarks	looks up the native model for this object
			\sa			model, setModel, _setNativeModel
			\return		<variant> nativeObject || None
		"""
		return None
	
	@abstractmethod
	def _nativeParent( self ):
		"""
			\remarks	looks up the native parent for this object
			\sa			parent, setParent, _setNativeParent
			\return		<variant> nativeObject || None
		"""
		return None
	
	@abstractmethod
	def _nativeWireColor( self ):
		"""
			\remarks	return the color for the wireframe of this object in the scene
			\sa			setWireColor
			\return		<QColor>
		"""
		return False
	
	@abstractmethod
	def _setNativeLayer( self, nativeLayer ):
		"""
			\remarks	sets the native layer for this object
			\sa			layer, setLayer, _nativeLayer
			\param		<variant> nativeLayer || None
			\return		<bool> success
		"""
		return False
	
	@abstractmethod
	def _setNativeMaterial( self, nativeMaterial ):
		"""
			\remarks	sets the native material for this object
			\sa			material, setMaterial, _nativeMaterial
			\param		<variant> nativeMaterial || None
			\return		<bool> success
		"""
		return False
	
	@abstractmethod
	def _setNativeModel( self, nativeModel ):
		"""
			\remarks	sets the native model for this object
			\sa			model, setModel, _nativeModel
			\param		<variant> nativeObject || None
			\return		<bool> success
		"""
		return False
	
	@abstractmethod
	def _setNativeParent( self, nativeParent ):
		"""
			\remarks	sets the native parent for this object
			\sa			parent, setParent, _nativeParent
			\param		<variant> nativeObject || None
			\return		<bool> success
		"""
		return False
	
	@abstractmethod
	def _setNativeWireColor( self, color ):
		"""
			\remarks	set the wirecolor for the object to the inputed QColor
			\sa			wireColor
			\param		color	<QColor>
			\return		<bool> success
		"""
		return False
		
	def _nativeModel( self ):
		"""
			\remarks	returns the native model this object belongs to.
			\return		<variant> model
		"""
		return None
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def addCacheFromFile( self, cacheFile ):
		"""
			\remarks	adds a new cache based on the inputed filename
			\param		cacheFile	<str>
			\return		<blur3d.api.SceneCache> || None
		"""
		nativeCache = self._addNativeCacheFromFile( cacheFile )
		if ( nativeCache ):
			from blur3d.api import SceneCache
			return SceneCache( self._scene, nativeCache )
		return None
		
	def caches( self, cacheType = 0 ):
		"""
			\remarks	return a list of the caches that are applied to this object
			\param		cacheType	<blur3d.constants.CacheType>	filter by the inputed cache type
			\return		<list> [ <blur3d.api.SceneCache> , .. ]
		"""
		from blur3d.api import SceneCache
		return [ SceneCache( self._scene, nativeCache ) for nativeCache in self._nativeCaches( cacheType ) ]
	
	def deslect( self ):
		"""
			\remarks	deselects the object in the scene
			\sa			isSelected, select, setSelected
			\return		<bool> success
		"""
		return self.setSelected(False)
		
	def childAt( self, index ):
		"""
			\remarks	returns the child at a particular index for this object
			\sa			childCount, children, findChild, _nativeChildren
			\param		index	<int>
			\return		<blur3d.api.SceneObject> || None
		"""
		nativeChildren = self._nativeChildren()
		if ( 0 <= index and index < len(nativeChildren) ):
			return SceneObject( self._scene, nativeChildren[index] )
		return None
	
	def childCount( self ):
		"""
			\remarks	returns the number of children this object has
			\sa			childAt, children, findChild, _nativeChildren
			\return		<int>
		"""
		return len( self._nativeChildren() )
	
	def children( self ):
		"""
			\remarks	returns SceneObject wrappers over the children for this object
			\sa			childAt, childCount, findChild, _nativeChildren
			\return		<list> [ <blur3d.api.SceneObject>, .. ]
		"""
		from blur3d.api import SceneObject
		scene = self._scene
		return [ SceneObject( scene, native ) for native in self._nativeChildren() ]
	
	def deselect( self ):
		"""
			\remarks	deslects this object in the scene
			\sa			isSelected, select, setSelected
			\return		<bool> success
		"""
		return self.setSelected( False )
	
	def findChild( self, name, recursive = False ):
		"""
			\remarks	loops through the children for this object searching for the proper one
			\sa			childAt, childCount, children, _nativeChildren, _findNativeChild
			\param		name	<str>
			\param		recursive <bool>
			\return		<blur3d.api.SceneObject> || None
		"""
		nativeChild = self._findNativeChild( name, recursive = recursive )
		if ( nativeChild ):
			from blur3d.api import SceneObject
			return SceneObject( self._scene, nativeChild )
		return None
	
	def freeze( self ):
		"""
			\remarks	freezes/locks this item
			\sa			isFrozen, setFrozen, unfreeze
			\return		<bool> success
		"""
		return self.setFrozen( True )
	
	def hide( self ):
		"""
			\remarks	hides the object in the scene
			\sa			isHidden, setHidden, unhide
			\return		<bool> success
		"""
		return self.setHidden( True )
	
	def icon( self ):
		"""
			\remarks	returns the icon associated with this object type
			\return		<QIcon>
		"""
		return self.cachedIcon( self.objectType() )
		
	@abstractmethod
	def isFrozen( self ):
		"""
			\remarks	returns whether or not this object is frozen(locked)
			\sa			freeze, setFrozen, unfreeze
			\return		<bool> frozen
		"""
		return False
	
	@abstractmethod
	def isHidden( self ):
		"""
			\remarks	returns whether or not this object is hidden
			\sa			hide, setHidden, unhide
			\return		<bool> hidden
		"""
		return False
	
	def isObjectType( self, objectType ):
		"""
			\remarks	returns whether or not the inputed object type is the type of object this is
			\sa			objectType, setObjectType, _typeOfNativeObject
			\param		objectType	<blur3d.constants.ObjectType>
			\return		<bool> matches
		"""
		return (self._objectType & objectType) != 0
	
	@abstractmethod
	def isSelected( self ):
		"""
			\remarks	returns whether or not this object is selected
			\sa			deselect, select, setSelected
			\return		<bool> selected
		"""
		return False
		
	def layer( self ):
		"""
			\remarks	returns the SceneLayer that this object is on, or none if no layer found
			\sa			setLayer, _nativeLayer
			\return		<blur3d.api.SceneLayer> || None
		"""
		nativeLayer = self._nativeLayer()
		if ( nativeLayer ):
			from blur3d.api import SceneLayer
			return SceneLayer( self._scene, nativeLayer )
		return None
	
	def material( self ):
		"""
			\remarks	returns the SceneMaterial that this object is using, or none if no scene material was found
			\sa			setMaterial, _nativeMaterial, _setNativeMaterial
			\return		<blur3d.api.SceneMaterial> || None
		"""
		nativeMaterial = self._nativeMaterial()
		if ( nativeMaterial ):
			from blur3d.api import SceneMaterial
			return SceneMaterial( self._scene, nativeMaterial )
		return None
	
	def model( self ):
		"""
			\remarks	returns the SceneObject that is the model for this object
			\sa			setModel, _nativeModel, _setNativeModel
			\return		<blur3d.api.SceneObject> || None
		"""
		nativeModel = self._nativeModel()
		if ( nativeModel ):
			from blur3d.api import SceneObject
			return SceneObject( self._scene, nativeModel )
		return None
	
	def objectType( self ):
		"""
			\remarks	returns the type of object this wrapper represents for the native object
			\sa			isObjectType, setObjectType, _typeOfNativeObject
			\return		<blur3d.constants.ObjectType>
		"""
		return self._objectType
	
	def parent( self ):
		"""
			\remarks	returns the parent item for this object
			\sa			setParent, _nativeParent, _setNativeParent
			\return		<blur3d.api.SceneObject> || None
		"""
		nativeParent = self._nativeParent()
		if ( nativeParent ):
			from blur3d.api import SceneObject
			return SceneObject( self._scene, nativeParent )
		return None
	
	def select( self ):
		"""
			\remarks	selects this object in the scene
			\sa			deselect, isSelected, setSelected
			\return		<bool> success
		"""
		return self.setSelected(True)
	
	@abstractmethod
	def setFrozen( self, state ):
		"""
			\remarks	freezes(locks)/unfreezes(unlocks) this object
			\sa			freeze, isFrozen, unfreeze
			\param		state	<bool>
			\return		<bool> success
		"""
		return False
	
	@abstractmethod
	def setHidden( self, state ):
		"""
			\remarks	hides/unhides this object
			\sa			hide, isHidden, unhide
			\param		state	<bool>
			\return		<bool> success
		"""
		return False
	
	def setLayer( self, layer ):
		"""
			\remarks	sets the layer for this object to the inputed SceneLayer
			\sa			layer, _setNativeLayer
			\param		layer	<blur3d.api.SceneLayer> || None
			\return		<bool> success
		"""
		nativeLayer = None
		if ( layer ):
			nativeLayer = layer.nativeLayer()
			
		return self._setNativeLayer( nativeLayer )
	
	def setMaterial( self, material ):
		"""
			\remarks	sets the material for this object to the inputed SceneMaterial
			\sa			material, _nativeMaterial, _setNativeMaterial
			\param		material	<blur3d.api.SceneMaterial> || None
			\return		<bool> success
		"""
		nativeMaterial = None
		if ( material ):
			nativeObject = material.nativeMaterial()
			
		return self._setNativeMaterial( nativeMaterial )
	
	def setModel( self, model ):
		"""
			\remarks	sets the model for this object to the inputed SceneObject
			\sa			model, _setNativeModel
			\param		model	<blur3d.api.SceneObject> || None
			\return		<bool> success
		"""
		nativeModel = None
		if ( model ):
			nativeModel = model.nativePointer()
			
		return self._setNativeModel( nativeModel )
	
	def setParent( self, parent ):
		"""
			\remarks	sets the parent for this object to the inputed item
			\sa			parent, _nativeParent, _setNativeParent
			\param		parent	<blur3d.api.SceneObject> || None
			\return		<bool> success
		"""
		
		# set the model in particular
		if ( parent and parent.isObjectType( ObjectType.Model ) ):
			return self._setNativeModel( parent.nativePointer() )
		
		nativeParent = None
		if ( parent ):
			nativeParent = parent.nativePointer()
		return self._setNativeParent( nativeParent )
			
	@abstractmethod
	def setSelected( self, state ):
		"""
			\remarks	selects/deselects this object
			\sa			deselect, isSelected, select
			\param		state	<bool>
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def setWireColor( self, color ):
		"""
			\remarks	sets the wirecolor for the object to the inputed QColor
			\sa			wireColor
			\param		color	<QColor>
			\return		<bool> success
		"""
		from PyQt4.QtGui import QColor
		return self._setNativeWireColor( self._scene._toNativeValue( QColor(color) ) )

	@abstractmethod
	def unfreeze( self ):
		"""
			\remarks	unfreezes (unlocks) the object in the scene
			\sa			freeze, isFrozen, setFrozen
			\return		<bool> success
		"""
		return self.setFrozen( False )

	@abstractmethod
	def unhide( self ):
		"""
			\remarks	unhides the object in the scene
			\sa			hide, isHidden, setHidden
			\return		<bool> success
		"""
		return self.setHidden( False )

	@abstractmethod
	def wireColor( self ):
		"""
			\remarks	returns the color for the wireframe of this object in the scene
			\sa			setWireColor, _nativeWireColor, _setNativeWireColor
			\return		<QColor>
		"""
		return self._scene._fromNativeValue( self._nativeWireColor() )

	@abstractmethod
	def deleteProperty( self, propertyName ):
		"""
			\remarks	delete the specified property. added by douglas.
			\param		propertyName <str>
			\return		<bool> success
		"""
		return False
		
	def model( self ):
		"""
			\remarks	returns the model this object belongs to.
			\return		<blur3d.api.SceneModel> || None
		"""
		from blur3d.api import Scene, SceneModel
		nativeModel = self._nativeModel()
		if nativeModel:
			return SceneModel( Scene(), nativeModel )
		return None
		
	def deleteProperty( self, propertyName ):
		"""
			\remarks	deletes the property of an object. added by douglas
			\param		propertyName <str>
			\return		<bool> success
		"""
		return False

	#------------------------------------------------------------------------------------------------------------------------
	# 												static methods
	#------------------------------------------------------------------------------------------------------------------------

	@staticmethod
	def _typeOfNativeObject( nativeObject ):
		"""
			\remarks	[virtual]	returns the ObjectType of the nativeObject applied
			\param		<variant> nativeObject || None
			\return		<bool> success
		"""
		return ObjectType.Generic
		
	@staticmethod
	def _subclasses( cls, classes=[], includeClass=False ):
		if includeClass:
			classes.append( cls )
		for subclass in cls.__subclasses__():
				cls._subclasses( subclass, classes, True )
		return classes
		
	@staticmethod
	def cachedIcon( objectType ):
		icon = AbstractSceneObject.iconCache.get( objectType )
		
		# return a cached icon
		if ( icon ):
			return icon
		
		# create an icon cache
		
		# create a light icon
		if ( objectType & ObjectType.Light ):
			iconfile = 'img/objects/light.png'
		
		# create a camera icon
		elif ( objectType & ObjectType.Camera ):
			iconfile = 'img/objects/camera.png'
		
		# create a model icon
		elif ( objectType & ObjectType.Model ):
			iconfile = 'img/objects/model.png'
		
		# create a geometry icon
		elif ( objectType & ObjectType.Geometry ):
			iconfile = 'img/objects/geometry.png'
		
		# create a default icon
		else:
			iconfile = 'img/objects/default.png'
		
		# create the QIcon
		import blur3d
		from PyQt4.QtGui 		import QIcon
		icon = QIcon( blur3d.resourcePath( iconfile ) )
		AbstractSceneObject.iconCache[ objectType ] = icon
		return icon
	
	@staticmethod
	def fromXml( scene, xml ):
		"""
			\remarks	create a new object from the inputed xml data
			\param		xml		<blurdev.XML.XMLElement>
			\return		
		"""
		if ( xml ):
			return scene.findObject( name = xml.attribute( 'name' ), uniqueId = int(xml.attribute( 'id', 0 )) )
		return None

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneObject', AbstractSceneObject, ifNotFound = True )