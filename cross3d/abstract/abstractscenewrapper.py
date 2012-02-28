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

from blur3d import abstractmethod, pendingdeprecation
from blur3d.api	import UserProps
from blur3d.api.abstract.blurtags import BlurTags

class AbstractSceneWrapper(object):
	def __eq__( self, other ):
		"""
			\remarks	compares this instance to another object
			\param		other	<variant>
			\return		<bool> equal
		"""
		if ( isinstance( other, AbstractSceneWrapper ) ):
			return other._nativePointer == self._nativePointer
		return False
		
	def __init__( self, scene, nativePointer = None ):
		"""
			\remarks	initialize the abstract scene controller
		"""
		super(AbstractSceneWrapper, self).__init__()
		self._scene				= scene
		self._nativePointer		= nativePointer
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	@abstractmethod
	def _nativeControllers( self ):
		"""
			\remarks	collect a list of the native controllers that are currently applied to this cache instance
			\return		<list> [ <variant> nativeController, .. ]
		"""
		return []
	
	@abstractmethod
	def _nativeController( self, name ):
		"""
			\remarks	find a controller for this object based on the inputed name
			\param		name		<str>
			\return		<variant> nativeController || None
		"""
		return None
	
	@abstractmethod
	def _nativeCopy( self ):
		"""
			\remarks	return a native copy of the instance in the scene
			\return		<variant> nativePointer || None
		"""
		return None
	
	@abstractmethod
	def _nativeProperty( self, key, default = None ):
		"""
			\remarks	return the value of the property defined by the inputed key
			\sa			hasProperty, setProperty, _nativeProperty, AbstractScene._fromNativeValue
			\param		key			<str>
			\param		default		<variant>	(auto-converted from the application's native value)
			\return		<variant>
		"""
		return default
	
	@abstractmethod
	def _setNativeController( self, name, nativeController ):
		"""
			\remarks	find a controller for this object based on the inputed name
			\param		name		<str>
			\param		<variant> nativeController || None
			\return		<bool> success
		"""
		return False
	
	@abstractmethod
	def _setNativeProperty( self, key, nativeValue ):
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
	def blurTags(self):
		"""
			\remarks	Uses CustomProperteries to store a dictionary containing all blur tags
			\return		<blur3d.api.BlurTags>
		"""
		return BlurTags(self)
	
	def copy( self ):
		"""
			\remarks	create a copy of this wrapper in the scene
			\return		<blur3d.api.SceneWrapper> || None
		"""
		nativeCopy = self._nativeCopy()
		if ( nativeCopy ):
			return self.__class__( self._scene, nativeCopy )
		return None
		
	def controllers( self ):
		"""
			\remarks	return a list of SceneAnimationControllers that are linked to this object and its properties
			\return		<list> [ <blur3d.api.SceneAnimationController> control, .. ]
		"""
		from blur3d.api import SceneAnimationController
		return [ SceneAnimationController( self, nativeController ) for nativeController in self._nativeControllers ]
		
	def controller( self, name ):
		"""
			\remarks	lookup a controller based on the inputed controllerName for this object
			\param		controllerName		<str>
			\return		<blur3d.api.SceneAnimationController> || None
		"""
		nativeController = self._nativeController( name )
		if ( nativeController ):
			from blur3d.api import SceneAnimationController
			return SceneAnimationController( self._scene, nativeController )
		return None
	
	def displayName( self ):
		"""
			\remarks	returns the display name for this wrapper instance, if not reimplemented, then it will just return
						the name of the object
			\return		<str>
		"""
		return self.name()

	@abstractmethod
	def hasProperty( self, key ):
		"""
			\remarks	check to see if the inputed property name exists for this controller
			\sa			property, setProperty
			\param		key		<str>
			\return		<bool> found
		"""
		return False
	
	@abstractmethod
	def name( self ):
		"""
			\remarks	return the name of this controller instance
			\sa			setControllerName
			\return		<str> name
		"""
		return ''
	
	def nativePointer( self ):
		"""
			\remarks	return the pointer to the native controller instance
			\return		<variant> nativeController
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
	
	@abstractmethod
	def propertyNames( self ):
		"""
			\remarks	return a list of the property names linked to this instance
			\return		<list> [ <str> propname, .. ]
		"""
		return []
	
	def recordXml( self, xml ):
		"""
			\remarks	define a way to record this controller to xml
			\param		xml		<blurdev.XML.XMLElement>
			\return		<bool> success
		"""
		if ( not xml ):
			return False
		
		xml.setAttribute( 'name', 	self.name() )
		xml.setAttribute( 'id', 	self.uniqueId() )
		return True
	
	def scene( self ):
		"""
			\remarks	return the scene instance that this wrapper instance is linked to
			\return		<blur3d.api.Scene>
		"""
		return self._scene
	
	def setController( self, name, controller ):
		"""
			\remarks	lookup a controller based on the inputed controllerName for this object
			\param		name				<str>
			\param		controller			<blur3d.api.SceneAnimationController> || None
			\return		<bool> success
		"""
		nativeController = None
		if ( controller ):
			nativeController = controller.nativePointer()
		return self._setNativeController( name, nativeController )
	
	@pendingdeprecation('Use setDisplayName() instead. Call setDisplayName to rename parent objects/Models.')
	def setName( self, name ):
		"""
			\Remarks	Returns the full name of this object, including any model information in xsi.
			\Returns	<str>
		"""
		return self.setDisplayName( name )
		
	@abstractmethod
	def setDisplayName( self, name ):
		"""
			\remarks	set the display name for this wrapper instance to the inputed name - if not reimplemented, then it will
						set the object's actual name to the inputed name
			\param		name	<str>
			\return		<bool> success
		"""
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
	
	@abstractmethod
	def setUniqueId( self, uniqueId ):
		"""
			\remarks	set the unique id for this wrapper instance
			\sa			uniqueId
			\param		uniqueId <int>
			\return		<bool> success
		"""
		return False
	
	def setUserProps(self, newDict):
		"""
			\remarks	ovewrites the current custom properties with the provided dict
			\param		newDict		<dict>
		"""
		props = UserProps(self._nativePointer)
		props.clear()
		props.update(newDict)
	
	@abstractmethod
	def uniqueId( self ):
		"""
			\remarks	return the unique id for this controller instance
			\sa			setControllerId
			\return		<int> id
		"""
		return 0
	
	def userProps(self):
		"""
			\remarks	returns the UserProps object associated with this element
			\return		<blur3d.api.UserProps>
		"""
		return UserProps(self._nativePointer)
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												static/class methods
	#------------------------------------------------------------------------------------------------------------------------
	@classmethod
	def fromXml( cls, scene, xml ):
		"""
			\remarks	create a new wrapper instance from the inputed xml data
			\param		xml		<blurdev.XML.XMLElement>
			\return		
		"""
		return 0
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneWrapper', AbstractSceneWrapper, ifNotFound = True )