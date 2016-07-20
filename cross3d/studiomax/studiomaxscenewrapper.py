##
#	\namespace	cross3d.abstract.abstractscenewrapper
#
#	\remarks	The AbstractSceneWrapper class defines the base class for all other scene wrapper instances.  This creates a basic wrapper
#				class for mapping native object instances from a DCC application to the cross3d structure
#
#	\author		eric
#	\author		Blur Studio
#	\date		03/15/10
#

from Py3dsMax import mxs
from cross3d import UserProps
from cross3d.abstract.abstractscenewrapper import AbstractSceneWrapper

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

		# Checking inputs.
		if not isinstance(name, basestring):
			return None
			
		# Handling nested attributes. The try is here to avoid crashes. 
		# If you do not believe it, try for yourself.
		maxScript = """fn attributeValue obj = (
			value = undefined
			try value = obj.{path}
			catch()
			value
		)"""
		mxs.execute(maxScript.format(path=name))
		if mxs.attributeValue(self._nativePointer) is not None:	
			maxScript = """fn controller obj = (
				obj.{path}.controller
			)"""
			mxs.execute(maxScript.format(path=name))
			controller = mxs.controller(self._nativePointer)
			if controller is not None:
				return controller

		# Strip out controller references.
		name = name.replace('.controller', '')
		parent = self._nativePointer
		
		# look up the parent
		splt = name.split('.')
		controller = None
		parent = self._nativePointer
		
		# Start with the transform controller if necessary.
		if (splt[0] == 'transform'):
			parent = parent.controller
			controller = parent
			splt = splt[1:]
		
		for section in splt:
			controller = mxs.getPropertyController( parent, section )
			if ( not controller ):
				return None
			parent = controller
		
		return controller
	
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

		# strip out controller references
		name = name.replace( '.controller', '' )
		
		# Handling nested attributes.
		try:
			maxScript = """fn attributeValue obj = (
				return obj.{path}
			)"""
			mxs.execute(maxScript.format(path=name))
			if mxs.attributeValue(self._nativePointer) is not None:
				maxScript = """fn setController obj ctrl = (
					obj.{path}.controller = ctrl
				)"""
				mxs.execute(maxScript.format(path=name))
				mxs.setController(self._nativePointer, nativeController)
				return True
		except RuntimeError:
			pass

		# look up the parent
		splt 		= name.split( '.' )
		parent 		= self._nativePointer
		
		# start with the transform controller if necessary
		if ( splt[0] == 'transform' ):
			parent = parent.controller
			splt = splt[1:]
		
		for section in splt:
			parent = mxs.getPropertyController(parent, section)
			if ( not parent ):
				return False
		
		# set the property
		propname 	= splt[-1]
		try:
			mxs.setPropertyController( parent, propname, nativeController )
			return True
		except:
			return False
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def displayName( self ):
		"""
			\remarks	implements the AbstractSceneObject.displayName method to look up the display name for this object and returns it
			\sa			name, setDisplayName, setName
			\return		<str> name
		"""

		# This handles our virtual implementation of models in Max. A name with a dot is considered as a model namespace across the API.
		name = self._nativePointer.name
		split = name.split('.')

		# If we find a corresponding model we return the name after the dot.
		if len(split) == 2:
			model = self._scene._findNativeObject(split[0])
			if model and UserProps(model).get('model'):
				return split[1]

		# Otherwise we just return the name.
		return name

	def name( self ):
		"""
			\remarks	implements the AbstractSceneObject.name to look up the unique name for this object and returns it
			\sa			displayName, setDisplayName, setName
			\return		<str> name
		"""
		return self._nativePointer.name
		
	def setDisplayName( self, name ):
		"""
			\remarks	implements the AbstractSceneObject.setDisplayName to set the display name for this object
			\sa			displayName, name, setName
			\param		name	<str>
			\return		<bool> success
		"""

		# This handles our virtual implementation of models in Max. A name with a dot is considered as a model namespace across the API.
		split = self._nativePointer.name.split( '.' )

		# If we find a corresponding model we just set the name after the dot.
		if len(split) == 2:
			model = self._scene._findNativeObject(split[0])
			if model and UserProps(model).get('model'):
				split[-1] = unicode(name)
				name = '.'.join(split)

		self._nativePointer.name = name
		return True
		
	def hasProperty( self, key ):
		"""
			\remarks	implements the AbstractSceneWrapper.hasProperty method to check to see if the inputed property name exists for this controller
			\sa			property, setProperty
			\param		key		<str>
			\return		<bool> found
		"""
		key = unicode(key)
		return mxs.isProperty( self._nativePointer, key ) or mxs.hasProperty( self._nativePointer, key )
	
	
	def propertyNames( self ):
		"""
			\remarks	implements the AbstractSceneWrapper.propertyNames method to return a list of the properties that this object
						can access
			\return		<list> [ <str> propname, .. ]
		"""
		return [ unicode(propname) for propname in mxs.getPropNames( self._nativePointer ) ]
	
# register the symbol
import cross3d
cross3d.registerSymbol( 'SceneWrapper', StudiomaxSceneWrapper )
