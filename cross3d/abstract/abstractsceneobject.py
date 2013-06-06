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

from blur3d import abstractmethod
from blur3d.api import SceneWrapper
from blur3d.constants import ObjectType
from blur3d import api


class AbstractSceneObject(SceneWrapper):
	"""
	The SceneObject class provides the base foundation for the 3d 
	Object framework for the blur3d system.  This class will provide a 
	generic overview structure for all manipulations of 3d objects
	"""

	iconCache = {}
	_objectType = ObjectType.Generic
	_subClasses = {}

	def __init__(self, scene, nativeObject):
		SceneWrapper.__init__(self, scene, nativeObject)
		self._objectType = self._typeOfNativeObject(nativeObject)

	def __new__(cls, scene, nativeObject):
		"""
			\remarks	acts as a factory to return the right type of scene object
			\return		<variant> SceneObject
		"""
		#print SceneWrapper.__subclasses__()
		if not cls._subClasses:
			for c in cls._subclasses(cls):
				if not c._objectType == ObjectType.Generic:
					cls._subClasses[ c._objectType ] = c

		sceneObjectType = cls._typeOfNativeObject(nativeObject)
		if sceneObjectType in cls._subClasses:
			c = cls._subClasses[ sceneObjectType ]
			return SceneWrapper.__new__(c)
		return SceneWrapper.__new__(cls)

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------

	@abstractmethod
	def _nativeType(self):
		"""
			\remarks	finds the native type and return it as a string
			ry)
			\return		str
		"""
		return str
	def _findNativeChild(self, name, recursive=False, parent=None):
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
	def _nativeCaches(self, cacheType=0):
		"""
			\remarks	return a list of the native caches that are applied to this object
			\param		cacheType	<blur3d.constants.CacheType>	fitler by the inputed cache type
			\return		<list> [ <variant> nativeCache, .. ]
		"""
		return []

	@abstractmethod
	def _nativeChildren(self, recursive=False, wildcard='', type='', parent='', childrenCollector=[]):
		"""
			\remarks	looks up the native children for this object
			\param		recursive         <bool>
			\param		parent		      <variant> nativeObject(used for recursive searches when necessary)
			\param		childrenCollector <list> (used for recursive searches when necessary)
			\sa			children
			\return		<list> [ <variant> nativeObject, .. ]
		"""
		return []

	@abstractmethod
	def _nativeLayer(self):
		"""
			\remarks	returns the native application's layer that the object is on
			\sa			layer, setLayer, _setNativeLayer
			\return		<variant> nativeLayer || None
		"""
		return None

	@abstractmethod
	def _nativeMaterial(self):
		"""
			\remarks	returns the native material for this object
			\sa			material, setMaterial, _setNativeMaterial
			\return		<variant> nativeMaterial || None
		"""
		return None

	@abstractmethod
	def _nativeModel(self):
		"""
			\remarks	looks up the native model for this object
			\sa			model, setModel, _setNativeModel
			\return		<variant> nativeObject || None
		"""
		return None

	@abstractmethod
	def _nativeParent(self):
		"""
			\remarks	looks up the native parent for this object
			\sa			parent, setParent, _setNativeParent
			\return		<variant> nativeObject || None
		"""
		return None

	@abstractmethod
	def _nativeWireColor(self):
		"""
			\remarks	return the color for the wireframe of this object in the scene
			\sa			setWireColor
			\return		<QColor>
		"""
		return False

	@abstractmethod
	def _setNativeLayer(self, nativeLayer):
		"""
			\remarks	sets the native layer for this object
			\sa			layer, setLayer, _nativeLayer
			\param		<variant> nativeLayer || None
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setNativeMaterial(self, nativeMaterial):
		"""
			\remarks	sets the native material for this object
			\sa			material, setMaterial, _nativeMaterial
			\param		<variant> nativeMaterial || None
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setNativeModel(self, nativeModel):
		"""
			\remarks	sets the native model for this object
			\sa			model, setModel, _nativeModel
			\param		<variant> nativeObject || None
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setNativeParent(self, nativeParent):
		"""
			\remarks	sets the native parent for this object
			\sa			parent, setParent, _nativeParent
			\param		<variant> nativeObject || None
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setNativeWireColor(self, color):
		"""
			\remarks	set the wirecolor for the object to the inputed QColor
			\sa			wireColor
			\param		color	<QColor>
			\return		<bool> success
		"""
		return False

	def _nativeModel(self):
		"""
			\remarks	returns the native model this object belongs to.
			\return		<variant> model
		"""
		return None

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def getCacheName(self, type):
		"""return the str of cache name depending on software.
		"""
		
		return None
		
	def addCacheFromFile(self, cacheFile):
		"""Adds a new cache based on the inputed filename
		
		:param cacheFile: filepath to the cache
		:type cacheFile: str
		:return: :class:`blur3d.api.SceneCache` or None
			
		"""
		nativeCache = self._addNativeCacheFromFile(cacheFile)
		if (nativeCache):
			from blur3d.api import SceneCache
			return SceneCache(self._scene, nativeCache)
		return None
	
	def applyCache(self, path, type):
		"""Applies cache to object
		param Type <cache type>
		return cache object
		"""
		
		return None
	def caches(self, cacheType=0):
		"""Return a list of the caches that are applied to this object
		
		:param cacheType: :data:`blur3d.constants.CacheType`
		:return: a list of :class:`blur3d.api.SceneCache` objects
		
		"""
		from blur3d.api import SceneCache
		return [ SceneCache(self._scene, nativeCache) for nativeCache in self._nativeCaches(cacheType) ]

	def childAt(self, index):
		"""Returns the child at a particular index for this object
		
		:return: :class:`blur3d.api.SceneObject` or None
		
		"""
		nativeChildren = self._nativeChildren()
		if (0 <= index and index < len(nativeChildren)):
			return SceneObject(self._scene, nativeChildren[index])
		return None

	def childCount(self):
		"""
			\remarks	returns the number of children this object has
			\sa			childAt, children, findChild, _nativeChildren
			\return		<int>
		"""
		return len(self._nativeChildren())

	def children(self, recursive=False, wildcard='', type=''):
		"""Returns SceneObject wrappers over the children for this object
		
		:param recursive: If True, will recursively traverse child tree
		:param wildcard: ?
		:type wildcard: str
		:param type: ?
		:type type: str
		:return: list of :class:`blur3d.api.SceneObject` objects

		"""
		from blur3d.api import SceneObject
		scene = self._scene
		return [ SceneObject(scene, native) for native in self._nativeChildren(recursive, wildcard, type) ]

	def deselect(self):
		"""Deslects this object in the scene

		"""
		return self.setSelected(False)

	def findChild(self, name, recursive=False):
		"""
		Loops through the children for this object searching for the 
		proper one

		:return: :class:`blur3d.api.SceneObject` or None

		"""
		nativeChild = self._findNativeChild(name, recursive=recursive)
		if (nativeChild):
			from blur3d.api import SceneObject
			return SceneObject(self._scene, nativeChild)
		return None

	def freeze(self):
		"""Freezes/locks this item

		"""
		return self.setFrozen(True)

	def hide(self):
		"""Hides the object in the scene

		"""
		return self.setHidden(True)

	def icon(self):
		"""Returns the icon associated with this object type
		
		:return: :class:`PyQt4.QtGui.QIcon`
		
		"""
		return self.cachedIcon(self.objectType())

	@abstractmethod
	def isBoxMode(self):
		"""Returns whether or not this object is in boxMode

		"""
		return False

	@abstractmethod
	def isFrozen(self):
		"""Returns whether or not this object is frozen(locked)
		
		"""
		return False

	@abstractmethod
	def isHidden(self):
		"""Returns whether or not this object is hidden
		
		"""
		return False

	def isObjectType(self, objectType):
		"""
		Returns whether or not the inputed object type is the type of object 
		this is
		
		:param objectType: :data:`blur3d.constants.ObjectType`

		"""
		return (self._objectType & objectType) != 0

	@abstractmethod
	def isSelected(self):
		"""Returns whether or not this object is selected

		"""
		return False

	def layer(self):
		"""
		Returns the SceneLayer that this object is on, or none if no 
		layer found
		
		:return: :class:`blur3d.api.SceneLayer` or None

		"""
		nativeLayer = self._nativeLayer()
		if (nativeLayer):
			from blur3d.api import SceneLayer
			return SceneLayer(self._scene, nativeLayer)
		return None

	def material(self):
		"""
		Returns the SceneMaterial that this object is using, or none if no 
		scene material was found
		
		:return: :class:`blur3d.api.SceneMaterial` or None

		"""
		nativeMaterial = self._nativeMaterial()
		if (nativeMaterial):
			from blur3d.api import SceneMaterial
			return SceneMaterial(self._scene, nativeMaterial)
		return None

	def model(self):
		"""Returns the SceneObject that is the model for this object
		
		:return: :class:`blur3d.api.SceneObject` or None

		"""
		nativeModel = self._nativeModel()
		if (nativeModel):
			from blur3d.api import SceneObject
			return SceneObject(self._scene, nativeModel)
		return None

	def objectType(self):
		"""
		Returns the type of object this wrapper represents for the 
		native object
		
		:return: :data:`blur3d.constants.ObjectType`

		"""
		return self._objectType

	def parent(self):
		"""Returns the parent item for this object
		
		:return: :class:`blur3d.api.SceneObject` or None

		"""
		nativeParent = self._nativeParent()
		if (nativeParent):
			from blur3d.api import SceneObject
			return SceneObject(self._scene, nativeParent)
		return None

	def select(self):
		"""Selects this object in the scene

		"""
		return self.setSelected(True)

	@abstractmethod
	def setBoxMode(self, state):
		"""Sets whether this object is in boxMode

		"""
		return False

	@abstractmethod
	def setFrozen(self, state):
		"""Freezes(locks)/unfreezes(unlocks) this object

		"""
		return False

	@abstractmethod
	def setHidden(self, state):
		"""Hides/unhides this object

		"""
		return False

	def setLayer(self, layer):
		"""Sets the layer for this object to the inputed SceneLayer
		
		:param layer: :class:`blur3d.api.SceneLayer`

		"""
		nativeLayer = None
		if (layer):
			nativeLayer = layer.nativeLayer()

		return self._setNativeLayer(nativeLayer)

	def setMaterial(self, material):
		"""
		Sets the material for this object to the inputed SceneMaterial
		
		:param material: :class:`blur3d.api.SceneMaterial` or None

		"""
		nativeMaterial = None
		if (material):
			nativeObject = material.nativeMaterial()

		return self._setNativeMaterial(nativeMaterial)

	def setModel(self, model):
		"""
		Sets the model for this object to the inputed SceneObject
		
		:param model: :class:`blur3d.api.SceneObject`

		"""
		nativeModel = None
		if (model):
			nativeModel = model.nativePointer()

		return self._setNativeModel(nativeModel)

	def setParent(self, parent):
		"""Sets the parent for this object to the inputed item
		
		:param parent: :class:`blur3d.api.SceneObject` or None
		
		"""

		# set the model in particular
		if (parent and parent.isObjectType(ObjectType.Model)):
			return self._setNativeModel(parent.nativePointer())

		nativeParent = None
		if (parent):
			nativeParent = parent.nativePointer()
		return self._setNativeParent(nativeParent)

	@abstractmethod
	def setSelected(self, state):
		"""Selects/deselects this object

		"""
		return False

	@abstractmethod
	def setWireColor(self, color):
		"""Sets the wirecolor for the object to the inputed QColor
		
		:param color: :class:`PyQt4.QtGui.QColor`

		"""
		from PyQt4.QtGui import QColor
		return self._setNativeWireColor(self._scene._toNativeValue(QColor(color)))

	def translate(self, transform, relative=False):
		"""
		:param transform: A list with a length of 3 floats representing x, y, z
		:param relative: Apply the translation as relative or absolute
		"""
		self._scene.translate([self], transform, relative)

	@abstractmethod
	def translation(self, local=False):
		"""
		Returns the translation of the current object.
		:param local: If True return the local translation. Default False.
		"""
		return 0, 0, 0

	@abstractmethod
	def unfreeze(self):
		"""Unfreezes (unlocks) the object in the scene

		"""
		return self.setFrozen(False)

	@abstractmethod
	def unhide(self):
		"""Unhides the object in the scene

		"""
		return self.setHidden(False)

	@abstractmethod
	def wireColor(self):
		"""Returns the color for the wireframe of this object in the scene

		:return: :class:`PyQt4.QtGui.QColor`
		"""
		return self._scene._fromNativeValue(self._nativeWireColor())

	@abstractmethod
	def deleteProperty(self, propertyName):
		"""Delete the specified property. added by douglas.
		
		"""
		return False

	def model(self):
		"""Returns the model this object belongs to.
		
		:return: :class:`blur3d.api.SceneModel` or None
			
		"""
		from blur3d.api import Scene, SceneModel
		nativeModel = self._nativeModel()
		if nativeModel:
			return SceneModel(Scene(), nativeModel)
		return None

	def deleteProperty(self, propertyName):
		"""Deletes the property of an object.

		"""
		return False

	#------------------------------------------------------------------------------------------------------------------------
	# 												static methods
	#------------------------------------------------------------------------------------------------------------------------

	@staticmethod
	def _nativeTypeOfObjectType(objectType):
		"""
			\remarks	[virtual]	returns the nativeObject Type of the ObjectType supplied
			\param		<variant> ObjectType || None
			\return		<bool> success
		"""
		return None


	@staticmethod
	def _typeOfNativeObject(nativeObject):
		"""
			\remarks	[virtual]	returns the ObjectType of the nativeObject applied
			\param		<variant> nativeObject || None
			\return		<bool> success
		"""
		return ObjectType.Generic

	@staticmethod
	def _subclasses(cls, classes=[], includeClass=False):
		if includeClass:
			classes.append(cls)
		for subclass in cls.__subclasses__():
				cls._subclasses(subclass, classes, True)
		return classes

	@staticmethod
	def cachedIcon(objectType):
		icon = AbstractSceneObject.iconCache.get(objectType)

		# return a cached icon
		if (icon):
			return icon

		# create an icon cache

		# create a light icon
		if (objectType & ObjectType.Light):
			iconfile = 'img/objects/light.png'

		# create a camera icon
		elif (objectType & ObjectType.Camera):
			iconfile = 'img/objects/camera.png'

		# create a model icon
		elif (objectType & ObjectType.Model):
			iconfile = 'img/objects/model.png'

		# create a geometry icon
		elif (objectType & ObjectType.Geometry):
			iconfile = 'img/objects/geometry.png'

		# create a default icon
		else:
			iconfile = 'img/objects/default.png'

		# create the QIcon
		import blur3d
		from PyQt4.QtGui 		import QIcon
		icon = QIcon(blur3d.resourcePath(iconfile))
		AbstractSceneObject.iconCache[ objectType ] = icon
		return icon

	@staticmethod
	def fromXml(scene, xml):
		"""Create a new object from the inputed xml data
		
		:param xml: :class:`blurdev.XML.XMLElement`

		"""
		if (xml):
			return scene.findObject(name=xml.attribute('name'), uniqueId=int(xml.attribute('id', 0)))
		return None


# register the symbol
api.registerSymbol('SceneObject', AbstractSceneObject, ifNotFound=True)

