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

	def _nativeChildren( self, recursive = False, wildcard = '', type = '', parent = '', childrenCollector = [] ):
		"""
			\remarks	implements the AbstractSceneObject._nativeChildren method to look up the native children for this object
			\param		recursive <bool> wildcard <string> type <string parent <string> childrenCollector <list>
			\sa			children
			\return		<list> [ <PySoftimage.xsi.Object> nativeObject, .. ]
		"""
		nativeType = ''
		if type != '':
			nativeType = self._nativeTypeOfObjectType( type )
		#return [ obj for obj in self._nativePointer.FindChildren( name, nativeType, parent, recursive ) ]
		return self._nativePointer.FindChildren( wildcard, nativeType, '', recursive )
	
	def _nativeParent( self ):
		"""
			\remarks	implements the AbstractSceneObject._nativeParent method to look up the native parent for this object
			\sa			parent, setParent, _setNativeParent
			\return		<PySoftimage.xsi.Object> nativeObject || None
		"""
		return self._nativePointer.Parent
	
	def _setNativeParent( self, nativeParent ):
		"""
			\remarks	implements the AbstractSceneObject._setNativeParent method to set the native parent for this object
			\sa			parent, setParent, _nativeParent
			\param		<PySoftimage.xsi.Object> nativeObject || None
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
	def _nativeTypeOfObjectType( objectType ):
		"""
			\remarks	reimplements the AbstractSceneObject._nativeTypeOfObjectType method to return the nativeType of the ObjectType supplied
			\param		<blur3d.api.constants.ObjectType> objectType || None
			\return		<bool> success
		"""	
		if objectType == ObjectType.Geometry:
			return 'polymsh'
		elif objectType == ObjectType.Light:
			return 'light'
		elif objectType == ObjectType.Camera:
			return 'camera'
		elif objectType == ObjectType.Model:
			return '#model'
		else:
			return None
		return AbstractSceneObject._nativeTypeOfObjectType( objectType )
	
	@staticmethod
	def _typeOfNativeObject( nativeObject ):
		"""
			\remarks	reimplements the AbstractSceneObject._typeOfNativeObject method to returns the ObjectType of the nativeObject applied
			\param		<PySoftimage.xsi.Object> nativeObject || None
			\return		<bool> success
		"""
		
		type = nativeObject.Type
		
		# check to see if the object is a geometry type
		if type == 'polymsh':
			return ObjectType.Geometry
		
		# check to see if the object is a light type
		elif type == 'light':
			return ObjectType.Light
		
		# check to see if the object is a camera type
		elif type == 'camera':
			return ObjectType.Camera
			
		# check to see if the object is a model type
		elif type == '#model':
			return ObjectType.Model
			
		return AbstractSceneObject._typeOfNativeObject( nativeObject )

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneObject', SoftimageSceneObject )

