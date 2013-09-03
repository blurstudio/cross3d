##
#	\namespace	blur3d.api.softimage.softimagesceneobject
#
#	\remarks	The SoftimageSceneModel class provides the implementation of the AbstractSceneModel class as it applies
#				to Softimage scenes
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		04/04/11
#

from blur3d.api.abstract.abstractscenemodel import AbstractSceneModel

#------------------------------------------------------------------------------------------------------------------------

class SoftimageSceneModel( AbstractSceneModel ):
	def _setNativeParent( self, nativeParent ):
		"""
			\remarks	implements the AbstractSceneObject._setNativeParent method to set the native parent for this object
			\sa			parent, setParent, _nativeParent
			\param		<PySoftimage.xsi.Object> nativeObject || None
			\return		<bool> success
		"""
		xsi.Application.ParentObj(nativeParent, self._nativePointer)
		return True
	
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneModel', SoftimageSceneModel )

