##
#	\namespace	blur3d.api.studiomax.studiomaxsceneobject
#
#	\remarks	The StudiomaxSceneModel class provides the implementation of the AbstractSceneModel class as it applies
#				to 3d Studio Max scenes
#	
#	\author		douglas@blur.com
#	\author		Blur Studio
#	\date		06/27/11
#

from blur3d.api.abstract.abstractscenemodel import AbstractSceneModel

#------------------------------------------------------------------------------------------------------------------------

class StudiomaxSceneModel( AbstractSceneModel ):
	pass

# register the symbol
from blur3d import api
api.registerSymbol( 'SceneModel', SoftimageSceneModel )

