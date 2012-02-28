##
#	\namespace	blur3d.api.softimage.softimagesceneobject
#
#	\remarks	The SoftimageSceneObject class provides the implementation of the AbstractSceneObject class as it applies
#				to Softimage
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/04/11
#

from PySoftimage import xsi
from blur3d.constants import ObjectType
from blur3d.api.abstract.abstractsceneobject import AbstractSceneObject

#------------------------------------------------------------------------------------------------------------------------

class SoftimageSceneObject( AbstractSceneObject ):

	#------------------------------------------------------------------------------------------------------------------------
	# 												protected methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def _findNativeChild( self, name, recursive = False, parent = None ):
		"""
			\remarks	implements the AbstractSceneObject._findNativeChildren method to look up a specific native children for this object
			\return		<PySotimage.xsi.Object> nativeObject
		"""
		return self.nativePointer().FindChild( name, '', '', recursive )

	def _nativeChildren( self, recursive = False, parent = None, childrenCollector = [] ):
		"""
			\remarks	implements the AbstractSceneObject._nativeChildren method to look up the native children for this object
			\param		recursive <bool>
			\sa			children
			\return		<list> [ <PySotimage.xsi.Object> nativeObject, .. ]
		"""
		return [ obj for obj in self._nativePointer.FindChildren( '', '', '', recursive ) ]
	
	def _nativeParent( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeParent method to look up the native parent for this object
			\sa			parent, setParent, _setNativeParent
			\return		<Py3dsMax.mxs.Object> nativeObject || None
		"""
		return self._nativePointer.Parent
	
	def _setNativeParent( self, nativeParent ):
		"""
			\remarks	implements the AbstractSceneObject._setNativeParent method to set the native parent for this object
			\sa			parent, setParent, _nativeParent
			\param		<Py3dsMax.mxs.Object> nativeObject || None
			\return		<bool> success
		"""
		xsi.Application.ParentObj(self._nativePointer, nativeParent)
		return True
		
	def _nativeModel( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeModel method to look up the native model for this object
			\sa			children
			\return		<list> [ <PySotimage.xsi.Model> nativeObject, .. ]
		"""
		obj = self.nativePointer()
		ignoreSceneRoot = True
		if str( obj.Type ) == "#model":
			if ignoreSceneRoot is True and obj.Name == "Scene_Root": 
				model = None
			else:
				model = obj
		else:
			if ignoreSceneRoot is True and obj.Model.Name == "Scene_Root":
				model = None
			else:
				model = obj.Model
		return model
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def deleteProperty( self, propertyName ):
		"""
			\remarks	implements the AbstractSceneObject.deleteProperty that deletes a property of this object.
			\return		<bool> success
		"""
		xsi.DeleteObj( '.'.join( [ self.name(), propertyName ] ) )
		return True
	
	def uniqueId( self ):
		"""
			\remarks	implements the AbstractSceneObject.uniqueId to look up the unique name for this object and returns it
			\sa			displayName, setDisplayName, setName
			\return		<str> name
		"""
		return self._nativePointer.ObjectID
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												static methods
	#------------------------------------------------------------------------------------------------------------------------
	
	@staticmethod
	def _typeOfNativeObject( nativeObject ):
		"""
			\remarks	reimplements the AbstractSceneObject._typeOfNativeObject method to returns the ObjectType of the nativeObject applied
			\param		<PySoftimage.xsi.Object> nativeObject || None
			\return		<bool> success
		"""
		
		type 	= nativeObject.Type
		
		# check to see if the object is a geometry type
		if type == 'polymsh':
			return ObjectType.Geometry
		
		# check to see if the object is a light type
		if type == 'light':
			return ObjectType.Light
		
		# check to see if the object is a camera type
		if type == 'camera':
			return ObjectType.Camera
			
		# check to see if the object is a model type
		if type == '#model':
			return ObjectType.Model
			
		return AbstractSceneObject._typeOfNativeObject( nativeObject )

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneObject', SoftimageSceneObject )

