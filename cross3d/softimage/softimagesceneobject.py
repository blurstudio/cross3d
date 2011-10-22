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
		return self.nativePointer().FindChild( name )

	def _nativeChildren(self):
		"""
			\remarks	implements the AbstractSceneObject._nativeChildren method to look up the native children for this object
			\sa			children
			\return		<list> [ <PySotimage.xsi.Object> nativeObject, .. ]
		"""
		return self._nativePointer.Children
	
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

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneObject', SoftimageSceneObject )

