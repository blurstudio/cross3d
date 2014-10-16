from blur3d import api
from blur3d.api.abstract.abstractscenemodel import AbstractSceneModel

#------------------------------------------------------------------------

class MayaSceneModel(AbstractSceneModel):
	pass
	
# register the symbol
api.registerSymbol('SceneModel', MayaSceneModel)