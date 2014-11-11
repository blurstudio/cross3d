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

from blur3d import api
from blur3d.api	import UserProps
from blur3d.constants import ControllerType
from blur3d import abstractmethod, pendingdeprecation

class AbstractSceneWrapper(object):
	"""
	The AbstractSceneWrapper class defines the base class for all other 
	scene wrapper instances.  This creates a basic wrapper class for 
	mapping native object instances from a DCC application to the blur3d 
	structure
	"""

	def __eq__(self, other):
		if (isinstance(other, AbstractSceneWrapper)):
			return other._nativePointer == self._nativePointer
		return False
	
	def __hash__(self):
		""" Returns self.uniqueId()
		NOTE: If uniqueId is not implemented for a software implemenation all objects will have a hash of 0
		"""
		return self.uniqueId()

	def __init__(self, scene, nativePointer=None):
		"""
			\remarks	initialize the abstract scene controller
		"""
		super(AbstractSceneWrapper, self).__init__()
		self._scene				 = scene
		self._nativePointer		 = nativePointer

	def __str__(self):
		return '<%s (%s)>' % (super(AbstractSceneWrapper, self).__str__().split()[0].split('.')[-1], self.displayName())

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	@abstractmethod
	def _nativeControllers(self):
		"""
			\remarks	collect a list of the native controllers that are currently applied to this cache instance
			\return		<list> [ <variant> nativeController, .. ]
		"""
		return []

	@abstractmethod
	def _nativeController(self, name):
		"""
			\remarks	find a controller for this object based on the inputed name
			\param		name		<str>
			\return		<variant> nativeController || None
		"""
		return None

	@abstractmethod
	def _nativeCopy(self):
		"""
			\remarks	return a native copy of the instance in the scene
			\return		<variant> nativePointer || None
		"""
		return None

	@abstractmethod
	def _nativeProperty(self, key, default=None):
		"""
			\remarks	return the value of the property defined by the inputed key
			\sa			hasProperty, setProperty, _nativeProperty, AbstractScene._fromNativeValue
			\param		key			<str>
			\param		default		<variant>	(auto-converted from the application's native value)
			\return		<variant>
		"""
		return default

	@abstractmethod
	def _setNativeController(self, name, nativeController):
		"""
			\remarks	find a controller for this object based on the inputed name
			\param		name		<str>
			\param		<variant> nativeController || None
			\return		<bool> success
		"""
		return False

	@abstractmethod
	def _setNativeProperty(self, key, nativeValue):
		"""
			\remarks	set the value of the property defined by the inputed key
			\sa			hasProperty, property, setProperty, AbstractScene._toNativeValue
			\param		key		<str>
			\param		value	<variant>	(pre-converted to the application's native value)
			\retrun		<bool> success
		"""
		return False

	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def copy(self):
		"""Create a copy of this wrapper in the scene
		
		:return: :class:`blur3d.api.SceneWrapper` or None
			
		"""
		nativeCopy = self._nativeCopy()
		if (nativeCopy):
			return self.__class__(self._scene, nativeCopy)
		return None

	def controllers(self):
		"""
		Return a list of SceneAnimationControllers that are linked to this 
		object and its properties
		
		:return: list of :class:`blur3d.api.SceneAnimationController` objects
			
		"""
		from blur3d.api import SceneAnimationController
		return [ SceneAnimationController(self, nativeController) for nativeController in self._nativeControllers() ]

	def controller(self, name):
		"""
		Lookup a controller based on the inputed controllerName for this object
		
		:return: :class:`blur3d.api.SceneAnimationController` or None
		
		"""
		nativeController = self._nativeController(name)
		if (nativeController):
			from blur3d.api import SceneAnimationController
			return SceneAnimationController(self._scene, nativeController)
		return None

	def displayName(self):
		"""
		Returns the display name for this wrapper instance, if not 
		reimplemented, then it will just return the name of the object

		"""
		return self.name()

	@abstractmethod
	def hasProperty(self, key):
		"""
		Check to see if the inputed property name exists for this controller

		"""
		return False

	@abstractmethod
	def namespace(self):
		return ''

	@abstractmethod
	def setNamespace(self):
		return False

	@abstractmethod
	def name(self):
		"""
		Return the name of this controller instance

		"""
		return ''

	def nativePointer(self):
		"""
		Return the pointer to the native controller instance

		"""
		return self._nativePointer

	def property(self, key, default=None):
		"""
		Return the value of the property defined by the inputed key
		
		"""
		return self._scene._fromNativeValue(self._nativeProperty(key, default))

	@abstractmethod
	def propertyNames(self):
		"""
		Return a list of the property names linked to this instance
		
		:return: list of names
		
		"""
		return []

	def recordXml(self, xml):
		"""
		Define a way to record this controller to xml
		
		:param xml: :class:`blurdev.XML.XMLElement`

		"""
		if (not xml):
			return False

		xml.setAttribute('name', 	self.name())
		xml.setAttribute('id', 	self.uniqueId())
		return True

	def scene(self):
		"""
		Return the scene instance that this wrapper instance is linked to
		
		:return: :class:`blur3d.api.Scene`
		
		"""
		return self._scene

	def setController(self, name, controller):
		"""
		lookup a controller based on the inputed controllerName for this 
		object
		
		:param name: str
		:param controller: :class:`blur3d.api.SceneAnimationController` or None

		"""

		if isinstance(controller, api.FCurve):
			fCurve = controller
			nativeController = api.SceneAnimationController._abstractToNativeTypes.get(ControllerType.BezierFloat)()
			controller = api.SceneAnimationController(self, nativeController)
			controller.setFCurve(fCurve)

		elif not isinstance(controller, SceneAnimationController):
			raise Exception('Argument 2 should be an instance of SceneAnimationController of FCurve.')

		return self._setNativeController(name, controller.nativePointer())

	@pendingdeprecation('Use setDisplayName() instead. Call setDisplayName to rename parent objects/Models.')
	def setName(self, name):
		"""
		Returns the full name of this object, including any model information in xsi.

		"""
		return self.setDisplayName(name)

	@abstractmethod
	def setDisplayName(self, name):
		"""
		Set the display name for this wrapper instance to the inputed 
		name - if not reimplemented, then it will set the object's actual 
		name to the inputed name

		"""
		return False

	def setProperty(self, key, value):
		"""Set the value of the property defined by the inputed key

		"""
		return self._setNativeProperty(key, self._scene._toNativeValue(value))

	@abstractmethod
	def setUniqueId(self, uniqueId):
		"""Set the unique id for this wrapper instance

		"""
		return False

	def setUserProps(self, newDict):
		"""
		Ovewrites the current custom properties with the provided dict
		
		:param newDict: dict
		
		"""
		props = UserProps(self._nativePointer)
		props.clear()
		props.update(newDict)

	@abstractmethod
	def uniqueId(self):
		"""Return the unique id for this controller instance

		"""
		return 0

	def userProps(self):
		"""Returns the UserProps object associated with this element
		
		:return; :class:`blur3d.api.UserProps`
		
		"""
		return UserProps(self._nativePointer)

	#------------------------------------------------------------------------------------------------------------------------
	# 												static/class methods
	#------------------------------------------------------------------------------------------------------------------------
	@classmethod
	def fromXml(cls, scene, xml):
		"""Create a new wrapper instance from the inputed xml data
		
		:param xml: :class:`blurdev.XML.XMLElement`

		"""
		return 0


# register the symbol
api.registerSymbol('SceneWrapper', AbstractSceneWrapper, ifNotFound=True)
