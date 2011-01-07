##
#	\namespace	blur3d.api.studiomax.studiomaxsceneobject
#
#	\remarks	The StudiomaxSceneObject class provides the implementation of the AbstractSceneObject class as it applies
#				to 3d Studio Max scenes
#	
#	\author		eric@blur.com
#	\author		Blur Studio
#	\date		03/15/10
#

from Py3dsMax import mxs
from blur3d.api.abstract.abstractsceneobject import AbstractSceneObject

class StudiomaxSceneObject( AbstractSceneObject ):
	AppDataAltMtlIndex		= 1108
	AppDataAltPropIndex 	= 1110
	
	def _findNativeChild( self, name, recursive = False, parent = None ):
		"""
			\remarks	implements the AbstractSceneObject._findNativeChild method to find 
						the child by the name and returns it
			\sa			findChild
			\param		name		<str>
			\param		recursive	<bool>
			\param		parent		<variant> nativeObject	(used for recursive searches when necessary)
			\return		<variant> nativeObject || None
		"""
		if ( not parent ):
			parent = self._nativePointer
		
		# loop through all the objects
		for child in parent.children:
			if ( child.name == name ):
				return child
			
			# if recursive, lookup child nodes
			if ( recursive ):
				found = self._findNativeChild( name, recursive = True, parent = child )
				if ( found ):
					return found
		
		return None
	
	def _nativeChildren( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeChildren method to look up the native children for this object
			\sa			children
			\return		<list> [ <variant> nativeObject, .. ]
		"""
		return self._nativePointer.children
	
	def _nativeLayer( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeLayer method to return the native application's layer that the object is on
			\sa			layer, setLayer, _setNativeLayer
			\return		<variant> nativeLayer || None
		"""
		return self._nativePointer.layer
	
	def _nativeMaterial( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeMaterial method to return the native material for this object
			\sa			material, setMaterial, _setNativeMaterial
			\return		<variant> nativeMaterial || None
		"""
		return self._nativePointer.material
	
	def _nativeModel( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeModel method to look up the native model for this object
			\sa			model, setModel, _setNativeModel
			\return		<variant> nativeObject || None
		"""
		fullname = self._nativePointer.name
		if ( '.' in fullname ):
			return mxs.getNodeByName( fullname.split('.')[0] )
		return None
	
	def _nativeParent( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeParent method to look up the native parent for this object
			\sa			parent, setParent, _setNativeParent
			\return		<variant> nativeObject || None
		"""
		return self._nativePointer.parent
	
	def _nativeWireColor( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeWireColor to return the color for the wireframe of this object in the scene
			\sa			setWireColor
			\return		<QColor>
		"""
		return self._nativePointer.wireColor
		
	def _setNativeLayer( self, nativeLayer ):
		"""
			\remarks	implements the AbstractSceneObject._setNativeLayer method to set the native layer for this object
			\sa			layer, setLayer, _nativeLayer
			\param		<variant> nativeLayer || None
			\return		<bool> success
		"""
		if ( not nativeLayer ):
			worldlayer = mxs.layerManager.getLayer(0)
			worldlayer.addNodes( [ self._nativePointer ] )
		else:
			nativeLayer.addNodes( [ self._nativePointer ] )
		
		return True
	
	def _setNativeMaterial( self, nativeMaterial ):
		"""
			\remarks	implements the AbstractSceneObject._setNativeMaterial method to set the native material for this object
			\sa			material, setMaterial, _nativeMaterial
			\param		<variant> nativeMaterial || None
			\return		<bool> success
		"""
		self._nativePointer.material = nativeMaterial
		return True
		
	def _setNativeModel( self, nativeModel ):
		"""
			\remarks	implements the AbstractSceneObject._setNativeModel method to set the native model for this object
			\sa			model, setModel, _nativeModel
			\param		<variant> nativeObject || None
			\return		<bool> success
		"""
		model = self._nativeModel()
		
		# don't process when we need to reset this model
		if ( nativeModel == model ):
			return True
		
		# otherwise, we need to reparent this node and reset its name
		obj 		= self._nativePointer
		obj.parent 	= nativeModel
		splt 		= obj.name.split( '.' )
		
		if ( nativeModel and len( splt ) == 2 ):
			obj.name = nativeModel.name + '.' + splt[1]
		elif ( nativeModel ):
			obj.name = nativeModel.name + '.' + obj.name
		elif ( splt == 2 ):
			obj.name = splt[1]
		
		return True
	
	def _setNativeParent( self, nativeParent ):
		"""
			\remarks	implements the AbstractSceneObject._setNativeParent method to set the native parent for this object
			\sa			parent, setParent, _nativeParent
			\param		<variant> nativeObject || None
			\return		<bool> success
		"""
		self._nativePointer.parent = nativeParent
		return True
	
	def _setNativeWireColor( self, color ):
		"""
			\remarks	implements the AbstractSceneObject._setNativeWireColor to sets the wirecolor for the object to the inputed QColor
			\sa			wireColor
			\param		color	<QColor>
			\return		<bool> success
		"""
		self._nativePointer.wireColor = color
		return True
		
	def _typeOfNativeObject( self, nativeObject ):
		"""
			\remarks	reimplements the AbstractSceneObject._typeOfNativeObject method to returns the ObjectType of the nativeObject applied
			\param		<variant> nativeObject || None
			\return		<bool> success
		"""
		from blur3d.constants import ObjectType
		
		isKindOf 	= mxs.isKindOf
		
		# check to see if the object is a geometry type
		if ( isKindOf( nativeObject, mxs.GeometryClass ) ):
			return ObjectType.Geometry
		
		# check to see if the object is a light type
		elif ( isKindOf( nativeObject, mxs.Light ) ):
			return ObjectType.Light
		
		# check to see if the object is a camera type
		elif ( isKindOf( nativeObject, mxs.Camera ) ):
			return ObjectType.Camera
			
		return AbstractSceneObject._typeOfNativeObject( self, nativeObject )
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	def displayName( self ):
		"""
			\remarks	implements the AbstractSceneObject.displayName method to look up the display name for this object and returns it
			\sa			objectName, setDisplayName, setObjectName
			\return		<str> name
		"""
		return self._nativePointer.name.split( '.' )[-1]
	
	def hasProperty( self, key ):
		"""
			\remarks	implements the AbstractSceneObject.hasProperty method to return whether or not the inputed key is a property of this object
			\sa			property, setProperty
			\param		key		<str>
			\return		<bool> found
		"""
		key = str(key)
		return mxs.isProperty( self._nativePointer, key ) or mxs.hasProperty( self._nativePointer, key )
	
	def isFrozen( self ):
		"""
			\remarks	implements the AbstractSceneObject.isFrozen to return whether or not this object is frozen(locked)
			\sa			freeze, setFrozen, unfreeze
			\return		<bool> frozen
		"""
		return self._nativePointer.isfrozen
		
	def isHidden( self ):
		"""
			\remarks	implements the AbstractSceneObject.isHidden to return whether or not this object is hidden
			\sa			hide, setHidden, unhide
			\return		<bool> hidden
		"""
		return self._nativePointer.ishiddeninvpt
		
	def isSelected( self ):
		"""
			\remarks	implements the AbstractSceneObject.isSelected to return whether or not this object is selected
			\sa			deselect, select, setSelected
			\return		<bool> selected
		"""
		return self._nativePointer.isselected
		
	def objectName( self ):
		"""
			\remarks	implements the AbstractSceneObject.objectName to look up the unique name for this object and returns it
			\sa			displayName, setDisplayName, setObjectName
			\return		<str> name
		"""
		return str(self._nativePointer.name)
		
	def property( self, key, default = None ):
		"""
			\remarks	implements the AbstractSceneObject.property to return the value for the property of this object, or the default value if not found
			\sa			hasProperty, setProperty
			\param		key			<str>
			\param		default		<variant>	default return value if not found
			\return		<variant>
		"""
		result = self._scene._fromNativeValue( mxs.getProperty( self._nativePointer, str(key) ) )
		if ( result == None ):
			return default
		return result
		
	def setDisplayName( self, name ):
		"""
			\remarks	implements the AbstractSceneObject.setDisplayName to set the display name for this object
			\sa			displayName, objectName, setObjectName
			\param		name	<str>
			\return		<bool> success
		"""
		splt 		= self._nativePointer.name.split( '.' )
		splt[-1] 	= name
		self._nativePointer.name = '.'.join( splt )
		return True
		
	def setFrozen( self, state ):
		"""
			\remarks	implements the AbstractSceneObject.setFrozen to freezes(locks)/unfreezes(unlocks) this object
			\sa			freeze, isFrozen, unfreeze
			\param		state	<bool>
			\return		<bool> success
		"""
		self._nativePointer.isfrozen = state
		return True
		
	def setHidden( self, state ):
		"""
			\remarks	implements the AbstractSceneObject.setHidden to hides/unhides this object
			\sa			hide, isHidden, unhide
			\param		state	<bool>
			\return		<bool> success
		"""
		self._nativePointer.ishidden = state
		return True
		
	def setObjectName( self, name ):
		"""
			\remarks	implements the AbstractSceneObject.setObjectName to set the full name for this object
			\sa			displayName, objectName, setDisplayName
			\param		name	<str>
			\return		<bool> success
		"""
		self._nativePointer.name = str(name)
		return True
		
	def setProperty( self, key, value ):
		"""
			\remarks	implements the AbstractSceneObject.setProperty to set the inputed object's property key to the given value
			\sa			hasProperty, property
			\param		key		<str>
			\param		value	<variant>
			\return		<bool> success
		"""
		mxs.setProperty( self._nativePointer, str(key), self._scene._toNativeValue(value) )
		return True
	
	def setSelected( self, state ):
		"""
			\remarks	implements the AbstractSceneObject.setSelected to selects/deselects this object
			\sa			deselect, isSelected, select
			\param		state	<bool>
			\return		<bool> success
		"""
		self._nativePointer.isselected = state
		return True

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneObject', StudiomaxSceneObject )