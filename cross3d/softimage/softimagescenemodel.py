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
		
	#------------------------------------------------------------------------------------------------------------------------
	# 												public methods
	#------------------------------------------------------------------------------------------------------------------------

	def assetType( self ):
		metadata = self.metadata()
		return metadata.attribute( 'assetType' )
		
	def department( self ):
		metadata = self.metadata()
		return metadata.attribute( 'department' )
		
# register the symbol
from blur3d import api
api.registerSymbol( 'SceneModel', SoftimageSceneModel )

