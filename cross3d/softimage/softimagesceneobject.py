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

	def _nativeChildren():
		return self.nativePointer.Children
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------
	
	def name( self ):
		return self._nativePointer.FullName
	
	def displayName( self ):
		return self._nativePointer.Name
		
	def setDisplayName( name ):
		"""
			\remarks	implements the AbstractSceneObject.setDisplayName to set the display name for this object
			\sa			displayName, name, setName
			\param		name	<str>
			\return		<bool> success
		"""
		self.nativePointer().Name = name
		
	def metadata( self ): #not in abstract
		from softimagesceneobjectmetadata import SoftimageSceneObjectMetadata
		return SoftimageSceneObjectMetadata( self )

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneObject', SoftimageSceneObject )

