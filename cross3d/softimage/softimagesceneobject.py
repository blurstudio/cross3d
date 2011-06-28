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
		return self.nativePointer().FindChild( name )

	def _nativeChildren(self):
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
	
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def name( self ):
		return self._nativePointer.FullName
	
	def displayName( self ):
		return self._nativePointer.Name
		
	# MH 06/13/11 moved functionality to correct place SoftimageSceneWrapper.setName. This method was missing self, so probubly didn't work
#	def setDisplayName( name ):
#		"""
#			\remarks	implements the AbstractSceneObject.setDisplayName to set the display name for this object
#			\sa			displayName, name, setName
#			\param		name	<str>
#			\return		<bool> success
#		"""
#		self.nativePointer().Name = name
	
	def isFrozen( self ):
		"""
			\remarks	returns whether or not this object is frozen(locked)
			\sa			freeze, setFrozen, unfreeze
			\return		<bool> frozen
		"""
		return not self._nativePointer.Properties('Visibility').Parameters('selectability').Value
	
	def isHidden( self ):
		"""
			\remarks	returns whether or not this object is hidden
			\sa			hide, setHidden, unhide
			\return		<bool> hidden
		"""
		return not self._nativePointer.Properties('Visibility').Parameters('viewvis').Value and not self._nativePointer.Properties('Visibility').Parameters('rendvis').Value

	def metadata( self ): #not in abstract
		from softimagesceneobjectmetadata import SoftimageSceneObjectMetadata
		return SoftimageSceneObjectMetadata( self )
	
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

