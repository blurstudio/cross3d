##
#	\namespace	cross3d.abstract.abstractsceneobject
#
#	\remarks	The AbstractSceneObject class provides the base foundation for the 3d Object framework for the cross3d system
#				This class will provide a generic overview structure for all manipulations of 3d objects
#	
#	\author		eric
#	\author		Blur Studio 
#	\date		03/15/10
#

import cross3d
from Qt.QtGui import QColor
from cross3d import SceneWrapper, abstractmethod
from cross3d.constants import ObjectType, RotationOrder

class AbstractSceneObject(SceneWrapper):

	"""
		The SceneObject class provides the base foundation for the 3d 
		Object framework for the cross3d system.  This class will provide a 
		generic overview structure for all manipulations of 3d objects
	"""

	_objectType = ObjectType.Generic
	_subClasses = {}

	def __init__(self, scene, nativeObject):
		SceneWrapper.__init__(self, scene, nativeObject)

		# This is for further type definition for generic objects we did not implement in the API.
		if self._objectType & ObjectType.Generic:
			self._objectType = self._typeOfNativeObject(nativeObject)

		self._parameters = {}

	def __new__(cls, scene, nativeObject, *args, **kwargs):
		"""
			\remarks	acts as a factory to return the right type of scene object
			\return		<variant> SceneObject
		"""
		if not cls._subClasses:
			for c in cls._subclasses(cls):
				if not c._objectType == ObjectType.Generic:
					cls._subClasses[ c._objectType ] = c

		sceneObjectType = cls._typeOfNativeObject(nativeObject)
			
		if sceneObjectType in cls._subClasses:
			c = cls._subClasses[sceneObjectType]
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
			\param		cacheType	<cross3d.constants.CacheType>	fitler by the inputed cache type
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

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	#
	@abstractmethod
	def boundingBox(self):
		""" Returns a blur3d.lib.cartesian.BoundingBox object representing the bounding box of the SceneObject.
		"""
		return False
	
	def getCacheName(self, type):
		"""return the str of cache name depending on software.
		"""
		
		return None
	
	def addController(self, name, group='', tpe=float, default=0.0):
		from cross3d import SceneAnimationController
		return SceneAnimationController(self._scene, self._addNativeController(name, group, tpe, default))

	@abstractmethod
	def _addNativeController(self, name, group='', tpe=float, default=0.0):
		return False

	def addCacheFromFile(self, cacheFile):
		"""Adds a new cache based on the inputed filename
		
		:param cacheFile: filepath to the cache
		:type cacheFile: str
		:return: :class:`cross3d.SceneCache` or None
			
		"""
		nativeCache = self._addNativeCacheFromFile(cacheFile)
		if (nativeCache):
			from cross3d import SceneCache
			return SceneCache(self._scene, nativeCache)
		return None
	
	def animationRange(self):
		""" Returns the animated range from the first to the last key frame.

		Returns:
			FrameRange: The animated range.
		"""
		return FrameRange((0, 0))

	def applyCache(self, path, type):
		"""Applies cache to object
		param Type <cache type>
		return cache object
		"""
		
		return None
	def caches(self, cacheType=0):
		"""Return a list of the caches that are applied to this object
		
		:param cacheType: :data:`cross3d.constants.CacheType`
		:return: a list of :class:`cross3d.SceneCache` objects
		
		"""
		from cross3d import SceneCache
		return [ SceneCache(self._scene, nativeCache) for nativeCache in self._nativeCaches(cacheType) ]

	def childAt(self, index):
		"""Returns the child at a particular index for this object
		
		:return: :class:`cross3d.SceneObject` or None
		
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
		:return: list of :class:`cross3d.SceneObject` objects

		"""
		from cross3d import SceneObject
		scene = self._scene
		return [SceneObject(scene, native) for native in self._nativeChildren(recursive, wildcard, type)]

	def constrainedObjects(self):
		from cross3d import SceneObject
		return [SceneObject(self._scene, nativeObject) for nativeObject in self._constrainedNativeObjects()]

	@abstractmethod
	def _constrainedNativeObjects(self):
		return []

	def constrainingObjects(self):
		from cross3d import SceneObject
		return [SceneObject(self._scene, nativeObject) for nativeObject in self._constrainingNativeObjects()]

	@abstractmethod
	def _constrainingNativeObjects(self):
		return []

	def convertCachesOriginalPlaybackToCurvePlayback(self, alembic=True):
		""" Takes all PC modifiers and TMC controllers and convert their original playback to a linear curve playback.

		This is used as a base setup for further time alterations.
		"""
		return False
		
	def deselect(self):
		"""Deslects this object in the scene

		"""
		return self.setSelected(False)

	def findChild(self, name, recursive=False):
		"""
		Loops through the children for this object searching for the 
		proper one

		:return: :class:`cross3d.SceneObject` or None

		"""
		nativeChild = self._findNativeChild(name, recursive=recursive)
		if (nativeChild):
			from cross3d import SceneObject
			return SceneObject(self._scene, nativeChild)
		return None

	@abstractmethod
	def matchTransforms(self, obj, position=True, rotation=True, scale=True):
		return False

	def freeze(self):
		"""
			Freezes/locks this item
		"""
		return self.setFrozen(True)

	def hide(self):
		"""
			Hides the object in the scene
		"""
		return self.setHidden(True)

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
		
		:param objectType: :data:`cross3d.constants.ObjectType`

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
		
		:return: :class:`cross3d.SceneLayer` or None

		"""
		nativeLayer = self._nativeLayer()
		if (nativeLayer):
			from cross3d import SceneLayer
			return SceneLayer(self._scene, nativeLayer)
		return None

	@abstractmethod
	def transformLocks(self, manipulation=True, keyability=False):
		""" Returns a dictionary of position, rotation and scale values. This dictionary
		can be passed to setTransformsLocks.
		:param manipulation: Flags if manipulation will be affected. Defaults to True.
		:param keyability: Flags if keyability will be affected. Defaults to False. (Not implemented.)
		"""
		return {'position': 'xyz', 'rotation': 'xyz', 'scale': 'xyz'}

	@abstractmethod
	def setTransformsLocks(self, position=None, rotation=None, scale=None, manipulation=True, keyability=False):
		"""
			Takes True, False, None or a string containing desired axis letters.
			Uppercase locks, lowercase unlocks, not provided ignores.
			:param position: Defaults to None.
			:param rotation: Defaults to None.
			:param scale: Defaults to None.
			:param manipulation: Flags if manipulation will be affected.
			:param keyability: Flags if keyability will be affected. Not implemented.
		"""
		return False
		
	def material(self):
		"""
		Returns the SceneMaterial that this object is using, or none if no 
		scene material was found
		
		:return: :class:`cross3d.SceneMaterial` or None

		"""
		nativeMaterial = self._nativeMaterial()
		if (nativeMaterial):
			from cross3d import SceneMaterial
			return SceneMaterial(self._scene, nativeMaterial)
		return None

	def model(self):
		"""Returns the SceneObject that is the model for this object
		
		:return: :class:`cross3d.SceneObject` or None

		"""
		nativeModel = self._nativeModel()
		if (nativeModel):
			from cross3d import SceneObject
			return SceneObject(self._scene, nativeModel)
		return None

	def objectType(self):
		"""
		Returns the type of object this wrapper represents for the 
		native object
		
		:return: :data:`cross3d.constants.ObjectType`

		"""
		return self._objectType

	def parent(self):
		"""
			Returns the parent item for this object	
			:return: :class:`cross3d.SceneObject` or None
		"""
		nativeParent = self._nativeParent()
		if (nativeParent):
			from cross3d import SceneObject
			return SceneObject(self._scene, nativeParent)
		return None

	@abstractmethod
	def resetTransforms(self, pos=True, rot=True, scl=True):
		"""
			Resets the transforms to zero.
		"""
		return False
		
	@abstractmethod
	def rotation(self, local=False):
		"""
			Returns the rotation of the current object.
			:param local: If True return the local rotation. Default False.
		"""
		return 0, 0, 0

	@abstractmethod
	def rotationOrder(self):
		""" Returns the cross3d.constants.RotationOrder enum for this object or zero """
		return 0

	@classmethod
	@abstractmethod
	def _setNativeRotationOrder(cls, nativePointer, order):
		""" Sets the transform rotation order for the provided object to the provided value.
		
		Args:
			order: cross3d.constants.RotationOrder enum
		"""
		return None

	def setRotationOrder(self, order):
		""" Sets the transform rotation order for this object. 
		
		Args:
			order: cross3d.constants.RotationOrder enum
		"""
		return self._setNativeRotationOrder(self._nativePointer, order)

	def select(self):
		"""
			Selects this object in the scene
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
		"""
			Hides/unhides this object
		"""
		return False
	
	@abstractmethod
	def key(self, target='keyable'):
		"""
			Set keys on the object parameters.
		"""
		return False

	@abstractmethod
	def keyframeTimeControllers(self, alembic=True):
		return False

	@abstractmethod
	def keyedFrames(self, start=None, end=None):
		return []
		
	def setLayer(self, layer):
		"""Sets the layer for this object to the inputed SceneLayer
		
		:param layer: :class:`cross3d.SceneLayer`

		"""
		nativeLayer = None
		if (layer):
			nativeLayer = layer.nativeLayer()

		return self._setNativeLayer(nativeLayer)

	def setMaterial(self, material):
		"""
		Sets the material for this object to the inputed SceneMaterial
		
		:param material: :class:`cross3d.SceneMaterial` or None

		"""
		nativeMaterial = None
		if (material):
			nativeObject = material.nativeMaterial()

		return self._setNativeMaterial(nativeMaterial)

	def setModel(self, model):
		"""
		Sets the model for this object to the inputed SceneObject
		
		:param model: :class:`cross3d.SceneObject`

		"""
		nativeModel = None
		if (model):
			nativeModel = model.nativePointer()

		return self._setNativeModel(nativeModel)

	def setParent(self, parent):
		"""Sets the parent for this object to the inputed item
		
		:param parent: :class:`cross3d.SceneObject` or None
		
		"""

		# set the model in particular
		if parent and parent.isObjectType(ObjectType.Model):
			self._setNativeModel(parent.nativePointer())

		nativeParent = parent.nativePointer() if parent else None
		return self._setNativeParent(nativeParent)

	def setRotation(self, axes, relative=False):
		"""
		Rotates the provided objects in the scene
		:param axes: A list with a length of 3 floats representing x, y, z
		:param relative: Apply the rotation as relative or absolute. Absolute by default.
		"""
		self._scene.setRotation([self], axes, relative)

	@abstractmethod
	def setSelected(self, state):
		"""Selects/deselects this object

		"""
		return False

	@abstractmethod
	def setWireColor(self, color):
		"""Sets the wirecolor for the object to the inputed QColor
		
		:param color: :class:`Qt.QtGui.QColor`

		"""
		return self._setNativeWireColor(self._scene._toNativeValue(QColor(color)))

	@abstractmethod
	def shapes(self):
		""" Returns a generator used to access all shape nodes that are children of this object
		
		Returns:
			generator: SceneObjects representing the shape children of this object
		"""
		yield self

	def translate(self, axes, relative=False):
		"""
		:param axes: A list with a length of 3 floats representing x, y, z
		:param relative: Apply the translation as relative or absolute
		"""
		self._scene.translate([self], axes, relative)

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

		:return: :class:`Qt.QtGui.QColor`
		"""
		return self._scene._fromNativeValue(self._nativeWireColor())

	@classmethod
	@abstractmethod
	def defaultRotationOrder(cls):
		""" The default rotation order when creating new cameras.
		
		Returns:
			cross3d.constants.RotationOrder
		"""
		return RotationOrder.XYZ

	@abstractmethod
	def deleteProperty(self, propertyName):
		"""Delete the specified property. added by douglas.
		
		"""
		return False

	@abstractmethod
	def parameters(self):
		return {}

	@abstractmethod
	def setParameters(self, parameters):
		return False

	def deleteProperty(self, propertyName):
		"""Deletes the property of an object.

		"""
		return False

	def isDeleted(sef):
		"""
		Returns True if the native object has been deleted.
		"""
		return False

	def storeParameters(self):
		self._parameters = self.parameters()
		return True

	def restoreParameters(self):
		return self.setParameters(self._parameters)

	#------------------------------------------------------------------------------------------------------------------------
	# 												class methods
	#------------------------------------------------------------------------------------------------------------------------
	#
	@classmethod
	def _typeOfNativeObject(cls, nativeObject):
		"""
			\remarks	[virtual]	returns the ObjectType of the nativeObject applied
			\param		<variant> nativeObject || None
			\return		<bool> success
		"""
		return ObjectType.Generic

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
	def _subclasses(cls, classes=[], includeClass=False):
		if includeClass:
			classes.append(cls)
		for subclass in cls.__subclasses__():
				cls._subclasses(subclass, classes, True)
		return classes

	@staticmethod
	def fromXml(scene, xml):
		"""Create a new object from the inputed xml data
		
		:param xml: :class:`cross3d.migrate.XMLElement`

		"""
		if (xml):
			return scene.findObject(name=xml.attribute('name'), uniqueId=int(xml.attribute('id', 0)))
		return None


# register the symbol
cross3d.registerSymbol('SceneObject', AbstractSceneObject, ifNotFound=True)

