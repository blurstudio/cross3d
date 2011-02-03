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

class AbstractSceneObject:
	iconCache = {}
	
	def __eq__( self, other ):
		"""
			\remarks	determines whether one 3dObject instance is equal to another by comparing the pointers to their native object pointers
			\param		other	<variant>
			\return		<bool> success
		"""
		if ( isinstance( other, AbstractSceneObject ) ):
			return self._nativePointer == other._nativePointer
		return False
		
	def __init__( self, scene, nativeObject ):
		# define custom properties
		self._scene			= scene
		self._nativePointer = nativeObject
		self._objectType	= self._typeOfNativeObject( nativeObject )
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	def _findNativeChild( self, name, recursive = False, parent = None ):
		"""
			\remarks	[abstract]	finds the child by the name and returns it
			\sa			findChild
			\param		name		<str>
			\param		recursive	<bool>
			\param		parent		<variant> nativeObject	(used for recursive searches when necessary)
			\return		<variant> nativeObject || None
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return None
		
	def _nativeChildren( self ):
		"""
			\remarks	[abstract]	looks up the native children for this object
			\sa			children
			\return		<list> [ <variant> nativeObject, .. ]
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return []
	
	def _nativeLayer( self ):
		"""
			\remarks	[abstract]	returns the native application's layer that the object is on
			\sa			layer, setLayer, _setNativeLayer
			\return		<variant> nativeLayer || None
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return None
	
	def _nativeMaterial( self ):
		"""
			\remarks	[abstract] returns the native material for this object
			\sa			material, setMaterial, _setNativeMaterial
			\return		<variant> nativeMaterial || None
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return None
	
	def _nativeModel( self ):
		"""
			\remarks	[abstract]	looks up the native model for this object
			\sa			model, setModel, _setNativeModel
			\return		<variant> nativeObject || None
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return None
	
	def _nativeParent( self ):
		"""
			\remarks	[abstract]	looks up the native parent for this object
			\sa			parent, setParent, _setNativeParent
			\return		<variant> nativeObject || None
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return None
	
	def _nativeWireColor( self ):
		"""
			\remarks	[abstract] return the color for the wireframe of this object in the scene
			\sa			setWireColor
			\return		<QColor>
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def _setNativeLayer( self, nativeLayer ):
		"""
			\remarks	[abstract]	sets the native layer for this object
			\sa			layer, setLayer, _nativeLayer
			\param		<variant> nativeLayer || None
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def _setNativeMaterial( self, nativeMaterial ):
		"""
			\remarks	[abstract]	sets the native material for this object
			\sa			material, setMaterial, _nativeMaterial
			\param		<variant> nativeMaterial || None
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def _setNativeModel( self, nativeModel ):
		"""
			\remarks	[abstract]	sets the native model for this object
			\sa			model, setModel, _nativeModel
			\param		<variant> nativeObject || None
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def _setNativeParent( self, nativeParent ):
		"""
			\remarks	[abstract]	sets the native parent for this object
			\sa			parent, setParent, _nativeParent
			\param		<variant> nativeObject || None
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def _setNativeWireColor( self, color ):
		"""
			\remarks	[abstract] set the wirecolor for the object to the inputed QColor
			\sa			wireColor
			\param		color	<QColor>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def _typeOfNativeObject( self, nativeObject ):
		"""
			\remarks	[virtual]	returns the ObjectType of the nativeObject applied
			\param		<variant> nativeObject || None
			\return		<bool> success
		"""
		from blur3d.constants import ObjectType
		return ObjectType.Generic
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def deslect( self ):
		"""
			\remarks	deselects the object in the scene
			\sa			isSelected, select, setSelected
			\return		<bool> success
		"""
		return self.setSelected(False)
		
	def displayName( self ):
		"""
			\remarks	[abstract]	looks up the display name for this object and returns it
			\sa			objectName, setDisplayName, setObjectName
			\return		<str> name
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return ''
		
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
	
	def hasProperty( self, key ):
		"""
			\remarks	[abstract]	returns whether or not the inputed key is a property of this object
			\sa			property, setProperty
			\param		key		<str>
			\return		<bool> found
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
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
		
	def isFrozen( self ):
		"""
			\remarks	[abstract]	returns whether or not this object is frozen(locked)
			\sa			freeze, setFrozen, unfreeze
			\return		<bool> frozen
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
		
	def isHidden( self ):
		"""
			\remarks	[abstract]	returns whether or not this object is hidden
			\sa			hide, setHidden, unhide
			\return		<bool> hidden
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def isObjectType( self, objectType ):
		"""
			\remarks	returns whether or not the inputed object type is the type of object this is
			\sa			objectType, setObjectType, _typeOfNativeObject
			\param		objectType	<blur3d.constants.ObjectType>
			\return		<bool> matches
		"""
		return (self._objectType & objectType) != 0
		
	def isSelected( self ):
		"""
			\remarks	[abstract]	returns whether or not this object is selected
			\sa			deselect, select, setSelected
			\return		<bool> selected
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
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
	
	def nativePointer( self ):
		"""
			\remarks	return the pointer to the native object that is wrapped
			\return		<variant> nativeObject
		"""
		return self._nativePointer
		
	def objectName( self ):
		"""
			\remarks	[abstract]	looks up the unique name for this object and returns it
			\sa			displayName, setDisplayName, setObjectName
			\return		<str> name
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return ''
	
	def objectId( self ):
		"""
			\remarks	[abstract] retrieve the unique object for this object and returns it
			\sa			setObjectId
			\return		<int> id
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return 0
	
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
	
	def property( self, key, default = None ):
		"""
			\remarks	[abstract] returns the value for the property of this object, or the default value if not found
			\sa			hasProperty, setProperty
			\param		key			<str>
			\param		default		<variant>	default return value if not found
			\return		<variant>
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return default
	
	def recordXml( self, xml ):
		"""
			\remarks	define a way to record this object to xml
			\param		xml		<blurdev.XML.XMLElement>
			\return		<bool> success
		"""
		if ( not xml ):
			return False
		
		xml.setAttribute( 'name', 	self.objectName() )
		xml.setAttribute( 'id', 	self.objectId() )
		return True
	
	def scene( self ):
		"""
			\remarks	returns the scene that this object is a part of
			\return		<blur3d.api.Scene>
		"""
		return self._scene
	
	def select( self ):
		"""
			\remarks	selects this object in the scene
			\sa			deselect, isSelected, setSelected
			\return		<bool> success
		"""
		return self.setSelected(True)
	
	def setDisplayName( self, name ):
		"""
			\remarks	[abstract]	sets the display name for this object
			\sa			displayName, objectName, setObjectName
			\param		name	<str>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def setFrozen( self, state ):
		"""
			\remarks	[abstract]  freezes(locks)/unfreezes(unlocks) this object
			\sa			freeze, isFrozen, unfreeze
			\param		state	<bool>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def setHidden( self, state ):
		"""
			\remarks	[abstract]  hides/unhides this object
			\sa			hide, isHidden, unhide
			\param		state	<bool>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
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
	
	def setObjectName( self, name ):
		"""
			\remarks	[abstract]	sets the full name for this object
			\sa			displayName, objectName, setDisplayName
			\param		name	<str>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def setObjectId( self, objectId ):
		"""
			\remarks	[abstract] set the unique object for this object to the inputed id
			\sa			objectId
			\param		objectId	<int>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def setParent( self, parent ):
		"""
			\remarks	sets the parent for this object to the inputed item
			\sa			parent, _nativeParent, _setNativeParent
			\param		parent	<blur3d.api.SceneObject> || None
			\return		<bool> success
		"""
		from blur3d.api import ObjectType
		
		# set the model in particular
		if ( parent and parent.isObjectType( ObjectType.Model ) ):
			return self._setNativeModel( parent.nativePointer() )
		
		nativeParent = None
		if ( parent ):
			nativeParent = parent.nativePointer()
		return self._setNativeParent( nativeParent )
			
	def setProperty( self, key, value ):
		"""
			\remarks	[abstract] sets the inputed object's property key to the given value
			\sa			hasProperty, property
			\param		key		<str>
			\param		value	<variant>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def setSelected( self, state ):
		"""
			\remarks	[abstract]  selects/deselects this object
			\sa			deselect, isSelected, select
			\param		state	<bool>
			\return		<bool> success
		"""
		from blurdev import debug
		
		# when debugging, raise an error
		if ( debug.debugLevel() ):
			raise NotImplementedError
		
		return False
	
	def setWireColor( self, color ):
		"""
			\remarks	[abstract]  sets the wirecolor for the object to the inputed QColor
			\sa			wireColor
			\param		color	<QColor>
			\return		<bool> success
		"""
		return self._setNativeWireColor( self._scene._toNativeValue( color ) )
	
	def unfreeze( self ):
		"""
			\remarks	unfreezes (unlocks) the object in the scene
			\sa			freeze, isFrozen, setFrozen
			\return		<bool> success
		"""
		return self.setFrozen( False )
	
	def unhide( self ):
		"""
			\remarks	unhides the object in the scene
			\sa			hide, isHidden, setHidden
			\return		<bool> success
		"""
		return self.setHidden( False )
	
	def wireColor( self ):
		"""
			\remarks	returns the color for the wireframe of this object in the scene
			\sa			setWireColor, _nativeWireColor, _setNativeWireColor
			\return		<QColor>
		"""
		return self._scene._fromNativeValue( self._nativeWireColor() )
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												static methods
	#------------------------------------------------------------------------------------------------------------------------
	
	@staticmethod
	def cachedIcon( objectType ):
		icon = AbstractSceneObject.iconCache.get( objectType )
		
		# return a cached icon
		if ( icon ):
			return icon
		
		# create an icon cache
		from blur3d.constants 	import ObjectType
		
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
			return scene.findObject( objectName = xml.attribute( 'name' ), objectId = int(xml.attribute( 'id', 0 )) )
		return None

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneObject', AbstractSceneObject, ifNotFound = True )